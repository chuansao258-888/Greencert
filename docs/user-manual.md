# GreenCert User Manual

## Purpose and scope

GreenCert records the lifecycle of a simulated renewable energy certificate batch on Sepolia. A batch moves through wallet submission, Admin review, listing, purchase and retirement. One REC represents one MWh in this prototype. Transactions use Sepolia test ETH and have no real-world monetary value.

Each certificate is traded and retired as a whole batch. The application does not support partial purchases, partial retirement, secondary resale, or reversal of retirement.

## Before you start

You need MetaMask, a Sepolia wallet and test ETH for transactions. A wallet that purchases a batch needs enough test ETH to cover the total listing price. Visitors can open Home, Market, certificate details and Audit without connecting a wallet.

### Mobile browser access

On a phone, use the MetaMask in-app browser. If a normal mobile browser does not expose MetaMask, GreenCert shows **Open in MetaMask** and **Copy page link**. The first option opens MetaMask’s official deep link for the current page, so a certificate record or Market page is preserved. If the browser blocks the link, copy the page link and open it manually from MetaMask’s browser.

The header reports the wallet's actual network. **Wallet: Sepolia** means the connected wallet is on the required network. **Wallet: wrong network** means switch MetaMask to Sepolia before connecting, reading wallet-controlled contract data or sending a transaction. Select **Switch to Sepolia** to request the change from MetaMask.

## Connect a wallet

1. Open the application and select the wallet button in the header.
2. Select the intended MetaMask account.
3. Switch MetaMask to Sepolia if prompted.
4. Sign the login message.

The login signature creates an application session. It does not send a blockchain transaction or consume gas. Any signed-in wallet can submit an application, sell a certificate it owns, buy a listing and retire an unlisted certificate it owns. The Admin account is set when `RoleRegistry` is deployed and is the only account allowed to approve or reject applications.

## Register a role

Open **Account** after signing in. An unregistered wallet can select **Register as Producer** or **Register as Buyer**. Review the permanent choice, then confirm the transaction in MetaMask. Registration costs Sepolia gas and can be performed only once per wallet. The page reads the registered role from the server's on-chain lookup after confirmation and on subsequent visits.

Producer and Buyer describe the wallet's primary participation; both may apply, buy and manage their own certificates. Registration is optional for these operations. Admin is assigned at deployment and cannot be selected through registration. Only Admin can approve or reject applications. The header continues to show the shortened wallet address.

## Any signed-in wallet

### Submit a batch application

Open **Applications** and complete the New batch application form.

| Field | Requirement |
| --- | --- |
| Site code | A site identifier, for example `SOLAR-01`. |
| Site name | A readable name for the site. |
| Energy source | Solar, Wind or Hydro. |
| Country code | A two-letter code, for example `SG`. |
| Generation period | A completed period; the end date must be before today. |
| Batch index | A positive integer used with the site and period to identify the batch. |
| Quantity | An integer from 1 to 100 RECs. |
| Evidence | A PDF, PNG or JPEG file up to 5 MiB. |

Select **Upload and submit**, then review and confirm the MetaMask transaction. The application stores the file and creates its metadata before MetaMask opens. A successful upload alone does not mean that the application was submitted.

The status message follows the transaction through wallet and network checks, MetaMask approval, submission, receipt confirmation and contract-event verification. A submitted hash is recorded before the receipt is available. If confirmation takes too long, do not submit the form again; check the transaction in MetaMask or Etherscan, then refresh the page.

`CertificateRegistry.submitApplication` creates a Pending application, reserves its batch key, stores the quantity and metadata hash, and emits `ApplicationSubmitted`. The original evidence file is not stored on-chain. After a successful receipt, the application appears as **Pending**.

### Withdraw a pending application

Open a Pending application in **Applications** and select **Withdraw**. Confirm the MetaMask transaction. Only the wallet that created the application can withdraw it, and it cannot be withdrawn after review.

`CertificateRegistry.withdrawApplication` changes the application status to **Withdrawn**. The batch key remains reserved and cannot be reused.

### List a certificate

After an application is approved, open **My RECs** using the wallet that owns the Active certificate and select **List batch**. Enter one total ETH price for the complete batch, then confirm in MetaMask.

`CertificateMarket.listCertificate` creates an active listing and marks the certificate as listed. The certificate quantity does not change.

### Change or cancel a listing

For an active listing in **My RECs**:

- Select **Change price** to set a new total price for the complete batch.
- Select **Cancel listing** to remove it from Market.

Both actions require MetaMask confirmation. Cancelling a listing does not transfer ownership; the certificate remains Active and owned by the same wallet.

### Withdraw sale proceeds

After another wallet purchases a batch, open **Account**. The **Claimable sales** amount shows the proceeds credited to the seller. Select **Withdraw proceeds** and confirm the transaction.

