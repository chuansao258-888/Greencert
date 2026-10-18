# Sepolia workflow checklist

Record transaction hash, receipt status and gas used for every successful write.

Before signing each deployment, compare the full constructor arguments with `deployment.json`. For `CertificateRegistry`, `roleRegistryAddress` must be the deployed `RoleRegistry` contract, not the Admin wallet. For `CertificateMarket`, verify both contract addresses. After each deployment, read back `roleRegistry()` and `certificateRegistry()` where available; a successful receipt alone does not prove the contracts were linked correctly.

- [x] Deploy RoleRegistry, CertificateRegistry and CertificateMarket.
- [x] Bind CertificateMarket with CertificateRegistry.setMarket.
- [x] Register Producer and Buyer roles.
- [ ] On the revised Registry and Market, verify that an unregistered wallet cannot submit an application or buy a listing. Record the reverted transaction or preflight error.
- [x] Submit and withdraw an application.
- [x] Submit and reject a second application.
- [x] Submit and approve a multi-unit batch application.
- [x] List, reprice and cancel the certificate listing.
- [x] List again and buy the complete batch for the exact total price.
- [x] Withdraw the Producer's sale proceeds.
- [x] Retire the complete batch as Buyer.
- [x] Confirm final owner, quantity, status and evidence access from a fresh server instance.

The completed items above are evidence for the deployed open-wallet Registry and Market. The unchecked registration-gate item is required after the replacement contracts in `docs/development/09-registration-deployment.md` are deployed.

The final persistence check created a fresh Flask instance against the existing on-disk database and evidence folder, then authenticated Admin and downloaded the approved evidence. The mobile-browser checklist remains separate.
