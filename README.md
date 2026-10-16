# GreenCert

GreenCert is a mobile-first coursework prototype for issuing, trading and retiring batches of simulated renewable energy certificates on Sepolia.

## Local setup

```powershell
python -m pip install -r requirements.txt
python scripts/init_db.py
python app.py
```

Open `http://127.0.0.1:5000`. Copy `.env.example` to `.env` before configuring an RPC endpoint or deployed contract addresses.

The current implementation is under development. The application uses test ETH only and does not issue accredited certificates.
