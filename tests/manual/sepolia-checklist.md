# Sepolia workflow checklist

Record transaction hash, receipt status and gas used for every successful write.

Before signing each deployment, compare the full constructor arguments with `deployment.json`. For `CertificateRegistry`, `roleRegistryAddress` must be the deployed `RoleRegistry` contract, not the Admin wallet. For `CertificateMarket`, verify both contract addresses. After each deployment, read back `roleRegistry()` and `certificateRegistry()` where available; a successful receipt alone does not prove the contracts were linked correctly.

- [x] Deploy RoleRegistry, CertificateRegistry and CertificateMarket.
- [x] Bind CertificateMarket with CertificateRegistry.setMarket.
- [x] Register Producer and Buyer roles.
- [ ] Submit and withdraw an application.
- [ ] Submit and reject a second application.
- [x] Submit and approve a multi-unit batch application.
- [ ] List, reprice and cancel the certificate listing.
- [ ] List again and buy the complete batch for the exact total price.
- [ ] Withdraw the Producer's sale proceeds.
- [ ] Retire the complete batch as Buyer.
- [ ] Confirm final owner, quantity, status and evidence access after server restart.

The boxes remain unchecked until the transactions have been completed on Sepolia.
