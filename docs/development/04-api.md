# API Design

Flask serves the pages and same-origin JSON endpoints under `/api`. MetaMask submits business transactions; the server reads contract state, stores supporting files and metadata, and checks submitted receipts. Successful JSON responses use `{"data": ...}`; errors use `{"error":{"code":"...","message":"..."}}`. Contract IDs and wei amounts are decimal strings. Bytes32 hashes use `0x` plus 64 hexadecimal characters.

## Configuration and authentication

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Report whether RPC and all contract deployment settings are present. |
| GET | `/api/config` | Return chain ID, currency, addresses and configuration status. |
| POST | `/api/auth/challenge` | Create a five-minute signing message for `address`. |
| POST | `/api/auth/verify` | Check `address`, `nonce` and `signature`; set an eight-hour session cookie. |
| GET | `/api/auth/me` | Return the session wallet, current role, CSRF token and expiry. |
| POST | `/api/auth/logout` | Revoke the session and clear the cookie. |

The challenge message includes the origin, chain ID, wallet address, nonce and expiry. Signed requests use an HttpOnly, SameSite=Lax cookie. Authenticated writes also send `X-CSRF-Token`. The frontend connects MetaMask and signs in again after a page reload.

## Evidence and immutable content

| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/api/files` | Signed-in wallet | Upload multipart `file`; return `fileId`, SHA-256, size and media type. |
| GET | `/api/files/{fileId}` | Uploader or Admin | Download the original evidence. |
| POST | `/api/content` | Signed-in wallet; Admin for rejection | Store canonical application, rejection or retirement content. |
| GET | `/api/content/{contentHash}` | Public | Return the exact canonical JSON and hash. |

Evidence is limited to 5 MiB and PDF, PNG or JPEG file headers. The server generates stored filenames. Application payloads contain `siteCode`, `siteName`, `source`, `country`, `periodStart`, `periodEnd`, `batchIndex`, `quantity` and `proofFileId`. Quantity is an integer from 1 to 100; one REC represents 1 MWh in this simulation. The evidence file must belong to the signed-in wallet.

An Admin rejection payload contains `applicationId` and `reason`. A retirement payload contains `certificateId`, `beneficiary` and `purpose`. The server checks the relevant pending application or owned active certificate before preparing these content records; the contract rechecks state when the transaction executes.

For all kinds, the canonical envelope contains `schemaVersion`, `kind`, `chainId`, `targetContract`, `creator` and normalized `payload`. JSON keys are sorted and serialized without optional whitespace. `contentHash = keccak256(UTF8(canonicalJson))`. The browser checks the returned hash before sending it to the contract. An application payload stores the proof SHA-256 instead of its local file ID. The response also returns `chainArgs` for the matching contract method.

## Contract records

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/api/applications` | Signed-in wallet or Admin | List the wallet's applications or the Admin queue; optional `status`. |
| GET | `/api/applications/{id}` | Applicant or Admin | Return application state, metadata and evidence file ID. |
| GET | `/api/certificates` | Public | List certificates; optional `owner`, `status`, `listed=true`. |
| GET | `/api/certificates/{id}` | Public | Return certificate, listing, metadata and retirement statement. |
| GET | `/api/certificates/{id}/events` | Public | Return matching issue, market and retirement events. |
| GET | `/api/dashboard` | Public | Return issued, active, listed, sold and retired totals, total MWh and source chart data. |
| GET | `/api/wallet` | Signed-in wallet | Return role, ETH balance and claimable sale proceeds. |

Contract state is authoritative for quantity, status, ownership, price and proceeds. The backend joins on-chain metadata hashes to its saved content. Missing content is returned as `null`; the on-chain record remains visible. Event reads start at the configured deployment blocks and query at most 1,000 blocks per RPC request.

The dashboard response adds `totalMWh` as a decimal string and `sourceBreakdown` as an array in the order Solar, Wind, Hydro, Unknown. Each source entry has `source`, `quantityMWh` (decimal string) and `batches` (number). The source chart uses the immutable quantity of every issued certificate, including retired ones. If saved metadata is absent or has an unrecognized source, its quantity goes under Unknown rather than disappearing from the total. The status chart uses `active` and `retired`; a listed batch is still Active. The dashboard does not invent chart values before contract deployment.

## Transactions

| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/api/transactions/verify` | Signed-in wallet | Decode and save a submitted `txHash`. |
| GET | `/api/transactions` | Signed-in wallet | Return up to 50 saved transactions. |
| GET | `/api/transactions/{txHash}` | Transaction sender | Return one saved transaction. |

Verification checks the transaction sender, deployed target, allowed contract method, receipt status and a log from the target contract. For application, rejection and retirement calls, the content hash must resolve to a matching saved content kind, creator and target. Pending transactions receive HTTP 202; confirmed or failed receipts receive HTTP 200. The activity page displays saved hashes and gas used. This coursework version does not run a background indexer or claim chain finality.

Typical errors use HTTP 400 for malformed input, 401 for missing login, 403 for a wrong role or wallet, 404 for a missing record, 409 for an invalid lifecycle state, 413 for an oversized file, 415 for an unsupported file, 422 for a transaction/content mismatch and 503 when contract configuration or RPC access is unavailable.
