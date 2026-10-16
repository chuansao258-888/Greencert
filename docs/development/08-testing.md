# Testing Plan

## Testing Approach

Testing demonstrates that the required workflows operate correctly. It is not intended to model every unusual wallet, network or adversarial condition.

Use three test levels:

| Level | Tool | Purpose |
|---|---|---|
| Contract tests | Remix Solidity Unit Testing | Verify the main role, issuance, market, payment and retirement rules. |
| Backend tests | Python `unittest` with Flask's test client | Verify the main API, authentication, evidence and transaction-verification functions. |
| Manual acceptance | MetaMask, Sepolia and a mobile browser | Verify the complete user journey with real wallet prompts and transaction receipts. |

The target is 14 automated tests and three manual checklists. This is enough to demonstrate functional completeness without turning the coursework into a security-testing project.

## Test Files

| File | Contents |
|---|---|
| `tests/contracts/TestActors.sol` | Simple caller contracts representing Producer and Buyer addresses where the Remix test needs distinct senders. |
| `tests/contracts/RoleRegistry_test.sol` | Two role tests. |
| `tests/contracts/CertificateRegistry_test.sol` | Four application, review and retirement tests. |
| `tests/contracts/CertificateMarket_test.sol` | Three listing, purchase and withdrawal tests. |
| `tests/backend/__init__.py` | Backend test package marker. |
| `tests/backend/base.py` | Temporary database, upload directory, sample addresses and a small deterministic chain stub. |
| `tests/backend/test_auth.py` | Wallet authentication test. |
| `tests/backend/test_content.py` | Evidence and immutable-content test. |
| `tests/backend/test_files.py` | Evidence upload and retrieval test. |
| `tests/backend/test_records.py` | Application, certificate and dashboard read test. |
| `tests/backend/test_transactions.py` | Transaction receipt verification test. |
| `tests/manual/mobile-checklist.md` | Responsive layout and mobile MetaMask workflow. |
| `tests/manual/sepolia-checklist.md` | Contract deployment and all eleven user transaction types. |

## Contract Tests

### RoleRegistry_test.sol

| ID | Test | Expected result |
|---|---|---|
| C01 | `test_registers_producer_and_buyer` | Two unregistered addresses receive their selected roles and emit registration events. |
| C02 | `test_rejects_unauthorised_role_change` | Admin self-registration and changing an existing role fail. |

### CertificateRegistry_test.sol

| ID | Test | Expected result |
|---|---|---|
| C03 | `test_producer_submits_batch_application` | A valid application stores its site, period, batch index, quantity, metadata hash and Pending status. |
| C04 | `test_application_can_be_withdrawn_or_rejected` | A Producer can withdraw one pending application and the Admin can reject another with a reason. |
| C05 | `test_admin_approval_issues_certificate_batch` | Approval creates one Active certificate with the same Producer, metadata hash and quantity. Repeating the review fails. |
| C06 | `test_buyer_retires_owned_certificate_batch` | The Buyer owner retires the complete purchased batch; quantity and retirement information remain readable. |

### CertificateMarket_test.sol

| ID | Test | Expected result |
|---|---|---|
| C07 | `test_producer_lists_updates_and_cancels_listing` | The Producer can list the complete batch, change its total price and cancel the listing. |
| C08 | `test_buyer_purchases_complete_batch` | Exact payment closes the listing, transfers the unchanged quantity and credits the seller. Wrong payment or a repeated purchase fails. |
| C09 | `test_seller_withdraws_sale_proceeds` | The seller receives the credited amount and the credit becomes zero. |

These tests cover the main success paths and a few directly related failures. Dedicated tests for reentrancy actors, forced ETH, fuzzing, blockchain reorganisations and large-volume concurrency are outside this coursework scope.

## Backend Tests

| ID | File and test | Expected result |
|---|---|---|
| B01 | `test_auth.py::test_wallet_sign_in_and_logout` | A valid signed challenge creates a session; logout removes access. |
| B02 | `test_content.py::test_application_content_and_hash` | Valid application data is normalised, includes quantity, produces stable canonical JSON and matches its metadata hash. |
| B03 | `test_files.py::test_evidence_upload_and_authorised_download` | A supported file is stored and can be downloaded by its Producer or the Admin. |
| B04 | `test_records.py::test_application_certificate_and_dashboard_reads` | The API returns application status, certificate quantity, listing information and dashboard totals from the chain stub. |
| B05 | `test_transactions.py::test_confirmed_transaction_verification` | A successful receipt from a configured contract is decoded and stored against the authenticated sender. |

The backend tests use temporary files and a temporary SQLite database. They do not call a public RPC service or write to the normal `instance/` directory.

## Sepolia Functional Checklist

Record one complete run in `tests/manual/sepolia-checklist.md`:

1. Deploy RoleRegistry, CertificateRegistry and CertificateMarket and bind the market.
2. Register a Producer and Buyer.
3. Submit and withdraw one batch application.
4. Submit and reject one batch application.
5. Submit and approve a multi-unit batch application.
6. List the certificate batch, update its total price and cancel the listing.
7. List it again and purchase it from the Buyer wallet.
8. Withdraw the seller's proceeds.
9. Retire the complete batch.
10. Open the certificate history and verify the final owner, unchanged quantity, Retired status and transaction links.

This checklist exercises all eleven user transaction types. Record the transaction hash, receipt status and `gasUsed` for each successful transaction.

## Mobile Functional Checklist

Run the Producer, Admin and Buyer journey in MetaMask's mobile browser. Confirm that:

- the main pages fit at 360 and 390 pixels without horizontal scrolling;
- wallet connection, network switching and transaction prompts work;
- application, review, market, purchase and retirement controls are usable by touch;
- the quantity and total price remain visible before purchase and retirement;
- a rejected wallet prompt returns the page to a usable state;
- confirmed results remain correct after a page refresh.

Desktop checks at 768 and 1280 pixels confirm the responsive layout, but they do not replace the mobile-wallet run.

## Persistence Check

After the Sepolia workflow, restart the hosted Flask application and verify that:

- the SQLite database opens successfully;
- the uploaded evidence file remains available to the authorised accounts;
- immutable metadata still matches its stored hash;
- the application reads the same certificate state from Sepolia.

## Running the Tests

Run the nine contract tests through Remix Solidity Unit Testing:

1. Compile the contracts, interfaces, `TestActors.sol` and the three `_test.sol` files with the deployment compiler settings.
2. Select `tests/contracts` in the Solidity Unit Testing plugin.
3. Run all tests in the Remix VM and copy the result summary to `docs/evidence/test-results.md`.

Run the five backend tests from the repository root:

```powershell
python -m unittest discover -s tests/backend -p "test_*.py" -v
```

Start the application for the manual checks:

```powershell
python scripts/init_db.py
python app.py
```

These are implementation targets. They are not evidence that tests currently pass.

## Completion Criteria

Testing is complete when:

- all nine contract tests and five backend tests pass;
- the Sepolia checklist demonstrates all eleven user transaction types;
- the mobile checklist completes the main Producer, Admin and Buyer journey;
- the persistence check succeeds after an application restart;
- `docs/evidence/test-results.md` records the commands, environment and observed results;
- `docs/evidence/gas-results.csv` contains receipt measurements for the successful transactions.

Use this CSV header:

```csv
transaction_type,tx_hash,block_number,gas_used,effective_gas_price_wei,cost_wei,result
```

Do not mark a planned test as passed until its output or transaction receipt has been saved.
