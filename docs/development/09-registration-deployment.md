# Required-registration deployment transition

The frontend prompts unregistered wallets after login and restored sessions. Cancelling allows public browsing only. Before business actions it rechecks the authenticated wallet's role. Upload and content APIs independently reject unregistered callers. Registration transactions and their receipt verification remain available.

The modified CertificateRegistry and CertificateMarket sources require a non-None on-chain role for every ordinary user write. Admin review remains Admin-only. Producer and Buyer both retain submission, buying and ownership-based management permissions.

## Current deployment status

The new contract guards are not yet deployed. `deployment.json` still contains the existing open-wallet Registry and Market addresses. Website/API restrictions do not prevent a caller from using those old contracts directly.

## Deployment sequence

1. Reuse RoleRegistry `0x628a94ff69e5bb527ce8b6dbbc1f480458af9d02` to retain existing registrations and Admin.
2. Compile the current source and record the actual compiler, EVM target and optimizer settings.
3. Deploy CertificateRegistry with that RoleRegistry address.
4. Deploy CertificateMarket with the same RoleRegistry address and the new CertificateRegistry address.
5. From the existing Admin wallet, call the new Registry's `setMarket(newMarket)` once.
6. Verify successful deployment/binding receipts and read back both registry references and `market()`.
7. Update deployment.json, README contract links and matching ABIs; deploy the web service.
8. Verify an unregistered call to submitApplication and buyCertificate reverts with registration required. Verify registered Producer and Buyer can each apply and buy, subject to ownership and price checks.

New Registry/Market deployments start with no applications, certificates or sale credits. Old records and any claimable proceeds remain at the old addresses; this procedure does not migrate or erase them. Keep those addresses and transaction evidence available.

## Validation

18 October 2026: backend tests passed (18), frontend checks passed (7 scripts), application and Solidity test sources compiled successfully. Added rejection coverage for unregistered API uploads/content, hidden application forms and Solidity submission/purchase checks. Solidity test execution and real-wallet popup/registration verification on this revision remain pending; compilation is not execution.
