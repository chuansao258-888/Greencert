# Test Results

## Current source recheck

The current source was rechecked on 18 October 2026 after the registration guard was added. The results below apply to the latest contract and application code in this repository.

| Check | Result |
|---|---|
| Backend unit tests | 18 passed, 0 failed |
| Frontend scripts | 7 passed, 0 failed |
| Contract source compilation | Passed with solc 0.8.30 |
| Solidity test-source compilation | Passed with solc 0.8.30 |
| Solidity test execution | 14 passed, 0 failed on a fresh Ganache Shanghai EVM |
| Current contract gas workflow | 16 transactions succeeded; final state checks passed |

The Solidity execution uses `scripts/run_contract_tests.cjs`. It deploys a fresh test contract for every test function. The selected tests include role registration, rejection of role changes, application submission, approval, withdrawal, rejection, listing, repricing, cancellation, purchase, seller withdrawal, retirement and rejection of unregistered submission and purchase.

The gas workflow uses `scripts/measure_current_gas.cjs`. It deploys the current RoleRegistry, CertificateRegistry and CertificateMarket source to a fresh local EVM. It then binds the market, registers Producer and Buyer accounts, completes the certificate lifecycle, checks application withdrawal and rejection, and validates the final stored states. Detailed values are in [gas-results.csv](../gas/gas-results.csv).

## Commands

```powershell
python -m unittest discover -s tests/backend -t .
npm run test:frontend
npm run compile
npm run test:contracts:compile

$env:NODE_PATH = (Resolve-Path tmp/evm-tools/node_modules).Path
node scripts/run_contract_tests.cjs
node scripts/measure_current_gas.cjs
```

## Public deployment checks

The public application returned HTTP 200 and `ready` from `/api/health`. `/api/config` returned Sepolia chain ID 11155111 and the three addresses in `deployment.json`. Read-only calls against the deployed Registry and Market rejected an unregistered application submission and purchase with `Register a role first`.

The public service uses SQLite and uploaded files on the free Render filesystem. Those local files can be lost after a restart or redeployment. The blockchain records remain on Sepolia, but missing supporting files can make an audit record incomplete.

## Scope

The automated results cover selected paths and failure cases. The gas measurements are local EVM receipts from the current source. They are not Sepolia transaction hashes or a performance benchmark. The public checks confirm service availability, configured addresses and selected read-only guard behaviour.
