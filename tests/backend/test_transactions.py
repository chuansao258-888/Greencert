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
