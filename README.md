# GreenCert

GreenCert is a coursework prototype for issuing, trading and retiring simulated renewable energy certificate (REC) batches on the Sepolia testnet. One REC represents one MWh in this prototype. The application uses test ETH and does not issue accredited certificates.

## Live deployment

Open the public application at [https://greencert.onrender.com](https://greencert.onrender.com).

| Contract | Sepolia address |
| --- | --- |
| `RoleRegistry` | [`0xc6ddfdef0eef7b9d2bb6df9e60bf439a2725a369`](https://sepolia.etherscan.io/address/0xc6ddfdef0eef7b9d2bb6df9e60bf439a2725a369) |
| `CertificateRegistry` | [`0x338c972fcab0892448fa0ee939f3330fb42f6c04`](https://sepolia.etherscan.io/address/0x338c972fcab0892448fa0ee939f3330fb42f6c04) |
| `CertificateMarket` | [`0xd7f2b6c233e7044ab4a76317b834c58c2ff23f01`](https://sepolia.etherscan.io/address/0xd7f2b6c233e7044ab4a76317b834c58c2ff23f01) |

Certificate ownership, listings, purchases and retirements are stored on Sepolia. The free Render deployment uses local service storage for uploaded evidence and SQLite records; those local records can be cleared when the service restarts or is redeployed.

## Documentation

| Document | Description |
| --- | --- |
| [User manual](docs/user-manual.md) | Wallet connection and the Producer, Admin, Buyer and public-audit workflows. |
| [Product and requirements](docs/development/01-product.md) | Scope, roles, business rules and requirements. |
| [Architecture and workflow](docs/development/02-architecture-flow.md) | Application components, state flow and transaction sequence. |
| [Smart contracts](docs/development/03-contracts.md) | Contract responsibilities, permissions, functions and events. |
| [API](docs/development/04-api.md) | Flask API endpoints and request/response behaviour. |
| [Data model](docs/development/05-data-model.md) | SQLite records, uploaded evidence and on-chain references. |
| [Responsive interface](docs/development/06-ui.md) | Pages, navigation, dashboard content and interaction states. |
| [Testing plan](docs/development/08-testing.md) | Automated and Sepolia workflow checks. |
| [Test results](docs/evidence/test-results.md) | Recorded local, Remix and Sepolia results. |
| [Gas measurements](docs/evidence/gas-results.csv) | Mined transaction receipts, gas used and transaction cost. |
| [Sepolia workflow](tests/manual/sepolia-checklist.md) | Completed on-chain workflow and expected state checks. |
| [Automated Sepolia run](tests/manual/sepolia-automated-run.md) | Test-wallet setup and resumable workflow runner. |

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

For a fresh deployment, deploy `RoleRegistry` with the Admin wallet address, deploy `CertificateRegistry` with the role registry address, then deploy `CertificateMarket` with both registry addresses. The Admin must call `CertificateRegistry.setMarket` once. Register separate Producer and Buyer wallets in the Account page.

## Tests

Run the local checks from the repository root:

```powershell
python -m unittest discover -s . -p "test_*.py" -v
npm run test:contracts:compile
npm run test:frontend
```

Run the Solidity test functions in `tests/contracts` using Remix Solidity Unit Testing. The local Solidity command checks compilation only; it does not execute the Remix test functions.

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
docs/                  Product, technical, testing and user documentation
deployment.json        Sepolia contract addresses and compiler settings
render.yaml            Render deployment configuration
```
