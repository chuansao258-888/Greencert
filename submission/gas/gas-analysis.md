# Gas Estimation and Optimisation Analysis

## Scope

This note separates two kinds of evidence:

- `gas-results.csv` contains mined receipts from the 13 October Sepolia deployment: RoleRegistry `0xc6ddfdef0eef7b9d2bb6df9e60bf439a2725a369`, Registry `0x338c972fcab0892448fa0ee939f3330fb42f6c04` and Market `0xd7f2b6c233e7044ab4a76317b834c58c2ff23f01`. Its configuration was recorded at commit `c93a5bf` (solc 0.8.30, Prague, optimizer 200). Blockscout returned the CSV receipt statuses, blocks, targets and gas used on 18 October.
- The current Registry and Market include an `onlyRegistered` check and were deployed on 18 October 2026. The receipt figures below remain measurements of the earlier full lifecycle; an equivalent guarded lifecycle measurement has not yet been recorded. Deployment and guard verification are in [registration deployment](../../docs/development/09-registration-deployment.md).

All values are for a testnet prototype. They are useful for comparing this implementation's transaction paths; they are not a production cost forecast.

## Estimation before signing

The browser prepares a transaction only after checking the connected account and Sepolia chain. For the scripted Sepolia workflow, `scripts/sepolia_e2e.py` first performs a read-only preflight call and calls `estimate_gas`. It then creates a gas limit with a buffer:

```text
max(estimatedGas × 1.3 + 50,000, estimatedGas + 100,000)
```

The runner rejects a transaction if that calculated limit is above its configured cap or if the test wallet lacks the required value plus estimated gas cost. A successful receipt records actual `gasUsed` and the effective gas price. Actual cost is calculated as:

```text
gasUsed × effectiveGasPrice
```

The website does not display its own explicit gas estimate; MetaMask handles transaction preparation and fee settings. The script estimate is preparation information, not a guarantee. A rejected or pending wallet request is not retried automatically.

## Recorded receipt measurements

The following successful workflow receipts are copied from `gas-results.csv`. They cover ten distinct state-changing paths after the certificate was issued and listed.

| Transaction | Gas used |
|---|---:|
| Reprice listing | 34,416 |
| Cancel listing | 43,735 |
| Relist certificate | 174,472 |
| Buy complete batch | 511,850 |
| Withdraw seller proceeds | 53,021 |
| Retire certificate | 151,054 |
| Submit application for withdrawal test | 924,679 |
| Withdraw application | 33,826 |
| Submit application for rejection test | 924,679 |
| Reject application | 146,202 |
| **Total** | **2,997,934** |

The receipts used an effective gas price of 1,000,015 wei. Their combined transaction fee was 2,997,978,969,010 wei, or 0.00000299797896901 SepoliaETH. The batch purchase also transfers its separately displayed listing value; that value is not a gas fee.

The larger costs occur where the contracts create a new application record or coordinate multiple state updates. A purchase updates the listing, certificate ownership and seller credit atomically. Low-cost operations such as repricing or withdrawing an already-recorded credit alter fewer storage locations.

## Design choices affecting gas

| Choice | Effect and trade-off |
|---|---|
| Optimizer enabled with 200 runs | The historical deployment configuration records Solidity optimisation for a repeated-use application contract. The same setting must be used when comparing a replacement deployment. |
| Compact timestamp and quantity fields | `uint64` is used for timestamps and `uint32` for quantity and batch index inside record structs, reducing storage footprint where Solidity can pack fields. |
| Immutable contract references | Registry references are assigned once in constructors, avoiding mutable configuration storage on ordinary calls. |
| Mappings with bounded count reads | Applications, certificates, listings and credits use mappings. Counts support bounded page reads instead of storing unbounded arrays of full records. |
| Event-based history | Events provide transaction history without duplicating a separate on-chain history table. The application reads logs for audit views. |
| Pull payments | A purchase credits the seller; the seller withdraws separately. This avoids sending Ether to an arbitrary seller during the purchase, at the cost of a later withdrawal transaction. |
| Complete-batch trading | Listing, purchase and retirement do not require quantity-splitting accounting. The trade-off is that partial sale and partial retirement are outside scope. |

The new `onlyRegistered` modifier adds an external role lookup on each ordinary write. It improves enforcement consistency but may increase gas use. No saving or increase is claimed until the same full set of paths is measured on the guarded contracts.

## Limits and next measurement

Receipt `gasUsed` is the reliable measurement for a completed transaction. It varies with the transaction path and storage state, so a single estimate cannot represent every case. For the guarded contracts, repeat registration, application, listing, purchase, withdrawal and retirement with the same test quantities; save the new receipts beside the historical CSV and compare like-for-like paths. Do not compare compiler or EVM settings unless they match the recorded deployment configuration.
