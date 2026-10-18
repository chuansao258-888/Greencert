# Automated Sepolia workflow

`scripts/sepolia_e2e.py` records the completed workflow against the existing Sepolia deployment from active listing #1. It sends real signed transactions in this order: reprice, cancel, relist, buy, withdraw proceeds, retire, submit and withdraw a test application, then submit and reject another test application. After **each** transaction, it checks the receipt status, direct target and sender, expected contract event, and resulting contract storage. A failed check stops the run. The ten transactions use Sepolia test ETH.

The addresses currently in `deployment.json` are the earlier open-wallet Registry and Market. Do not use this runner as evidence for the newer Solidity registration guards until its configuration and expected state are updated for replacement deployments. The required deployment and validation sequence is in `docs/development/09-registration-deployment.md`.

The script signs with the three existing **test-only** wallets. Copy `.sepolia-test.env.example` to `.sepolia-test.env`, then enter the corresponding private keys locally. Never paste the keys in chat, commit them, or use a wallet holding real funds. `.sepolia-test.env` and `instance/sepolia-e2e-state.json` are ignored by Git. The script verifies that every key derives the configured address, checks chain ID `11155111` and deployed contract bindings, and enforces gas-price and per-transaction cost caps before broadcasting. The default caps are 5 gwei and 0.01 SepoliaETH; change them only after reviewing current network conditions and the expected cost.

From the repository root:

```powershell
python scripts/sepolia_e2e.py check
python scripts/sepolia_e2e.py preflight
python scripts/sepolia_e2e.py run
```

`check` only reads public chain state and needs no private keys. `preflight` validates the wallets, roles, balances, price cap, and the next action without broadcasting. `run` signs and sends the remaining steps. Transaction hashes and completion flags are saved in `instance/sepolia-e2e-state.json` before the next step. If the process stops, run the same command again; it resumes from the first unverified transaction rather than deliberately sending it again. If a broadcast is uncertain and its hash is not found, investigate that hash before retrying. The script appends successful receipt measurements to `docs/evidence/gas-results.csv`.

The two additional applications use distinct on-chain test hashes. They exercise contract withdrawal and rejection; they do not upload new evidence through the website. The retirement also uses a chain-only test hash, so its statement is not stored as website content. At the end, the script verifies that the approved certificate #1 still has matching metadata and a SHA-256-valid evidence file in the local application database. It also creates a fresh Flask instance, authenticates Admin and downloads that evidence through the API. Browser layout and MetaMask prompts remain separate manual checks.
