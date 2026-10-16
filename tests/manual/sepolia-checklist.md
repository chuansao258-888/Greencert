# Sepolia workflow checklist

Record transaction hash, receipt status and gas used for every successful write.

- [ ] Deploy RoleRegistry, CertificateRegistry and CertificateMarket.
- [ ] Bind CertificateMarket with CertificateRegistry.setMarket.
- [ ] Register Producer and Buyer roles.
- [ ] Submit and withdraw an application.
- [ ] Submit and reject a second application.
- [ ] Submit and approve a multi-unit batch application.
- [ ] List, reprice and cancel the certificate listing.
- [ ] List again and buy the complete batch for the exact total price.
- [ ] Withdraw the Producer's sale proceeds.
- [ ] Retire the complete batch as Buyer.
- [ ] Confirm final owner, quantity, status and evidence access after server restart.

The boxes remain unchecked until the transactions have been completed on Sepolia.
