# Registration-guard deployment

The role gate is deployed on Sepolia. `CertificateRegistry` and `CertificateMarket` both reject ordinary state-changing calls from an address whose `roleOf` value is `None`. Admin review remains limited to the original Admin address.

## Deployed contracts

| Contract | Address | Block | Deployment transaction |
| --- | --- | ---: | --- |
| RoleRegistry (reused) | `0x628a94ff69e5bb527ce8b6dbbc1f480458af9d02` | 11938276 | recorded in the original deployment evidence |
| CertificateRegistry | `0xa3456442711ead1110d6f93e0c56b35ab25bebc9` | 11939875 | `0x843a3f939114225f2b93f85978e81ac6ddaf3b5e8a5967e768a1b98b4fa7a4ef` |
| CertificateMarket | `0x84990af8d7ca3224df64305d1330c50e21c887aa` | 11939890 | `0x5736383495b5f4eff81277a3148a4af64900ab977fc35fe62d895c60bdc73f0d` |

Admin bound the Market to the Registry in transaction `0xd20152cf4832b68e201e983bccc5e9a3ecbeac86a8957188061b1401ad79720b` at block 11939898. The receipt status was `0x1`. A later `market()` read returned `0x84990af8d7ca3224df64305d1330c50e21c887aa`.

## Verification

On 18 October 2026, the contracts were compiled in Remix with Solidity `0.8.34`, then deployed from the Admin wallet on Sepolia. An `eth_call` from unregistered address `0x1111111111111111111111111111111111111111` reverted with `Register a role first` for both:

- `CertificateRegistry.submitApplication(...)`; and
- `CertificateMarket.buyCertificate(1, 0)`.

The application stores the new addresses and deployment blocks in `deployment.json`. A new Registry and Market begin empty: records and sale credits at the previous contract addresses are not migrated. Earlier workflow receipts remain historical evidence only.
