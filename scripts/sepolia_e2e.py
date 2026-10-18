"""Resume-safe Sepolia contract workflow with receipt and state checks after each write."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import time
from pathlib import Path

from dotenv import dotenv_values
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import HTTPProvider, Web3
from web3.logs import DISCARD


ROOT = Path(__file__).resolve().parents[1]
KEY_FILE = ROOT / ".sepolia-test.env"
STATE_FILE = ROOT / "instance" / "sepolia-e2e-state.json"
GAS_CSV = ROOT / "submission" / "gas" / "sepolia-gas-results.csv"
CHAIN_ID = 11155111
CERTIFICATE_ID = 1
INITIAL_PRICE = 100_000_000_000_000
UPDATED_PRICE = 200_000_000_000_000
EXPECTED_METADATA_HASH = "0x342077c31f9f344e8de5c7946e71f3faafa877d5729775576a0b000dc9ac7b93"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def same_address(left: str, right: str) -> bool:
    return left.lower() == right.lower()


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temporary.replace(STATE_FILE)


class SepoliaWorkflow:
    def __init__(self, signing: bool) -> None:
        settings = dotenv_values(KEY_FILE) if KEY_FILE.exists() else {}
        deployment = json.loads((ROOT / "deployment.json").read_text(encoding="utf-8"))
        require(deployment["chainId"] == CHAIN_ID, "Deployment is not Sepolia.")
        self.addresses = {name: Web3.to_checksum_address(value) for name, value in deployment["contracts"].items()}
        rpc_url = settings.get("SEPOLIA_RPC_URL") or "https://ethereum-sepolia-rpc.publicnode.com"
        self.web3 = Web3(HTTPProvider(rpc_url, request_kwargs={"timeout": 30}))
        require(self.web3.is_connected(), "Sepolia RPC is unavailable.")
        require(self.web3.eth.chain_id == CHAIN_ID, "RPC is not Sepolia.")
        self.contracts = {}
        for name, artifact in (("roleRegistry", "RoleRegistry"), ("certificateRegistry", "CertificateRegistry"), ("certificateMarket", "CertificateMarket")):
            abi = json.loads((ROOT / "static" / "contracts" / f"{artifact}.json").read_text(encoding="utf-8"))
            self.contracts[name] = self.web3.eth.contract(address=self.addresses[name], abi=abi)
            require(bool(self.web3.eth.get_code(self.addresses[name])), f"{artifact} has no code.")
        self.roles = self.contracts["roleRegistry"]
        self.registry = self.contracts["certificateRegistry"]
        self.market = self.contracts["certificateMarket"]
        self.wallets = {}
        if signing:
            require(KEY_FILE.exists(), f"Create {KEY_FILE.name} from its example first.")
            for label in ("ADMIN", "PRODUCER", "BUYER"):
                key = settings.get(f"SEPOLIA_{label}_PRIVATE_KEY")
                expected = settings.get(f"SEPOLIA_{label}_ADDRESS")
                require(bool(key and expected), f"Set {label} address and private key in {KEY_FILE.name}.")
                wallet = Account.from_key(key)
                require(same_address(wallet.address, expected), f"{label} private key does not match its configured address.")
                self.wallets[label.lower()] = wallet
            self.max_gas_price = Web3.to_wei(settings.get("SEPOLIA_MAX_GAS_PRICE_GWEI") or "5", "gwei")
            self.max_transaction_cost = Web3.to_wei(settings.get("SEPOLIA_MAX_TRANSACTION_COST_ETH") or "0.01", "ether")
        self.state = json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else None

    def bindings(self) -> None:
        require(same_address(self.registry.functions.roleRegistry().call(), self.addresses["roleRegistry"]), "Registry role binding is wrong.")
        require(same_address(self.registry.functions.market().call(), self.addresses["certificateMarket"]), "Registry market binding is wrong.")
        require(same_address(self.market.functions.roleRegistry().call(), self.addresses["roleRegistry"]), "Market role binding is wrong.")
        require(same_address(self.market.functions.certificateRegistry().call(), self.addresses["certificateRegistry"]), "Market certificate binding is wrong.")

    def snapshot(self) -> None:
        self.bindings()
        certificate = self.registry.functions.getCertificate(CERTIFICATE_ID).call()
        listing = self.market.functions.getListing(CERTIFICATE_ID).call()
        print(f"Sepolia block: {self.web3.eth.block_number}")
        print(f"Certificate #{CERTIFICATE_ID}: owner={certificate[3]}, quantity={certificate[4]}, status={certificate[6]}, listed={certificate[7]}")
        print(f"Listing: seller={listing[1]}, totalPriceWei={listing[2]}, active={listing[3]}")
        print(f"Applications={self.registry.functions.applicationCount().call()}, sales={self.market.functions.soldCount().call()}")
        if self.state:
            print("Verified steps:", ", ".join(name for name, result in self.state["steps"].items() if result.get("verified")) or "none")

    def new_state(self) -> None:
        if self.state:
            require(self.state["chainId"] == CHAIN_ID and self.state["contracts"] == self.addresses, "Saved run targets a different deployment.")
            require(self.state["wallets"] == {name: wallet.address for name, wallet in self.wallets.items()}, "Saved run uses different wallets.")
            return
        self.bindings()
        admin = self.wallets["admin"].address
        producer = self.wallets["producer"].address
        buyer = self.wallets["buyer"].address
        require(same_address(self.roles.functions.admin().call(), admin), "Admin account does not match the contract.")
        require(self.roles.functions.roleOf(producer).call() == 1, "Producer role is missing.")
        require(self.roles.functions.roleOf(buyer).call() == 2, "Buyer role is missing.")
        certificate = self.registry.functions.getCertificate(CERTIFICATE_ID).call()
        listing = self.market.functions.getListing(CERTIFICATE_ID).call()
        require(certificate[4] == 5 and certificate[6] == 1 and certificate[7], "Certificate #1 is not the expected active five-unit batch.")
        require(same_address(certificate[3], producer) and certificate[5].hex() == EXPECTED_METADATA_HASH[2:], "Certificate #1 owner or metadata differs.")
        require(listing[3] and same_address(listing[1], producer) and listing[2] == INITIAL_PRICE, "Certificate #1 is not listed at the expected starting price.")
        require(self.market.functions.soldCount().call() == 0 and self.market.functions.totalCredits().call() == 0, "Market already has sales or pending credits.")
        run_id = Web3.keccak(text=f"SC6113 Sepolia E2E {time.time_ns()}").hex()
        self.state = {
            "chainId": CHAIN_ID,
            "contracts": self.addresses,
            "wallets": {name: wallet.address for name, wallet in self.wallets.items()},
            "runId": run_id,
            "startingApplicationCount": self.registry.functions.applicationCount().call(),
            "steps": {},
        }
        save_state(self.state)

    def application(self, kind: str, index: int, quantity: int) -> tuple:
        run_id = self.state["runId"]
        site_hash = Web3.keccak(text=f"SC6113-{kind}-site-{run_id}")
        metadata_hash = Web3.keccak(text=f"SC6113-{kind}-metadata-{run_id}")
        now = int(time.time())
        return site_hash, now - 172_800, now - 86_400, index, quantity, metadata_hash

    def send_step(self, name: str, actor: str, contract, function, event: str, event_args: dict, before, after, value: int = 0) -> None:
        existing = self.state["steps"].get(name)
        if existing and existing.get("verified"):
            return
        wallet = self.wallets[actor]
        if not existing:
            before()
            gas_price = self.web3.eth.gas_price
            require(gas_price <= self.max_gas_price, f"{name}: gas price exceeds configured cap.")
            call_options = {"from": wallet.address, "value": value}
            function.call(call_options)
            estimated = function.estimate_gas(call_options)
            gas_limit = max(int(estimated * 1.3) + 50_000, estimated + 100_000)
            require(gas_limit <= 2_500_000, f"{name}: gas estimate is unexpectedly high.")
            require(gas_limit * gas_price + value <= self.max_transaction_cost, f"{name}: transaction exceeds cost cap.")
            require(self.web3.eth.get_balance(wallet.address) >= gas_limit * gas_price + value, f"{name}: {actor} lacks Sepolia ETH.")
            tx = function.build_transaction({
                "from": wallet.address, "chainId": CHAIN_ID,
                "nonce": self.web3.eth.get_transaction_count(wallet.address, "pending"),
                "gas": gas_limit, "gasPrice": gas_price, "value": value,
            })
            signed = Account.sign_transaction(tx, wallet.key)
            tx_hash = "0x" + signed.hash.hex().removeprefix("0x")
            self.state["steps"][name] = {"txHash": tx_hash, "actor": actor, "target": contract.address}
            save_state(self.state)
            print(f"{name}: broadcasting {tx_hash}", flush=True)
            self.web3.eth.send_raw_transaction(signed.raw_transaction)
        else:
            tx_hash = existing["txHash"]
            print(f"{name}: resuming {tx_hash}", flush=True)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=240)
        transaction = self.web3.eth.get_transaction(tx_hash)
        require(receipt.status == 1, f"{name}: transaction reverted: {tx_hash}")
        require(same_address(transaction["from"], wallet.address) and same_address(transaction["to"], contract.address), f"{name}: wrong sender or target.")
        matches = getattr(contract.events, event)().process_receipt(receipt, errors=DISCARD)
        require(any(all(log["args"].get(key) == expected for key, expected in event_args.items()) for log in matches), f"{name}: expected event is missing.")
        after()
        self.record_gas(name, receipt)
        self.state["steps"][name].update({"verified": True, "block": receipt.blockNumber, "gasUsed": receipt.gasUsed})
        save_state(self.state)
        print(f"{name}: PASS, block {receipt.blockNumber}, gas {receipt.gasUsed}", flush=True)

    @staticmethod
    def record_gas(name: str, receipt) -> None:
        tx_hash = "0x" + receipt.transactionHash.hex().removeprefix("0x")
        if tx_hash[2:].lower() in GAS_CSV.read_text(encoding="utf-8").lower():
            return
        price = receipt.effectiveGasPrice
        line = f"e2e_{name},{tx_hash},{receipt.blockNumber},{receipt.gasUsed},{price},{receipt.gasUsed * price},success\n"
        with GAS_CSV.open("a", encoding="utf-8") as file:
            file.write(line)

    def run(self) -> None:
        self.new_state()
        producer = self.wallets["producer"].address
        buyer = self.wallets["buyer"].address
        certificate = lambda: self.registry.functions.getCertificate(CERTIFICATE_ID).call()
        listing = lambda: self.market.functions.getListing(CERTIFICATE_ID).call()
        check = lambda condition, message: require(condition, message)

        self.send_step("reprice", "producer", self.market, self.market.functions.updatePrice(CERTIFICATE_ID, UPDATED_PRICE), "ListingPriceUpdated", {"certificateId": CERTIFICATE_ID, "newTotalPriceWei": UPDATED_PRICE},
                       lambda: check(listing()[3] and listing()[2] == INITIAL_PRICE, "Unexpected listing before repricing."),
                       lambda: check(listing()[3] and listing()[2] == UPDATED_PRICE, "Repricing state mismatch."))
        self.send_step("cancel", "producer", self.market, self.market.functions.cancelListing(CERTIFICATE_ID), "ListingCancelled", {"certificateId": CERTIFICATE_ID},
                       lambda: check(listing()[3] and certificate()[7], "Listing is not active before cancellation."),
                       lambda: check(not listing()[3] and not certificate()[7] and same_address(certificate()[3], producer), "Cancellation state mismatch."))
        self.send_step("relist", "producer", self.market, self.market.functions.listCertificate(CERTIFICATE_ID, INITIAL_PRICE), "CertificateListed", {"certificateId": CERTIFICATE_ID, "totalPriceWei": INITIAL_PRICE},
                       lambda: check(not listing()[3] and not certificate()[7], "Certificate is still listed before relisting."),
                       lambda: check(listing()[3] and listing()[2] == INITIAL_PRICE and certificate()[7], "Relisting state mismatch."))
        self.send_step("buy", "buyer", self.market, self.market.functions.buyCertificate(CERTIFICATE_ID, INITIAL_PRICE), "CertificatePurchased", {"certificateId": CERTIFICATE_ID, "buyer": buyer, "quantity": 5, "totalPriceWei": INITIAL_PRICE},
                       lambda: check(listing()[3] and listing()[2] == INITIAL_PRICE and same_address(certificate()[3], producer), "Purchase precondition failed."),
                       lambda: check(not listing()[3] and same_address(certificate()[3], buyer) and certificate()[4] == 5 and not certificate()[7] and self.market.functions.credits(producer).call() == INITIAL_PRICE and self.market.functions.totalSalesWei().call() == INITIAL_PRICE and self.market.functions.soldCount().call() == 1, "Purchase state mismatch."), value=INITIAL_PRICE)
        self.send_step("withdraw_proceeds", "producer", self.market, self.market.functions.withdraw(), "Withdrawal", {"seller": producer, "amountWei": INITIAL_PRICE},
                       lambda: check(self.market.functions.credits(producer).call() == INITIAL_PRICE, "Seller credit does not match sale price."),
                       lambda: check(self.market.functions.credits(producer).call() == 0 and self.market.functions.totalCredits().call() == 0 and self.web3.eth.get_balance(self.market.address) == 0, "Withdrawal state mismatch."))

        retirement_hash = Web3.keccak(text=f"SC6113-e2e-retirement-{self.state['runId']}")
        self.send_step("retire", "buyer", self.registry, self.registry.functions.retireCertificate(CERTIFICATE_ID, retirement_hash), "CertificateRetired", {"certificateId": CERTIFICATE_ID, "owner": buyer, "retirementHash": retirement_hash},
                       lambda: check(same_address(certificate()[3], buyer) and certificate()[6] == 1 and not certificate()[7], "Certificate cannot be retired yet."),
                       lambda: check(certificate()[6] == 2 and certificate()[4] == 5 and certificate()[10] == retirement_hash and certificate()[9] > 0, "Retirement state mismatch."))

        first_id = self.state["startingApplicationCount"] + 1
        second_id = first_id + 1
        first = self.application("withdraw", 2, 2)
        second = self.application("reject", 3, 3)
        application = lambda identifier: self.registry.functions.getApplication(identifier).call()
        self.send_step("submit_for_withdrawal", "producer", self.registry, self.registry.functions.submitApplication(*first), "ApplicationSubmitted", {"applicationId": first_id, "producer": producer, "quantity": 2},
                       lambda: check(self.registry.functions.applicationCount().call() == first_id - 1, "Application count changed before first submission."),
                       lambda: check(self.registry.functions.applicationCount().call() == first_id and application(first_id)[9] == 1 and application(first_id)[8] == first[5], "First application state mismatch."))
        self.send_step("withdraw_application", "producer", self.registry, self.registry.functions.withdrawApplication(first_id), "ApplicationWithdrawn", {"applicationId": first_id, "producer": producer},
                       lambda: check(application(first_id)[9] == 1, "First application is not pending."),
                       lambda: check(application(first_id)[9] == 4, "First application was not withdrawn."))
        self.send_step("submit_for_rejection", "producer", self.registry, self.registry.functions.submitApplication(*second), "ApplicationSubmitted", {"applicationId": second_id, "producer": producer, "quantity": 3},
                       lambda: check(self.registry.functions.applicationCount().call() == second_id - 1, "Application count changed before second submission."),
                       lambda: check(self.registry.functions.applicationCount().call() == second_id and application(second_id)[9] == 1 and application(second_id)[8] == second[5], "Second application state mismatch."))
        reason_hash = Web3.keccak(text=f"SC6113-e2e-rejection-{self.state['runId']}")
        self.send_step("reject_application", "admin", self.registry, self.registry.functions.rejectApplication(second_id, reason_hash), "ApplicationRejected", {"applicationId": second_id, "reasonHash": reason_hash},
                       lambda: check(application(second_id)[9] == 1, "Second application is not pending."),
                       lambda: check(application(second_id)[9] == 3 and application(second_id)[11] == reason_hash, "Second application was not rejected."))
        self.verify_evidence()
        self.verify_fresh_app()
        print("All Sepolia transaction and state checks passed.")

    def verify_evidence(self) -> None:
        database = ROOT / "instance" / "greencert.db"
        require(database.exists(), "Local application database is missing.")
        connection = sqlite3.connect(database)
        try:
            row = connection.execute(
                "SELECT c.canonical_json, f.stored_name, f.sha256 FROM contents c "
                "JOIN content_files cf ON cf.content_hash = c.content_hash "
                "JOIN files f ON f.id = cf.file_id WHERE c.content_hash = ?",
                (EXPECTED_METADATA_HASH,),
            ).fetchone()
        finally:
            connection.close()
        require(row is not None, "Approved certificate metadata or evidence is missing locally.")
        require(Web3.keccak(text=row[0]).hex() == EXPECTED_METADATA_HASH[2:], "Saved metadata hash does not match the chain.")
        evidence = ROOT / "instance" / "uploads" / row[1]
        require(evidence.exists() and hashlib.sha256(evidence.read_bytes()).hexdigest() == row[2], "Saved evidence file failed SHA-256 check.")
        print("Approved certificate metadata and evidence: PASS")

    def verify_fresh_app(self) -> None:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from app import create_app

        client = create_app().test_client()
        wallet = self.wallets["admin"]
        response = client.post("/api/auth/challenge", json={"address": wallet.address})
        require(response.status_code == 200, "Fresh app did not issue an Admin challenge.")
        challenge = response.json["data"]
        signature = Account.sign_message(encode_defunct(text=challenge["message"]), wallet.key).signature.hex()
        response = client.post("/api/auth/verify", json={"address": wallet.address, "nonce": challenge["nonce"], "signature": signature})
        require(response.status_code == 200, "Fresh app did not authenticate Admin.")
        response = client.get(f"/api/certificates/{CERTIFICATE_ID}")
        require(response.status_code == 200, "Fresh app could not read the certificate.")
        certificate = response.json["data"]
        require(certificate["status"] == "Retired" and certificate["quantity"] == "5" and not certificate["listed"], "Fresh app certificate state differs from chain.")
        require(same_address(certificate["owner"], self.wallets["buyer"].address), "Fresh app certificate owner differs from chain.")
        response = client.get("/api/applications/1")
        require(response.status_code == 200, "Fresh app could not read the approved application.")
        application = response.json["data"]
        require(application["metadataHash"].lower() == EXPECTED_METADATA_HASH and application["evidenceFileId"], "Fresh app could not find the approved evidence.")
        response = client.get(f"/api/files/{application['evidenceFileId']}")
        require(response.status_code == 200, "Fresh app denied the Admin evidence download.")
        require(hashlib.sha256(response.data).hexdigest() == application["metadata"]["proofSha256"], "Downloaded evidence failed SHA-256 check.")
        print("Fresh Flask instance: certificate state, Admin access and evidence download PASS")

    def preflight(self) -> None:
        self.bindings()
        for name, expected_role in (("producer", 1), ("buyer", 2)):
            wallet = self.wallets[name]
            require(self.roles.functions.roleOf(wallet.address).call() == expected_role, f"{name} role is missing.")
        require(same_address(self.roles.functions.admin().call(), self.wallets["admin"].address), "Admin address does not match.")
        gas_price = self.web3.eth.gas_price
        require(gas_price <= self.max_gas_price, "Gas price exceeds configured cap.")
        print(f"Gas price: {Web3.from_wei(gas_price, 'gwei')} gwei (cap {Web3.from_wei(self.max_gas_price, 'gwei')})")
        for name, wallet in self.wallets.items():
            print(f"{name}: {wallet.address}, balance {Web3.from_wei(self.web3.eth.get_balance(wallet.address), 'ether')} SepoliaETH")
        if not self.state:
            certificate = self.registry.functions.getCertificate(CERTIFICATE_ID).call()
            listing = self.market.functions.getListing(CERTIFICATE_ID).call()
            require(certificate[6] == 1 and certificate[7] and same_address(certificate[3], self.wallets["producer"].address), "Certificate is not ready for repricing.")
            require(listing[3] and listing[2] == INITIAL_PRICE, "Listing is not at the expected initial price.")
            function = self.market.functions.updatePrice(CERTIFICATE_ID, UPDATED_PRICE)
            options = {"from": self.wallets["producer"].address}
            function.call(options)
            print(f"First step (reprice) simulated successfully; estimated gas {function.estimate_gas(options)}")
        else:
            require(self.state["wallets"] == {name: wallet.address for name, wallet in self.wallets.items()}, "Saved run uses different wallets.")
            print("Saved run found; the next unverified step will resume.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "preflight", "run"), help="check reads state; preflight validates signers without writes; run sends remaining transactions")
    args = parser.parse_args()
    try:
        workflow = SepoliaWorkflow(signing=args.mode != "check")
        if args.mode == "check":
            workflow.snapshot()
        elif args.mode == "preflight":
            workflow.preflight()
        else:
            workflow.run()
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
