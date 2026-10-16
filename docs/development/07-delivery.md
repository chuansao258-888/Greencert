# Implementation and Delivery

## Project Structure

```text
greencert/
  README.md
  app.py
  config.py
  backend/
    __init__.py
    auth.py
    chain.py
    content.py
    db.py
    schema.sql
    routes/
      __init__.py
      api_auth.py
      api_content.py
      api_files.py
      api_records.py
      api_transactions.py
      pages.py
  contracts/
    RoleRegistry.sol
    CertificateRegistry.sol
    CertificateMarket.sol
    interfaces/
      IRoleRegistry.sol
      ICertificateRegistry.sol
  templates/
    base.html
    dashboard.html
    market.html
    certificate_detail.html
    applications.html
    my_certificates.html
    activity.html
    account.html
  static/
    css/
      app.css
    js/
      api.js
      app.js
      contracts.js
      pages.js
      transactions.js
      wallet.js
    contracts/
      RoleRegistry.json
      CertificateRegistry.json
      CertificateMarket.json
  tests/
    frontend/
      dashboard.test.cjs
    contracts/
      TestActors.sol
      RoleRegistry_test.sol
      CertificateRegistry_test.sol
      CertificateMarket_test.sol
    backend/
      __init__.py
      base.py
      test_auth.py
      test_content.py
      test_files.py
      test_records.py
      test_transactions.py
    manual/
      mobile-checklist.md
      sepolia-checklist.md
  scripts/
    compile.cjs
    check_contract_tests.cjs
    init_db.py
    export_abi.py
    backup_data.py
  instance/                 # Local database and evidence; ignored by Git
    uploads/
  docs/
    development/
    evidence/
      README.md
      gas-results.csv
      test-results.md
  deployment.json
  requirements.txt
  requirements-dev.txt
  .env.example
  .gitignore
```

This layout is fixed for the first implementation. Do not add service layers, a JavaScript build system or separate applications unless the documented design can no longer be implemented clearly with these files.

## File Responsibilities

