from __future__ import annotations

import json
from pathlib import Path

from web3 import HTTPProvider, Web3


ROLE_NAMES = ("None", "Producer", "Buyer", "Admin")
APPLICATION_STATUSES = ("None", "Pending", "Approved", "Rejected", "Withdrawn")
CERTIFICATE_STATUSES = ("None", "Active", "Retired")


class ChainService:
    # Load the deployment and optional read-only RPC connection.
    def __init__(self, config: dict) -> None:
        self.config = config
        self.deployment = self._load_deployment(Path(config["DEPLOYMENT_FILE"]))
        self.web3 = Web3(HTTPProvider(config["RPC_URL"])) if config["RPC_URL"] else None

    # Read deployed addresses from the local configuration file.
    @staticmethod
    def _load_deployment(path: Path) -> dict:
        if not path.exists():
            return {"contracts": {}, "deploymentBlocks": {}}
        return json.loads(path.read_text(encoding="utf-8"))

    # Return the address of a named contract.
    def contract_address(self, name: str) -> str:
        return self.deployment.get("contracts", {}).get(name, "")

    # Report whether all contract reads are available.
    def configured(self) -> bool:
        return bool(self.web3 and all(self.contract_address(name) for name in ("roleRegistry", "certificateRegistry", "certificateMarket")))

    # Bind a deployed contract to its browser ABI.
    def contract(self, name: str):
        if not self.configured():
            raise RuntimeError("Contracts are not configured")
        artifact_name = {"roleRegistry": "RoleRegistry", "certificateRegistry": "CertificateRegistry", "certificateMarket": "CertificateMarket"}[name]
        abi_path = Path(__file__).resolve().parents[1] / "static" / "contracts" / f"{artifact_name}.json"
        abi = json.loads(abi_path.read_text(encoding="utf-8"))
        return self.web3.eth.contract(address=Web3.to_checksum_address(self.contract_address(name)), abi=abi)

    # Resolve a wallet's registered role.
    def role_name(self, address: str) -> str:
        if not self.configured():
            return "None"
        role = self.contract("roleRegistry").functions.roleOf(Web3.to_checksum_address(address)).call()
        return ROLE_NAMES[role]

    # Fetch all applications for the small coursework dataset.
    def applications(self) -> list[dict]:
        registry = self.contract("certificateRegistry")
        return [self._application(registry.functions.getApplication(index).call()) for index in range(1, registry.functions.applicationCount().call() + 1)]

    # Fetch certificates with their current listing state.
    def certificates(self) -> list[dict]:
        registry = self.contract("certificateRegistry")
        market = self.contract("certificateMarket")
        return [
            self._certificate(registry.functions.getCertificate(index).call(), market.functions.getListing(index).call())
            for index in range(1, registry.functions.certificateCount().call() + 1)
        ]

    # Convert an application tuple into API data.
    @staticmethod
    def _application(value: tuple) -> dict:
        return {
            "id": str(value[0]), "producer": value[1], "batchKey": "0x" + value[2].hex(), "siteHash": "0x" + value[3].hex(),
            "periodStart": str(value[4]), "periodEnd": str(value[5]), "batchIndex": str(value[6]),
            "quantity": str(value[7]), "metadataHash": "0x" + value[8].hex(), "status": APPLICATION_STATUSES[value[9]],
            "certificateId": str(value[10]), "rejectionHash": "0x" + value[11].hex(),
        }

    # Convert a certificate and listing tuple into API data.
    @staticmethod
    def _certificate(value: tuple, listing: tuple) -> dict:
        return {
            "id": str(value[0]), "applicationId": str(value[1]), "producer": value[2], "owner": value[3],
            "quantity": str(value[4]), "metadataHash": "0x" + value[5].hex(), "status": CERTIFICATE_STATUSES[value[6]],
            "listed": value[7], "issuedAt": str(value[8]), "retiredAt": str(value[9]),
            "retirementHash": "0x" + value[10].hex(),
            "listing": {"seller": listing[1], "totalPriceWei": str(listing[2]), "active": listing[3]},
        }

    # Fetch a transaction and its receipt when mined.
    def transaction(self, tx_hash: str) -> tuple[dict, dict | None]:
        if not self.web3:
            raise RuntimeError("RPC is not configured")
        transaction = dict(self.web3.eth.get_transaction(tx_hash))
        try:
            receipt = dict(self.web3.eth.get_transaction_receipt(tx_hash))
        except Exception:
            receipt = None
        return transaction, receipt
