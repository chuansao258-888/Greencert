# Sepolia workflow checklist

Record transaction hash, receipt status and gas used for every successful write.

Before signing each deployment, compare the full constructor arguments with `deployment.json`. For `CertificateRegistry`, `roleRegistryAddress` must be the deployed `RoleRegistry` contract, not the Admin wallet. For `CertificateMarket`, verify both contract addresses. After each deployment, read back `roleRegistry()` and `certificateRegistry()` where available; a successful receipt alone does not prove the contracts were linked correctly.

- [x] Deploy RoleRegistry, CertificateRegistry and CertificateMarket.
- [x] Bind CertificateMarket with CertificateRegistry.setMarket.
- [x] Register Producer and Buyer roles.
- [x] On the guarded Registry and Market, read-only calls from an unregistered address to `submitApplication` and `buyCertificate` both reverted with `Register a role first` on 18 October 2026. See `docs/development/09-registration-deployment.md`.
- [x] Submit and withdraw an application.
- [x] Submit and reject a second application.
- [x] Submit and approve a multi-unit batch application.
- [x] List, reprice and cancel the certificate listing.
- [x] List again and buy the complete batch for the exact total price.
- [x] Withdraw the Producer's sale proceeds.
- [x] Retire the complete batch as Buyer.
- [x] Confirm final owner, quantity, status and evidence access from a fresh server instance.

The lifecycle items above are evidence for the earlier open-wallet Registry and Market. The registration-gate item is evidence for the current guarded contracts. A complete issuance, purchase and retirement cycle has not yet been recorded on the guarded contracts.

The final persistence check created a fresh Flask instance against the existing on-disk database and evidence folder, then authenticated Admin and downloaded the approved evidence. The mobile-browser checklist remains separate.
