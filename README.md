# GreenCert

GreenCert is a coursework prototype for issuing, trading and retiring simulated renewable energy certificate (REC) batches on the Sepolia testnet. One REC represents one MWh in this prototype. The application uses test ETH and does not issue accredited certificates.

## Live deployment

Open the public application at [https://greencert.onrender.com](https://greencert.onrender.com).

| Contract | Sepolia address |
| --- | --- |
| `RoleRegistry` | [`0x628a94ff69e5bb527ce8b6dbbc1f480458af9d02`](https://sepolia.etherscan.io/address/0x628a94ff69e5bb527ce8b6dbbc1f480458af9d02) |
| `CertificateRegistry` | [`0xa3456442711ead1110d6f93e0c56b35ab25bebc9`](https://sepolia.etherscan.io/address/0xa3456442711ead1110d6f93e0c56b35ab25bebc9) |
| `CertificateMarket` | [`0x84990af8d7ca3224df64305d1330c50e21c887aa`](https://sepolia.etherscan.io/address/0x84990af8d7ca3224df64305d1330c50e21c887aa) |

Certificate ownership, listings, purchases and retirements are stored on Sepolia. The free Render deployment uses local service storage for uploaded evidence and SQLite records; those local records can be cleared when the service restarts or is redeployed.

## Coursework materials

Submission materials and supporting evidence are collected in [submission/](submission/). Test source files remain in [tests/](tests/) so the test commands continue to work.

| Material | Links |
| --- | --- |
| Course requirements and status | [Requirements checklist](docs/submission-checklist.md) |
| Problem and evaluation | [Problem and evaluation evidence](submission/evaluation/problem-evaluation.md) |
| Architecture, contract interaction and process flow | [Architecture and workflow](docs/development/02-architecture-flow.md), [smart contracts](docs/development/03-contracts.md) |
| Data model and UI diagrams | [Data model](docs/development/05-data-model.md), [responsive interface](docs/development/06-ui.md) |
| Source, setup and documentation | [Source and repository layout](#repository-layout), [setup](#local-setup), [API](docs/development/04-api.md), [product and requirements](docs/development/01-product.md) |
| Deployment and contract details | [Public application](https://greencert.onrender.com), [deployment record](docs/development/09-registration-deployment.md), [deployment.json](deployment.json) |
| Testing report and evidence | [Test results](submission/testing/test-results.md), [local contract test output](submission/testing/contract-test-local.txt), [test source](tests/), [testing plan](docs/development/08-testing.md), [Sepolia checklist](tests/manual/sepolia-checklist.md), [automated Sepolia run](tests/manual/sepolia-automated-run.md) |
| Gas estimation and optimization | [Gas analysis](submission/gas/gas-analysis.md), [receipt measurements](submission/gas/gas-results.csv) |
| User manual | [User manual](docs/user-manual.md) |
| Presentation and video | [Demonstration video](https://www.youtube.com/watch?v=dHrIokU-WzI&t=2s)|


The complete lifecycle receipt and gas evidence is from the earlier Sepolia deployment; see the reports for its addresses and the limits of current-deployment verification.

## Local setup

Requirements: Python, Node.js, MetaMask and a Sepolia RPC endpoint.

```powershell
python -m pip install -r requirements.txt
npm ci
npm run compile
python scripts/export_abi.py
python scripts/init_db.py
python app.py
```

Open `http://127.0.0.1:5000`. Copy `.env.example` to `.env` and set `RPC_URL` to a Sepolia endpoint. `deployment.json` contains the deployed contract addresses and their deployment blocks.

For a fresh deployment, deploy `RoleRegistry` with the Admin wallet address, deploy `CertificateRegistry` with the role registry address, then deploy `CertificateMarket` with both registry addresses. The Admin must call `CertificateRegistry.setMarket` once. A registered Producer, Buyer or Admin can submit applications, list an owned certificate, purchase a listing and retire an owned unlisted certificate. Only the Admin can approve or reject applications.

## Tests

After signing in, unregistered wallets are prompted to register on-chain as Producer or Buyer. Registration is required for application and trading actions. Both roles share ordinary business permissions; Admin alone grants approval and rejection authority. The account page displays the role read from the chain.

The deployed Registry and Market require a registered on-chain role for ordinary state-changing operations. See [deployment verification](docs/development/09-registration-deployment.md).

Run the local checks from the repository root:

```powershell
python -m unittest discover -s . -p "test_*.py" -v
npm run test:contracts:compile
npm run test:frontend
```

The local Solidity compilation command does not execute tests. The current test functions have also been executed on an isolated local EVM; see [test results](submission/testing/test-results.md) for the commands, versions and limitations. Remix execution of the revised tests has not been recorded.

For the deployed Sepolia contracts, run:

```powershell
python scripts/sepolia_e2e.py check
```

The signed workflow is documented in [Automated Sepolia run](tests/manual/sepolia-automated-run.md). It uses dedicated test wallets configured only in the ignored `.sepolia-test.env` file. Never commit or share private keys.

## Repository layout

```text
app.py                 Flask application factory
backend/               API routes, authentication, chain reads and SQLite access
contracts/             Solidity contracts and interfaces
static/                Browser JavaScript, CSS and contract ABIs
templates/             HTML pages
tests/                 Backend, frontend, contract and Sepolia workflow tests
submission/            Test and gas evidence, evaluation and presentation information
docs/                  Product, technical, testing and user documentation
deployment.json        Sepolia contract addresses and compiler settings
render.yaml            Render deployment configuration
```