`CertificateMarket.withdraw` transfers the credited test ETH to the seller and clears the claimable balance. Purchase and withdrawal are separate transactions.

## Admin

Open **Applications** using the Admin wallet. Pending applications show the Producer address, batch quantity and review controls.

1. Select **View details** and check the site, period, quantity and metadata hash.
2. Select **Download evidence** to inspect the uploaded file.
3. Choose **Approve** or **Reject**.

Approving calls `CertificateRegistry.approveApplication`. The application becomes **Approved** and one Active certificate is issued to the Producer with the submitted quantity and metadata hash.

Rejecting requires a reason and calls `CertificateRegistry.rejectApplication`. The application becomes **Rejected** and no certificate is issued.

Only Pending applications can be reviewed. Evidence review is a manual decision; a matching hash shows record consistency, not independent proof of electricity generation.

## Purchase and retirement

### Review a listing

Open **Market**. Each entry represents one complete certificate batch and shows its quantity and total price. Select the certificate or public record link to inspect its owner, status, metadata hash, evidence-integrity summary and on-chain history.

### Buy a whole batch

Select **Buy whole batch**. Confirm the quantity and total price, then confirm the MetaMask transaction. The value sent must equal the current total listing price.

`CertificateMarket.buyCertificate` checks the listing status and expected price. It transfers the whole certificate to the purchasing wallet, closes the listing and credits sale proceeds to the seller in one transaction. If the seller changes the price before confirmation, refresh Market and start again.

After a successful receipt, the batch is removed from Market and appears in the purchasing wallet's **My RECs** page.

### Retire a certificate

Open **My RECs**, select an Active unlisted certificate owned by the connected wallet, and choose **Retire whole batch**. Enter the retirement beneficiary and purpose, then confirm in MetaMask.

`CertificateRegistry.retireCertificate` records a hash of the retirement statement and changes the certificate status to **Retired**. The certificate remains owned by the same wallet, but cannot be listed or traded again.

## Public audit and activity records

### Public certificate record

Open a certificate from Market, My RECs or Audit. The public record shows its quantity, owner, status, listing status, metadata hash and, where applicable, retirement beneficiary and purpose.

### Evidence integrity

The evidence-integrity section checks:

1. The certificate is linked to an approved application.
2. Stored metadata matches the on-chain metadata hash.
3. Batch details match the approved application.
4. The locally stored evidence file matches its SHA-256 hash.

**Verified** means these records match. It does not prove that renewable electricity was generated. The uploaded evidence file remains private; visitors and Buyers can view only the integrity summary.

### Audit

Open **Audit** to review certificate status, integrity results and on-chain history. Each event includes a transaction link for Sepolia Etherscan.

### Activity

After connecting a wallet, open **Activity** to view transactions that the server has verified for the current wallet. This is a personal activity record, not a complete chain-wide event list.

## Status reference

| Item | Status | Meaning |
| --- | --- | --- |
| Application | Pending | Submitted by a wallet and waiting for Admin review. |
| Application | Approved | Reviewed by Admin; a certificate was issued. |
| Application | Rejected | Rejected by Admin; no certificate was issued. |
| Application | Withdrawn | Withdrawn by its submitting wallet before review. |
| Certificate | Active | Issued and not retired. |
| Certificate | Listed | An Active certificate with a current Market listing. |
| Certificate | Retired | Permanently removed from trading after its owner's retirement transaction. |

## Common issues

| Issue | What to check |
| --- | --- |
| Wallet connection fails | Confirm MetaMask is unlocked and the selected network is Sepolia. |
| MetaMask is unavailable in a phone browser | Select **Open in MetaMask**, or copy the current page link and open it from MetaMask’s browser. |
| Wallet: wrong network | Switch the wallet to Sepolia, then retry the action. |
| MetaMask says a request is pending | Open MetaMask and approve or reject the existing request before starting another action. |
| Transaction is rejected | Check the MetaMask confirmation window, account balance and role. |
| Transaction stays pending | Do not submit again. Keep the transaction hash, inspect it in MetaMask or Etherscan, and refresh after it is confirmed. |
| A listing cannot be purchased | Refresh Market. The listing may have been cancelled, purchased or repriced. |
| An application cannot be submitted | Check the date range, quantity, batch index and evidence file type and size. A previously used batch key cannot be submitted again. |
| Evidence integrity is Incomplete | The on-chain certificate may exist while matching local metadata or a file is unavailable. |
| Audit data is unavailable | Check the Sepolia RPC connection and reload the page. |

## Safe use

Use test wallets only. Do not enter, upload or share a wallet private key. Confirm the receiving contract and transaction value in MetaMask before approving a transaction. GreenCert is a Sepolia testnet prototype and is not a real REC registry or payment service.
