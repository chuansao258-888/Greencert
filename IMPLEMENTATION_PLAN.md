# GreenCert Implementation Plan

Build a mobile-first application for simulated renewable energy certificate issuance, trading and retirement. Prioritise complete role workflows, consistent contract state and a clear demonstration.

Status: specification complete; application implementation, testing and deployment pending.

## Technology Stack

Solidity and Remix; HTML, CSS and JavaScript with ethers.js and MetaMask; Python Flask and SQLite; Sepolia test ETH; Render with persistent storage for the database and evidence files.

## Milestones

| Phase | Work | Completion condition |
|---|---|---|
| 1 | Requirements, application structure, database, mobile navigation, wallet connection and roles. | The application runs and role-based access works. |
| 2 | Evidence upload, immutable metadata, applications, withdrawal and review. | A Producer can submit evidence and receive an approved certificate. |
| 3 | Listings, repricing, cancellation, purchase, withdrawal and retirement. | The complete certificate and payment workflow is consistent. |
| 4 | Dashboard, history, receipt verification, gas measurements and tests. | Eleven transaction types and critical failure cases have evidence. |
| 5 | Testnet and public hosting deployment, persistence checks and mobile testing. | The public URL works and complete workflows pass on a mobile wallet browser. |
| 6 | Report, user guide, contribution records, slides and demonstration. | Deliverables reflect the implemented application and satisfy the submission checklist. |

## Scope

Three roles and three interacting contracts. Each certificate record represents a batch of 1–100 simulated RECs, with each REC corresponding to 1 MWh. A batch has one fixed total price and must be purchased and retired as a whole. Secondary markets, batch splitting, NFT standards, carbon calculations, live meters and automated accreditation are outside the scope.

The complete directory, every planned source filename and its responsibility are fixed in [Implementation and Delivery](docs/development/07-delivery.md). Test files, cases, commands and evidence are defined in the [Testing Plan](docs/development/08-testing.md). Record actual test and deployment results during implementation. Confirm persistent hosting availability and cost before provisioning.
