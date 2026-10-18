# Gas Estimation and Optimization Analysis

## Measurement scope

The measurements in [gas-results.csv](gas-results.csv) were produced from the current guarded contract source on 18 October 2026. The script deployed fresh contracts to an isolated Ganache Shanghai EVM, used solc 0.8.30 with optimizer setting 200, sent 16 state-changing transactions and checked the final contract state. All 16 receipts had status 1.

These values measure EVM gas for the current implementation. They are suitable for comparing transaction paths in this project. They are not Sepolia transaction hashes, network fees or a production cost forecast.

## Estimation before signing

The Sepolia workflow runner performs a read-only preflight and calls `estimate_gas` before broadcasting. It creates a buffered limit using:

```text
max(estimatedGas × 1.3 + 50,000, estimatedGas + 100,000)
```

The runner also checks its configured cap and the wallet balance. The website lets MetaMask prepare transactions and display fee settings. An estimate is preparation information. The final receipt records actual gas used.

## Current contract measurements

One measured call for each of the eleven business transaction types is shown below.

| Transaction | Gas used |
|---|---:|
| Register role | 45,508 |
| Submit application | 236,619 |
| Withdraw application | 38,120 |
| Approve application | 221,735 |
| Reject application | 56,682 |
| List certificate | 133,206 |
| Update listing price | 38,680 |
| Cancel listing | 46,436 |
| Buy whole batch | 143,062 |
| Withdraw seller proceeds | 54,328 |
| Retire certificate | 61,536 |
| **Total** | **1,075,912** |

The full CSV also contains market binding, both role registrations, relisting and the additional applications used for withdrawal and rejection checks. Those 16 transactions used 1,688,193 gas in total.

Application submission and approval use more gas because they create several stored values. Purchase updates the listing, certificate owner and seller credit in one transaction. Price update and application withdrawal change fewer storage fields. A first listing and a relisting can use different gas because their storage conditions differ.

## Optimization choices

| Choice | Effect and trade-off |
|---|---|
| Optimizer enabled with 200 runs | Reduces repeated execution cost while accepting a larger deployment bytecode trade-off. |
| Compact timestamp and quantity fields | `uint64` and `uint32` values allow storage packing inside records. |
| Immutable contract references | Registry addresses are assigned once and do not require mutable configuration reads. |
| Mappings and bounded count reads | Records are retrieved by identifier without storing full unbounded arrays. |
| Event-based history | Events provide audit history without a second on-chain history table. |
| Pull payments | Purchase credits the seller, who withdraws separately. This reduces external-call risk during purchase but adds one transaction. |
| Complete-batch trading | The contracts avoid partial quantity accounting at the cost of excluding partial sale and retirement. |

The registration guard performs an external role lookup on ordinary writes. The current measurements include this check. No percentage saving is claimed because the project did not benchmark an alternative contract implementation under the same conditions.

## Reproduction

After installing the local EVM dependencies, run:

```powershell
$env:NODE_PATH = (Resolve-Path tmp/evm-tools/node_modules).Path
node scripts/measure_current_gas.cjs
```

The command recreates `submission/gas/gas-results.csv` from a fresh local deployment and fails if a receipt or final state check fails.
