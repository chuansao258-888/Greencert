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
| `CertificateMarket_test.sol` | 4 | 0 |
| `CertificateRegistry_test.sol` | 4 | 0 |
| `RoleRegistry_test.sol` | 2 | 0 |
| **Total** | **10** | **0** |

The results above were reported by Remix Solidity Unit Testing with the tests in `remix-upload/tests/contracts`. They replace the earlier inconclusive `Passed: 0, Failed: 0` run. Sepolia and mobile-wallet checks have not been run because contract addresses are not configured.
