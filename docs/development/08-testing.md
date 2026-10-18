# Testing Plan

Testing concentrates on the open-wallet workflow, Admin review and the core accounting rules. Python `unittest` covers server behavior with temporary SQLite and upload folders. Solidity test functions target Remix Solidity Unit Testing, the tool used for contract exercises. Sepolia workflow verification is recorded manually because it requires real wallet signatures.

## Automated checks

| Files | Main behavior |
|---|---|
| `tests/contracts/RoleRegistry_test.sol` | Producer and Buyer registration; an assigned role cannot change. |
| `tests/contracts/CertificateRegistry_test.sol` | Multi-unit application, withdrawal, rejection, approval and unchanged certificate quantity. |
| `tests/contracts/CertificateMarket_test.sol` | Whole-batch listing, repricing, cancellation, exact-price purchase, seller withdrawal and Buyer retirement. |
| `tests/contracts/TestActors.sol` | Separate Producer and Buyer callers for the contract tests. |
| `tests/backend/test_auth.py` | Signed challenge, session creation and nonce reuse. |
| `tests/backend/test_content.py` | Canonical hash, 25-unit batch and API content creation. |
| `tests/backend/test_files.py` | Supported evidence types, upload and download. |
| `tests/backend/test_records.py` | Page rendering, certificate reads, dashboard totals and chart breakdown, and event endpoint. |
| `tests/backend/test_transactions.py` | Confirmed transaction decoding and saved activity. |
| `tests/frontend/dashboard.test.cjs` | Labeled chart values, Unknown source and no-certificate empty state. |
| `tests/frontend/wallet_session.test.cjs` | Restored wallet sessions, changed accounts and wrong-chain session rejection. |
| `tests/frontend/wallet_mobile.test.cjs` | MetaMask mobile deep link preserves the current route, query string and fragment. |
| `tests/frontend/transaction_state.test.cjs` | Submission hash recording, receipt/event verification stages and pending-timeout guidance. |

Run the Python suite from the repository root:

```powershell
python -m unittest discover -s . -p "test_*.py" -v
```

Compile application contracts and Solidity test sources:

```powershell
npm ci
npm run compile
npm run test:contracts:compile
python scripts/export_abi.py
npm run test:frontend
```

`test:contracts:compile` checks Solidity syntax and imports using a local compilation stub for Remix's `Assert` library. It does not execute the test functions. Run the files in `tests/contracts` through Remix Solidity Unit Testing for execution results. Each test emits a Remix assertion event; a result of `Passed: 0, Failed: 0` means no test was counted. The payable market tests use Remix's `#value` directive to supply 100 wei to the test function. Record the observed pass/fail results in `docs/evidence/test-results.md`.

## Manual acceptance

`tests/manual/sepolia-checklist.md` covers deployment, role registration, submission, withdrawal, rejection, approval, listing, repricing, cancellation, purchase, seller withdrawal and retirement. Use separate wallets for the three roles. Record transaction hash, receipt status, gas used and effective gas price for each successful write in `docs/evidence/gas-results.csv`. Calculate cost as `gasUsed × effectiveGasPrice`.

Do not mark a manual step or Solidity test as passed before it has been run. The empty deployment addresses and gas CSV are deliberate placeholders until Sepolia deployment.
