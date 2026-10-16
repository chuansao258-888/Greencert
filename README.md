# GreenCert

GreenCert is a mobile-first coursework prototype for issuing, trading and retiring batches of simulated renewable energy certificates on Sepolia.

## Local setup

```powershell
python -m pip install -r requirements.txt
npm ci
npm run compile
python scripts/export_abi.py
python scripts/init_db.py
python app.py
```

Open `http://127.0.0.1:5000`. Copy `.env.example` to `.env`, set `RPC_URL` to a Sepolia endpoint, and enter the three deployed contract addresses and their deployment block numbers in `deployment.json`. The site shows its pages before deployment, but wallet actions and chain reads require those settings.

Deploy `RoleRegistry` with the Admin wallet address, `CertificateRegistry` with the role registry address, and `CertificateMarket` with both registry addresses. Call `CertificateRegistry.setMarket` once from the Admin wallet. Register separate Producer and Buyer wallets on the account page. All trades use Sepolia test ETH. A listing's quantity is fixed at issuance; the price and purchase cover the full batch.

Run local checks with:

```powershell
python -m unittest discover -s . -p "test_*.py" -v
npm run test:contracts:compile
npm run test:frontend
```

Run the Solidity test functions in `tests/contracts` with Remix Solidity Unit Testing. The local contract check compiles the tests but does not execute them. The mobile and Sepolia steps are listed in `tests/manual`.

For the already deployed Sepolia contracts, `python scripts/sepolia_e2e.py check` reads the current on-chain state. The signed, resumable real-chain workflow is documented in [`tests/manual/sepolia-automated-run.md`](tests/manual/sepolia-automated-run.md); it requires dedicated test-wallet keys configured only in the ignored `.sepolia-test.env` file.

This coursework prototype uses simulated certificate records and test ETH; it does not issue accredited certificates. The deployment file has empty addresses until the contracts are deployed.
