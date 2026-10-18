# Test results

## Recheck on 18 October 2026

Source under test was commit `5c1ace4` plus the added local runner `scripts/run_contract_tests.cjs`; no contract source changed in this recheck. Python 3.14.3: `python -m unittest discover -s tests/backend -t . -v` passed 18 tests. Node v24.13.1: `npm run test:frontend` passed all seven scripts. `npm run compile` and `npm run test:contracts:compile` passed with solc 0.8.30. These compilation commands alone do not execute Solidity tests.

The 14 current Solidity test functions were executed on an isolated in-process Ganache 7.9.2 Shanghai EVM with ethers 6.17.0, solc `0.8.30+commit.73712a01` and optimizer 200. All 14 passed and none failed: two role, six registry and six market tests, including rejection of unregistered submission and purchase. The local runner substitutes a reverting `Assert.ok` for Remix's assertion event and deploys a fresh test contract per function. Payable tests receive 100 wei. This is a local EVM execution, not a Remix run or Sepolia receipt; it uses Shanghai and a different compiler from the deployed 0.8.34/Osaka build. Ganache allowed oversized test harness contracts and used its JavaScript fallback for an unavailable optional native module. Output is in [contract-test-local.txt](contract-test-local.txt).

To repeat from the repository root after `npm ci`:

```powershell
npm install --prefix tmp/evm-tools --no-save --no-package-lock ganache@7.9.2 ethers@6.17.0
$env:NODE_PATH = (Resolve-Path tmp/evm-tools/node_modules).Path
node scripts/run_contract_tests.cjs
```

## Current public deployment observation

On 18 October 2026, `/api/health` returned HTTP 200 and `ready`; `/api/config` returned the addresses in `deployment.json`. Normalizing CRLF/LF, the served `wallet.js`, `transactions.js`, `pages.js` and Registry ABI matched commit `5c1ace4`; this does not identify the entire running Git commit. `/api/certificates` showed certificate 1, quantity 1, Active and listed, with `metadata: null`. `/api/audit` reported `incomplete`: approved application passed but metadata hash, fields and evidence file were unavailable. `/api/dashboard` consequently grouped 1 MWh under Unknown. The service responses alone do not establish why supporting data is absent. A read-only lookup of the matching content hash in the one local `instance/greencert.db` found no matching row; no Render database inspection or recovery was performed. SQLite records and uploads are on the free service filesystem and can be lost; no persistent disk is configured. Do not approve a new application without first checking its evidence: the UI does not automatically block approval when supporting data is missing.

The public audit returned the following events for the **current** guarded contracts. Independent read-only Sepolia RPC receipt queries returned status 1 and the stated target and block. These two receipts are partial current-deployment evidence, not a complete lifecycle or a new signed test by this recheck.

