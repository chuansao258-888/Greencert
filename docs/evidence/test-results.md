# Test results

## Local checks

| Check | Result |
|---|---|
| Python `unittest` suite | 11 tests passed |
| Application Solidity compilation | Passed with solc 0.8.30 |
| Solidity test-source compilation | Passed with solc 0.8.30 |
| JavaScript syntax checks | Passed with Node.js |
| Dashboard chart rendering | Passed with the Node.js frontend check |
| Local browser layout preview | Navigation, market empty state and dashboard chart panels rendered; chart panels showed the configuration message while contracts were unavailable |

## Remix Solidity Unit Testing

| Suite | Passed | Failed |
|---|---:|---:|
| `CertificateMarket_test.sol` | 5 | 0 |
| `CertificateRegistry_test.sol` | 5 | 0 |
| `RoleRegistry_test.sol` | 2 | 0 |
| **Total** | **12** | **0** |

The results above were reported by Remix Solidity Unit Testing with the updated tests in `remix-deploy/tests/contracts`. They replace the earlier inconclusive `Passed: 0, Failed: 0` run and include the constructor address checks. Sepolia end-to-end and mobile-wallet checks have not yet been run.

A Sepolia `CertificateRegistry` creation at `0x73ab2452c4ad4d51b64329ece959964efcd39754` succeeded as a transaction but incorrectly pointed to the Admin wallet. It is excluded from `deployment.json` and must not be used. Read-only Sepolia calls confirmed that the updated constructor accepts the deployed `RoleRegistry` and rejects the Admin wallet before a transaction is sent. The replacement `CertificateRegistry` at `0x338c972fcab0892448fa0ee939f3330fb42f6c04` was then deployed successfully; its `roleRegistry()` returned the expected contract address. The `CertificateMarket` at `0xd7f2b6c233e7044ab4a76317b834c58c2ff23f01` was deployed successfully and returned both expected registry addresses.

The first `setMarket` attempt was routed by MetaMask's optional Added protection to `0xdb9b1e94b5b69df7e401ddbede43491141047db3` and reverted in block 11907671. The transaction input contained the intended Registry call and Market address, but the receipt status was `0x0` and the Registry's `market()` remained zero. A direct read-only call from the Admin address to the Registry with the same `setMarket` calldata succeeded, and direct gas estimation returned 135,445. The exact cause of the protected-call revert has not been established.

With optional Added protection disabled, Admin sent `setMarket` directly to `CertificateRegistry` in transaction `0x8ccc9c94f56d3ca74da3a023256f91c8bc657b0f1e12981383763c808890e0a2`. The receipt status was `0x1` in block 11907687. A subsequent read of `market()` returned `0xd7f2b6c233e7044ab4a76317b834c58c2ff23f01`, confirming the binding.

Producer `0x7ac1c7fb0c77332b2d74688fca86b9c9a3d5b028` registered with role `1` in transaction `0x349091739d0df35dbd24e323a73817a28b6c4a041d8934157fae92a00057d365`. Its receipt status was `0x1` in block 11907723, and `roleOf(Producer)` returned `1`.

Buyer `0x280d860553cb04d14cefc35b8726fb360df633ff` registered with role `2` in transaction `0x7f9685b5a532fe724eea77b1b1f75afbaabb2b8a722a6954d52f41801b7e1ecc`. Its receipt status was `0x1` in block 11907741, and `roleOf(Buyer)` returned `2`.
