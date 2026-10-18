# Product and Requirements

## Project Objective

GreenCert gives small renewable energy producers and business buyers a simple way to demonstrate certificate issuance, purchase and retirement. The project focuses on completing this workflow with clear ownership records, visible transaction history and a usable mobile interface.

The proposed problem is fragmented evidence: a buyer needs to understand where a certificate came from, who owns it and whether its environmental attributes have already been claimed. GreenCert links reviewed generation evidence to a certificate record and makes retirement a permanent state change. Research or user interviews should substantiate this problem before it is presented as a validated finding.

## Roles

| Role | Responsibilities |
|---|---|
| Connected wallet | Upload evidence; submit or withdraw its pending applications; list, reprice, cancel, purchase or retire certificates according to ownership and listing state; withdraw its sales proceeds. |
| Producer | Optional on-chain primary role for generation participants; retains all connected-wallet operations. |
| Buyer | Optional on-chain primary role for purchasers; retains all connected-wallet operations. |
| Admin | Review generation evidence and approve or reject pending applications. |
| Visitor | Browse public certificate records, evidence-integrity summaries, market listings, dashboard data and the read-only audit. |

The Admin address is fixed at deployment. First connection prompts unregistered wallets to register as Producer or Buyer. The signed-in session reads roles from the chain. Producer and Buyer share ordinary certificate permissions after registration; only Admin reviews applications. Unregistered wallets may browse public records only. Visitors are not an authenticated role. The contract deployment transition is tracked in 09-registration-deployment.md.

## Functional Requirements

| ID | Requirement | Acceptance condition |
|---|---|---|
| FR-01 | Wallet connection | The interface identifies the connected address and actual wallet network. |
| FR-02 | Evidence submission | A signed-in wallet uploads an accepted file and submits an application linked to immutable metadata. |
| FR-03 | Review and issuance | An Admin can approve or reject a pending application after inspecting its evidence. Approval creates exactly one certificate record containing the approved batch quantity. |
| FR-04 | Application withdrawal | The submitting wallet can withdraw its own pending application. |
| FR-05 | Fixed-price listing | A certificate owner can list, reprice and cancel a complete active certificate batch. |
| FR-06 | Purchase | Exact payment of the batch's total test ETH price transfers the complete quantity and credits the seller in a single transaction. |
| FR-07 | Proceeds withdrawal | A seller can withdraw their credited proceeds without changing another seller's balance. |
| FR-08 | Retirement | A certificate owner can permanently retire a complete active unlisted batch, with a beneficiary and purpose. |
| FR-09 | Traceability | Certificate details show issuance, sale and retirement records with transaction links. |
| FR-10 | Dashboard | Issued, listed, sold and retired totals and two labeled charts reflect contract records. The source chart sums REC quantity by energy source; the status chart counts Active and Retired batches. |
| FR-11 | Mobile access | The complete role workflows work in a mobile wallet browser. |
| FR-12 | Recovery | Refreshing the browser or restarting the server does not lose confirmed business records or stored evidence. |
| FR-13 | Evidence integrity | A certificate's public summary distinguishes matching, missing and inconsistent application, metadata and evidence-file hashes without releasing the uploaded file. |
| FR-14 | Read-only audit | The public audit lists certificate integrity results and on-chain certificate events with transaction links and a status filter. |

## Business Rules

1. Each application represents one batch containing 1–100 simulated RECs and can produce at most one certificate record. Each REC corresponds to 1 MWh, so `quantity` also states the batch's total MWh.
2. The generation period must satisfy `periodStart < periodEnd <= block.timestamp`; `batchIndex` and `quantity` must be positive, and `quantity` cannot exceed 100.
3. A batch is identified by the chain, submitting wallet address, normalised site code, generation period and batch index. Its key is permanently reserved when the application is submitted.
4. Rejected and withdrawn applications remain visible in history. Editing or resubmitting the same batch key is not supported.
5. Only pending applications may be approved, rejected or withdrawn.
6. Only the current owner may list a certificate. A listing requires an active certificate and a positive price.
7. A purchase requires a wallet other than the seller, an active listing and exact payment at the purchaser's expected price. A changed price causes the transaction to revert.
8. A purchased certificate batch may be held or retired. Purchase and retirement always apply to its complete quantity; it cannot be resold, split or partially retired.
9. Retirement is permanent. The owner and historical records remain available after retirement.
10. The Admin has no arbitrary ownership transfer, balance withdrawal or retirement reversal function.

The batch key prevents an exact duplicate submission under the same identifiers. It cannot detect fabricated generation, overlapping batches, changed batch indices or site identifiers, submissions from other wallets or registration in external systems. The Admin must confirm that the evidence supports the declared quantity and that it has not already been accepted in another batch.

Evidence-integrity checks establish that the locally available file and metadata match their stored and on-chain hashes. They do not independently establish that the claimed energy was generated. Raw evidence downloads remain limited to the uploading Producer and Admin.

## Coursework Coverage

| Area | Planned evidence |
|---|---|
| Problem and business context | Research, user scenarios, role definitions and an explanation of why a shared certificate record is useful. |
| Blockchain design | Three interacting contracts, explicit permissions, immutable metadata references and lifecycle events. |
| Transaction functionality | Eleven distinct user transaction types, documented in the contract specification. |
| Application development | Flask endpoints, SQLite storage, wallet integration and responsive pages. |
| Deployment | A public application URL, testnet contract addresses, deployment configuration and transaction receipts. |
| Evaluation | Functional tests, failure cases, measured gas use and usability observations. |
| Submission | Report, source repository, contribution records, user instructions and presentation materials. |

The submission checklist should be checked against the final assignment brief before delivery. A mobile-first web application is the implementation target; an Android or iOS package is outside the current scope.

## Scope Limits

The project excludes secondary trading, fungible token payments, NFT standards, lending, carbon accounting, live meter integration, automated accreditation, oracles and complex scaling infrastructure. Basic permission checks, consistent accounting and recoverable storage remain required for a working application.