| File or group | Responsibility |
|---|---|
| `README.md` | Setup, configuration, run, test and deployment instructions. |
| `app.py` | Create the Flask application, register route blueprints and expose the application entry point. |
| `config.py` | Read and validate environment variables; contain no secrets or environment-specific values in source. |
| `backend/__init__.py` | Define the backend package and shared blueprint registration. |
| `backend/auth.py` | Create challenges, recover signed addresses, consume nonces and manage sessions and CSRF checks. |
| `backend/chain.py` | Load deployments and ABIs; perform contract reads, event queries and transaction receipt verification. |
| `backend/content.py` | Validate content payloads, create canonical JSON and calculate metadata hashes. |
| `backend/db.py` | Open SQLite connections, enable foreign keys and provide transaction helpers. |
| `backend/schema.sql` | Create the versioned initial tables and indexes described in the data model. |
| `backend/routes/__init__.py` | Export and register the route blueprints. |
| `backend/routes/api_auth.py` | `/auth/challenge`, `/auth/verify`, `/auth/me` and `/auth/logout`. |
| `backend/routes/api_content.py` | Create and read immutable application, rejection and retirement content. |
| `backend/routes/api_files.py` | Upload, validate and authorise evidence-file downloads. |
| `backend/routes/api_records.py` | Configuration, applications, certificates, dashboard, wallet and event read endpoints. |
| `backend/routes/api_transactions.py` | Verify transaction hashes and return personal transaction records. |
| `backend/routes/pages.py` | Render the application pages. |
| `contracts/RoleRegistry.sol` | Immutable Admin and one-time Producer or Buyer registration. |
| `contracts/CertificateRegistry.sol` | Application review, certificate ownership and retirement. |
| `contracts/CertificateMarket.sol` | Listings, exact-price purchases, seller credits and withdrawals. |
| `contracts/interfaces/IRoleRegistry.sol` | Minimum role queries required by the other contracts. |
| `contracts/interfaces/ICertificateRegistry.sol` | Minimum listing and sale hooks required by the market. |
| `templates/base.html` | Shared document structure, status banner and responsive navigation. |
| `templates/dashboard.html` | Public certificate totals, source/status charts and workflow overview. |
| `templates/market.html` | Active whole-batch listings. |
| `templates/certificate_detail.html` | Certificate metadata, ownership and event history. |
| `templates/applications.html` | Producer application form and Admin review queue. |
| `templates/my_certificates.html` | Producer and Buyer holdings with permitted actions. |
| `templates/activity.html` | Personal verified transactions. |
| `templates/account.html` | Wallet, network, role registration, session and proceeds. |
| `static/css/app.css` | All responsive layout, component and accessibility styles. |
| `static/js/api.js` | Same-origin API client, error parsing and CSRF header handling. |
| `static/js/app.js` | Shared page initialisation, notices and common formatting. |
| `static/js/contracts.js` | ABI loading, deployed contract instances and read helpers. |
| `static/js/pages.js` | Page-specific form binding and rendering for this small application. |
| `static/js/transactions.js` | Wallet submission, receipt waiting and backend verification state. |
| `static/js/wallet.js` | MetaMask connection, signer and network switching. |
| `static/contracts/*.json` | Compiled ABI only; no bytecode is required by the browser. |
| `tests/contracts/*.sol` | Remix Solidity unit tests and small actor/helper contracts. |
| `tests/backend/*.py` | Python `unittest` API and service tests using temporary storage. |
| `tests/frontend/*.cjs` | Small Node.js checks for dashboard rendering. |
| `tests/manual/*.md` | Repeatable mobile-wallet and Sepolia acceptance checklists. |
| `scripts/init_db.py` | Initialise or validate the SQLite schema without deleting existing data. |
| `scripts/compile.cjs` | Compile the application contracts and produce local artifacts. |
| `scripts/check_contract_tests.cjs` | Compile Solidity tests before they are run in Remix. |
| `scripts/export_abi.py` | Copy only the three contract ABIs into `static/contracts`. |
| `scripts/backup_data.py` | Use SQLite backup and copy uploads into a named backup directory. |
| `instance/` | Runtime database and uploads; never committed. |
| `docs/evidence/README.md` | Explain evidence naming and distinguish planned from completed results. |
| `docs/evidence/gas-results.csv` | Receipt measurements entered after Sepolia checks. |
| `docs/evidence/test-results.md` | Test run commands, environment, results and links to supporting evidence. |
| `deployment.json` | Chain, addresses, deployment blocks, compiler and optimizer settings. |
| `requirements.txt` | Runtime Python packages with compatible pinned versions. |
| `requirements-dev.txt` | Test-only Python packages, if any; keep `unittest` in the standard library. |
| `.env.example` | Safe variable names and non-secret examples. |
| `.gitignore` | Ignore `.env`, caches, local databases, uploads, backups and generated artifacts. |

## Implementation Milestones

| Milestone | Work | Completion condition |
|---|---|---|
| P1: Foundation | Confirm requirement mapping; create Flask structure, database, responsive navigation, wallet connection and roles. | Application starts; roles are read from the deployed role contract; protected actions enforce the role. |
| P2: Issuance | Implement evidence upload, canonical content, batch quantity, applications, withdrawal and Admin review. | A Producer can obtain a certificate record with an immutable quantity; rejected and withdrawn applications remain traceable. |
| P3: Market | Implement whole-batch listing, repricing, cancellation, purchase, credit withdrawal and retirement. | Quantity, ownership, listing status and seller balances remain consistent through the full workflow. |
| P4: Evaluation | Add dashboard, history, receipt verification, functional tests and gas measurements. | All eleven transaction types and critical failure cases have recorded results. |
| P5: Deployment | Deploy contracts and hosted application; configure persistent storage; exercise mobile workflows. | Public URL works, stored evidence survives a restart, and mobile wallet actions complete. |
| P6: Submission | Prepare report, user guide, contribution records, slides and demonstration evidence. | Submission materials match the implemented and verified behaviour. |

Complete each core workflow before adding visual polish. Deferred features should remain outside the implementation unless a coursework requirement makes them necessary.

## Testing