| Event | Block | Receipt target | Gas used | Transaction |
|---|---:|---|---:|---|
| CertificateIssued | 11939939 | current Registry | 929,116 | [`0xca9b30…de1853c`](https://sepolia.etherscan.io/tx/0xca9b30e68e2e0a0ac321c1e57a98d2af0922219e7edf7707e8d9ef02dae1853c) |
| CertificateListed | 11939943 | current Market | 489,412 | [`0x340d7c…da8c519`](https://sepolia.etherscan.io/tx/0x340d7cfa5ca2dedfbade64a2884a5bc29ff84c7b2304d0cd724b74610da8c519) |

Both receipts reported effective gas price 1,500,000,016 wei. The API event record identifies the events; the independent receipt query checked status, target, block and gas, not the event decoding. The public responses are saved in [public-observation-2026-10-18.txt](public-observation-2026-10-18.txt); more recent state may differ.

## Local checks

On 18 October 2026, the current source was checked after adding mandatory Producer/Buyer registration for business operations. The automated checks cover role display, both registration choices, cancellation, the hidden application form for an unregistered wallet, and the client-side gate before application, listing, purchase, retirement and withdrawal actions. Backend checks confirm that an unregistered session cannot upload evidence or create content. These are local automated checks; signed Sepolia registration and guarded lifecycle execution require separate evidence.

| Check | Result |
|---|---|
| Python `unittest` suite | 18 tests passed |
| Application Solidity compilation | Passed with local solc `0.8.30+commit.73712a01.Emscripten.clang` |
| Solidity test-source compilation | Passed with local solc `0.8.30+commit.73712a01.Emscripten.clang` |
| Frontend checks | 7 Node.js scripts passed: dashboard, wallet session, mobile deep link, transaction stages, application role, audit and role registration |
| Registration-gate API checks | Passed: unregistered upload and content requests are rejected |
| Registration-gate contract source checks | Passed: submission and purchase tests include unregistered rejection cases |

## Current registration-guard status

The current Sepolia Registry and Market are the guarded contracts in `deployment.json`. On 18 October 2026, both were compiled in Remix with Solidity `0.8.34`, deployed, and bound by the Admin. The Registry deployment receipt was `0x1` in transaction `0x843a3f939114225f2b93f85978e81ac6ddaf3b5e8a5967e768a1b98b4fa7a4ef`; the Market deployment receipt was `0x1` in transaction `0x5736383495b5f4eff81277a3148a4af64900ab977fc35fe62d895c60bdc73f0d`. Binding transaction `0xd20152cf4832b68e201e983bccc5e9a3ecbeac86a8957188061b1401ad79720b` also had receipt status `0x1`.

A read-only call from unregistered address `0x1111111111111111111111111111111111111111` reverted with `Register a role first` for both `submitApplication(...)` and `buyCertificate(1, 0)`. This confirms that direct contract calls are gated independently of the website and API.

## Remix Solidity Unit Testing

| Suite | Passed | Failed |
|---|---:|---:|
| `CertificateMarket_test.sol` | 5 | 0 |
| `CertificateRegistry_test.sol` | 5 | 0 |
| `RoleRegistry_test.sol` | 2 | 0 |
| **Total** | **12** | **0** |

The results above were reported by Remix Solidity Unit Testing for the earlier contract revision. They are retained as recorded execution evidence for its workflow. The current test sources have been compiled locally but have not yet been executed in Remix after the registration-guard changes. The automated Sepolia end-to-end workflow is recorded below.

## Earlier Sepolia deployment

A separate intermediate deployment used the following addresses. These are not the contracts used by the historical full lifecycle CSV below; the current guarded addresses are in `deployment.json`. `RoleRegistry` was created at `0x628a94ff69e5bb527ce8b6dbbc1f480458af9d02` in transaction `0x2a2f617c23de24a1e47897f1bbc49041e23c7645b623277e7fb2d7dca653a561`, `CertificateRegistry` at `0x7a8b0776910828da7b91144b61e6669d5a3c3723` in transaction `0x421c3f35f3a3753cc2cd1f404b305938aa6e1c4194b6ad2858ac3132c52d9a1f`, and `CertificateMarket` at `0xef2db1a0e411c3ded0756493ad5703b8404646fd` in transaction `0xffd6de89d8f8b96c08089de71acaa6042e2127df191a5e34a89b78615831eed9`.

The Admin then called `setMarket` in transaction `0xfdef98a0ed1b2a539384e0723a123c7e7b5d3434fd17adad0a64c74c89a12981`. The receipt status was `0x1`; a subsequent `market()` call on `CertificateRegistry` returned `0xef2db1a0e411c3ded0756493ad5703b8404646fd`.

The historical workflow record below and `gas-results.csv` instead refer to the 13 October deployment: RoleRegistry `0xc6ddfdef0eef7b9d2bb6df9e60bf439a2725a369`, Registry `0x338c972fcab0892448fa0ee939f3330fb42f6c04`, and Market `0xd7f2b6c233e7044ab4a76317b834c58c2ff23f01`. Its configuration was recorded in `deployment.json` at commit `c93a5bf`.

On 18 October, Blockscout returned the CSV transactions with the recorded blocks, statuses and gas used; the successful business calls targeted the historical Registry or Market above, and registrations targeted its RoleRegistry. One public RPC returned null for the older hashes, so Blockscout was used for this historical check. The row-by-row response summary is in [historical-receipt-check.txt](historical-receipt-check.txt).

A Sepolia `CertificateRegistry` creation at `0x73ab2452c4ad4d51b64329ece959964efcd39754` succeeded as a transaction but incorrectly pointed to the Admin wallet. It is excluded from `deployment.json` and must not be used. Read-only Sepolia calls confirmed that the updated constructor accepts the deployed `RoleRegistry` and rejects the Admin wallet before a transaction is sent. The replacement `CertificateRegistry` at `0x338c972fcab0892448fa0ee939f3330fb42f6c04` was then deployed successfully; its `roleRegistry()` returned the expected contract address. The `CertificateMarket` at `0xd7f2b6c233e7044ab4a76317b834c58c2ff23f01` was deployed successfully and returned both expected registry addresses.

The first `setMarket` attempt was routed by MetaMask's optional Added protection to `0xdb9b1e94b5b69df7e401ddbede43491141047db3` and reverted in block 11907671. The transaction input contained the intended Registry call and Market address, but the receipt status was `0x0` and the Registry's `market()` remained zero. A direct read-only call from the Admin address to the Registry with the same `setMarket` calldata succeeded, and direct gas estimation returned 135,445. The exact cause of the protected-call revert has not been established.

With optional Added protection disabled, Admin sent `setMarket` directly to `CertificateRegistry` in transaction `0x8ccc9c94f56d3ca74da3a023256f91c8bc657b0f1e12981383763c808890e0a2`. The receipt status was `0x1` in block 11907687. A subsequent read of `market()` returned `0xd7f2b6c233e7044ab4a76317b834c58c2ff23f01`, confirming the binding.

Producer `0x7ac1c7fb0c77332b2d74688fca86b9c9a3d5b028` registered with role `1` in transaction `0x349091739d0df35dbd24e323a73817a28b6c4a041d8934157fae92a00057d365`. Its receipt status was `0x1` in block 11907723, and `roleOf(Producer)` returned `1`.

Buyer `0x280d860553cb04d14cefc35b8726fb360df633ff` registered with role `2` in transaction `0x7f9685b5a532fe724eea77b1b1f75afbaabb2b8a722a6954d52f41801b7e1ecc`. Its receipt status was `0x1` in block 11907741, and `roleOf(Buyer)` returned `2`.

The Producer's first local-site application transaction `0xe72b0583f924ee529e56df0a5cbfd483037299a314feb65543f1689def1d6914` was routed through MetaMask's `redeemDelegations` contract at `0xdb9b1e94b5b69df7e401ddbede43491141047db3` despite the confirmation view showing the Registry as the interaction target and an apparently unchecked optional protection control. Its receipt status was `0x0` in block 11907835. Blockscout's raw trace shows that the delegated inner call reached the correct Registry but ran out of gas. The inner call was allocated approximately 971,000 gas; a read-only direct call with the same calldata ran out at 971,000 gas and succeeded at 1,031,882 gas. The Registry's `applicationCount()` remained zero. This failure cost 1,653,388,516,533,885 wei. The application metadata and evidence were stored locally before the failed chain transaction; they were not anchored on-chain.

Producer then submitted the saved five-unit batch directly to `CertificateRegistry` using Remix in transaction `0x625452ea4591e657e9b7a0a440c0a99d099c5cce493b0f75b3dfde7bd5bedd9a`. Its receipt status was `0x1` in block 11907862. The six call arguments matched the saved application content. `applicationCount()` returned `1`, and `getApplication(1)` returned the Producer address, quantity `5`, metadata hash `0x342077c31f9f344e8de5c7946e71f3faafa877d5729775576a0b000dc9ac7b93`, and status `Pending`. Gas used was 1,022,587, costing 1,533,880,515,338,805 wei.

Admin approved application `1` directly through Remix in transaction `0xed15b7ff0a37f5a81a144fdc101847007f329bf82297507a01038b7a22ef9e29`. Its receipt status was `0x1` in block 11907893. `getApplication(1)` returned `Approved` and certificate ID `1`; `certificateCount()` returned `1`; `getCertificate(1)` returned the Producer as owner, quantity `5`, and status `Active`. Gas used was 926,995, costing 1,390,492,513,904,925 wei.

Producer listed certificate `1` directly through Remix in transaction `0xbef6a00ab752e5ac6c32c407ac87014565646c29c9ab1243584a21f24ba42c48`. Its receipt status was `0x1` in block 11907923. `getListing(1)` returned the Producer as seller, total batch price `100000000000000` wei, and `active=true`; `getCertificate(1)` returned `listed=true` with quantity `5`. Gas used was 488,232, costing 732,348,007,323,480 wei.

## Historical automated Sepolia execution

The signed runner `scripts/sepolia_e2e.py` completed ten direct transactions in blocks 11908037–11908048 against the earlier open-wallet Registry and Market. Each step passed a pre-send read-only call and gas estimate, then a successful receipt, expected event and immediate contract-state check before the next transaction was sent. An independent read-only pass checked all ten receipts and final storage again. Exact transaction hashes, gas used, gas price and costs are in `gas-results.csv`; the ten transactions together used 2,997,934 gas and cost 2,997,978,969,010 wei (0.00000299797896901 SepoliaETH). Repeat the same measurement after deploying the current guarded source.

| Step | Block | Verified result |
|---|---:|---|
| Reprice | 11908037 | Active total batch price became 200,000,000,000,000 wei |
| Cancel | 11908039 | Listing inactive; certificate no longer listed |
| Relist | 11908041 | Listing active again at 100,000,000,000,000 wei |
| Buy | 11908042 | Buyer owns all 5 units; seller credit and sale total equal the exact price |
| Withdraw proceeds | 11908043 | Producer credit, total credits and Market balance are zero |
| Retire | 11908044 | Buyer-owned certificate remains 5 units and is Retired |
| Submit first test application | 11908045 | Application 2 Pending, quantity 2 |
| Withdraw first test application | 11908046 | Application 2 Withdrawn |
| Submit second test application | 11908047 | Application 3 Pending, quantity 3 |
| Reject second test application | 11908048 | Application 3 Rejected with the expected reason hash |

Final independent reads returned application 1 Approved, application 2 Withdrawn, application 3 Rejected, certificate 1 Retired and owned by Buyer, `listed=false`, `soldCount=1`, and zero Producer credit and Market balance. A new Flask instance using the existing database authenticated Admin, read certificate and application 1, downloaded its 186,794-byte evidence file, and matched its SHA-256 to the saved metadata. The two extra applications and the retirement used on-chain-only test hashes, so their new review/retirement content is not available through the website; the original approved application evidence is available.
