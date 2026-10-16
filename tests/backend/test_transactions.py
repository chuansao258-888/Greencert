from unittest.mock import Mock

from tests.backend.base import AppTestCase


class TransactionTests(AppTestCase):
    # Decode and save a confirmed role-registration receipt.
    def test_confirmed_transaction_verification(self) -> None:
        address, csrf = self.sign_in()
        chain = self.app.extensions["chain"]
        target = "0x" + "1" * 40
        tx_hash = "0x" + "a" * 64
        chain.configured = lambda: True
        chain.contract_address = lambda name: target if name == "roleRegistry" else "0x" + "2" * 40
        chain.transaction = lambda hash_value: (
            {"from": address, "to": target, "input": "0x1234", "value": 0},
            {"status": 1, "gasUsed": 45000, "blockNumber": 5, "blockHash": bytes.fromhex("b" * 64), "logs": [{"address": target}]},
        )
        function = Mock(fn_name="register")
        contract = Mock()
        contract.decode_function_input.return_value = (function, {"requestedRole": 1})
        chain.contract = lambda name: contract
        response = self.client.post("/api/transactions/verify", json={"txHash": tx_hash}, headers={"X-CSRF-Token": csrf})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["status"], "confirmed")
        self.assertEqual(len(self.client.get("/api/transactions").json["data"]), 1)

    # Accept a successful GreenCert call wrapped by a wallet smart-account contract.
    def test_wrapped_transaction_verification_uses_emitted_business_event(self) -> None:
        address, csrf = self.sign_in()
        chain = self.app.extensions["chain"]
        role_target = "0x" + "1" * 40
        registry_target = "0x" + "2" * 40
        market_target = "0x" + "3" * 40
        wrapper_target = "0x" + "4" * 40
        tx_hash = "0x" + "c" * 64
        chain.configured = lambda: True
        chain.contract_address = lambda name: {
            "roleRegistry": role_target, "certificateRegistry": registry_target, "certificateMarket": market_target,
        }[name]
        chain.transaction = lambda hash_value: (
            {"from": address, "to": wrapper_target, "input": "0x1234", "value": 0},
            {"status": 1, "gasUsed": 51000, "blockNumber": 6, "blockHash": bytes.fromhex("d" * 64), "logs": [{"address": registry_target}]},
        )

        class Event:
            def __init__(self, name):
                self.name = name

            def process_log(self, log):
                if self.name != "CertificateIssued":
                    raise ValueError("Not this event")
                return {"args": {"certificateId": 7, "applicationId": 4, "producer": address, "quantity": 5, "metadataHash": bytes(32)}}

        class Events:
            def __getattr__(self, name):
                return lambda: Event(name)

        class Contract:
            def __init__(self, contract_address):
                self.address = contract_address
                self.events = Events()

        chain.contract = lambda name: Contract(chain.contract_address(name))
        response = self.client.post("/api/transactions/verify", json={"txHash": tx_hash}, headers={"X-CSRF-Token": csrf})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["method"], "approveApplication")
        saved = self.client.get("/api/transactions").json["data"][0]
        self.assertEqual(saved["target"], registry_target)
        self.assertEqual(saved["entity_type"], "application")
        self.assertEqual(saved["entity_id"], "4")