The complete test tools, named files, case ownership, commands and evidence format are defined in the [Testing Plan](08-testing.md). Contract tests use Remix Solidity Unit Testing so the contract workflow stays close to the taught toolchain. Backend tests use Python's built-in `unittest`. Wallet and responsive behaviour use repeatable manual checklists because MetaMask approval cannot be represented faithfully by a Flask unit test.

## Gas and Performance Evaluation

Collect transaction hashes, `gasUsed` and effective gas price for all eleven user transaction types. Calculate actual transaction cost as `gasUsed * effectiveGasPrice`. Distinguish gas estimates from mined receipt measurements.

For a focused comparison, use a separate test fixture to compare full on-chain descriptive strings with a bytes32 metadata reference. Keep the business operation, input content, compiler, optimizer settings and network consistent. Explain that off-chain metadata reduces chain storage but introduces hosting and availability dependencies.

Measure response latency for representative reads, such as the market page and certificate details, on a small documented dataset. Report the sample size and environment. A coursework demonstration does not establish production-scale throughput.

## Deployment Configuration

| Variable | Purpose |
|---|---|
| APP_ORIGIN | Public HTTPS origin used for authentication and origin checks. |
| SECRET_KEY | Random server secret, supplied through the host's environment configuration. |
| RPC_URL | Sepolia RPC endpoint; keep provider credentials on the server. |
| CHAIN_ID | Expected chain ID, 11155111. |
| DATABASE_PATH | SQLite file on persistent storage. |
| UPLOAD_DIR | Evidence directory on persistent storage. |
| DEPLOYMENT_FILE | Path to contract addresses, deployment blocks and compilation settings. |
| COOKIE_SECURE | Enabled for the deployed HTTPS application. |

`deployment.json` contains the network, three contract addresses, deployment blocks, compiler version, EVM target and optimizer settings. Export matching ABIs for the server and frontend. Never store wallet private keys in application configuration or the repository.

Use one Flask application worker for the initial deployment. On Render, place SQLite and uploads under the mounted persistent path, such as `/var/data`. Verify the selected hosting plan supports persistent storage and confirm its cost before provisioning. Do not rely on an ephemeral filesystem for submitted evidence.

## Deployment Checks

1. Compile and test the contracts using the recorded settings.
2. Deploy the three contracts and complete the one-time market binding.
3. Save addresses, ABIs, deployment blocks and transaction receipts.
4. Configure the application origin, RPC access, cookie settings and persistent paths.
5. Initialise the schema without deleting existing data.
6. Exercise multi-unit batch issuance, whole-batch purchase, withdrawal and whole-batch retirement using separate role wallets.
7. Restart the server and recheck the stored files and records.
8. Open the public site in a real mobile wallet browser and repeat the main user actions.

Back up the database with the SQLite backup API and preserve uploads and deployment configuration. To roll back application code, retain compatible data and contract references. Contracts are not upgradeable; a replacement deployment must be explicit and documented rather than silently switching users to new addresses.

## Submission Checklist

- [ ] A 10-15 page report covering the problem, requirements, architecture, implementation, evaluation and limitations.
- [ ] Architecture diagram, workflow diagrams, state transitions and data relationships consistent with the application.
- [ ] Source repository with setup instructions and genuine contribution records.
- [ ] Public application URL and three testnet contract addresses.
- [ ] Evidence for all eleven transaction types, including receipts and measured gas use.
- [ ] Functional test results and representative failure cases.
- [ ] Screenshots and observations from mobile wallet testing.
- [ ] User instructions for Producer, Buyer and Admin.
- [ ] Presentation slides and a ten-minute demonstration.
- [ ] A final check against the assignment brief and submission instructions.

## Demonstration Outline

Introduce the problem and the three roles, then show a Producer application for several simulated RECs and Admin approval. List the complete batch at a total price, purchase it from a Buyer wallet, and withdraw the seller's proceeds. Retire the complete purchased batch and inspect its quantity and history. Finish with the dashboard, gas results and the limitations of manual evidence review.

Prepare role wallets and test ETH before the demonstration. Keep recorded receipts available if a live network request is slow. Describe every result according to the evidence collected; planned features remain identified as incomplete until verified.
