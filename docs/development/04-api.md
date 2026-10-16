# API Design

## Conventions

Flask serves same-origin endpoints under `/api`. Requests and responses use UTF-8 JSON unless an endpoint explicitly accepts a file. The server reads blockchain state and verifies receipts; MetaMask submits all business transactions.

Successful responses use `{"data": ...}`. Collections include `meta` with `nextCursor` and, for chain-derived results, `snapshotBlock`. Related contract reads use the same snapshot block where supported. A snapshot identifies when the data was read; it is not a guarantee of finality.

- Encode wei amounts, uint256 identifiers and block numbers as decimal strings. Chain IDs and small enum values may be JSON numbers.
- Return API timestamps in UTC ISO 8601 format. Contract arguments use Unix seconds represented as decimal strings.
- Validate addresses, store them in lowercase and return checksummed addresses for display.
- Represent bytes32 hashes as `0x` followed by 64 hexadecimal characters.
- Collection limits default to 20 and must not exceed 50. ID-based lists use descending IDs and an exclusive cursor. Apply filters before filling a page.
- Reject unknown fields on write requests. Bound user text and uploaded file sizes.

```json
{
  "error": {
    "code": "WRONG_ROLE",
    "message": "A Producer account is required."
  }
}
```

| HTTP status | Meaning |
|---|---|
| 400 | Invalid request or field format. |
| 401 | Missing or expired authenticated session. |
| 403 | Wrong role, ownership failure or invalid origin/CSRF token. |
| 404 | Record not found. |
| 409 | Conflicting state or consumed challenge. |
| 413 | File exceeds the size limit. |
| 415 | Unsupported file type. |
| 422 | Transaction or metadata does not match the expected chain record. |
| 503 | RPC or required storage is unavailable. |

Logs must not contain session cookies, signing secrets or authentication signatures.

## Configuration

| Method and path | Access | Result |
|---|---|---|
| `GET /health` | Public | Application health and database/configuration readiness; 503 if a required component is unavailable. |
| `GET /config` | Public | Chain ID, currency, contract addresses, deployment blocks, ABI URLs and explorer base URL. |

`/config` returns Sepolia chain ID `11155111` and currency `ETH`. It must not expose a private RPC credential, server secret or filesystem path.

## Wallet Authentication

| Method and path | Request | Result |
|---|---|---|
| `POST /auth/challenge` | `address` | `nonce`, exact signing `message`, `expiresAt`. |
| `POST /auth/verify` | `address`, `nonce`, `signature` | Set session cookie; return `address`, chain-derived `role`, `csrfToken`, `expiresAt`. |
| `GET /auth/me` | Session cookie | Current account, role, CSRF token and session expiry. |
| `POST /auth/logout` | Session cookie and CSRF header | Revoke session and clear cookie. |

The signing message binds the application origin, chain ID, address, nonce, issue time and expiry. A challenge expires after five minutes. Recover the signer from the stored message and consume the nonce atomically; a challenge cannot authenticate twice.

Sessions expire after eight hours. Store a hash of a random session token in SQLite. Use an HttpOnly, SameSite=Lax cookie and enable Secure on the deployed HTTPS site. Authenticated writes require a matching `Origin` and `X-CSRF-Token`. The frontend ends the session when the wallet account or network changes.

This is a small personal-sign authentication flow. An unregistered address may sign in to reach role registration, but it cannot use role-restricted endpoints. Registration itself occurs on-chain.

## Evidence Files

| Method and path | Access | Behaviour |
|---|---|---|
| `POST /files` | Producer, authenticated write | Multipart field `file`; return `fileId`, `sha256`, `size`, `mediaType`. |
| `GET /files/{fileId}` | Uploader or Admin | Download the evidence as an attachment. |

Accept PDF, PNG and JPEG files up to 5 MiB. Check actual file bytes as well as the declared MIME type. Generate storage names on the server; never use an uploaded filename as a path. HTML and SVG uploads are not accepted. Original filenames are display metadata only. Public certificate pages do not expose evidence files.

## Immutable Content

### POST /content

Authenticated write. Request fields: `kind` and `payload`. Return `contentHash`, the exact `canonicalJson` string and contract-ready `chainArgs`. A newly stored object returns 201; identical existing content returns 200.

| Kind | Role and state | Payload |
|---|---|---|
| `application` | Producer; evidence file belongs to caller. | `siteCode`, `siteName`, `source`, `country`, `periodStart`, `periodEnd`, `batchIndex`, `quantity`, `proofFileId` |
| `rejection` | Admin; referenced application is Pending. | `applicationId`, `reason` |
| `retirement` | Buyer owns referenced Active certificate. | `certificateId`, `beneficiary`, `purpose` |

Validation rules:

- Normalise `siteCode` to uppercase ASCII letters, digits and hyphens; length 1 to 40.
- Limit `siteName` to 80 characters and `beneficiary` to 100 characters.
- Limit `reason` and `purpose` to 500 characters. Required strings cannot be empty after trimming; reject control characters.
- `source` is `Solar`, `Wind` or `Hydro`. `country` is a two-letter uppercase country code.
- Validate the generation period, a positive uint32 `batchIndex` and an integer `quantity` from 1 to 100 before producing contract arguments.
- These checks improve the form workflow. Contracts recheck their own authoritative permissions and state when a transaction executes.

Canonical content uses the following envelope:

```text
{
  schemaVersion: 1,
  kind: application | rejection | retirement,
  chainId: configured chain ID,
  targetContract: lower-case registry address,
  creator: lower-case caller address,
  payload: normalised content
}
```

This is a schematic description, not a JSON request example. Before serialisation, replace `proofFileId` with the file's `proofSha256` and add `energyMWh` equal to the normalised quantity string. Convert IDs, quantity, batch index and generation timestamps to decimal strings. Sort object keys recursively and serialise compact UTF-8 JSON without ASCII escaping or optional whitespace.

Calculate `contentHash = keccak256(UTF8(canonicalJson))`. The frontend hashes the exact returned string and compares it with `contentHash`; it must not parse and reserialise it before hashing.

| Kind | Returned chainArgs |
|---|---|
| application | siteHash, periodStart, periodEnd, batchIndex, quantity, metadataHash |
| rejection | applicationId, reasonHash |
| retirement | certificateId, retirementHash |

### GET /content/{contentHash}

Public. Return the immutable envelope and exact canonical JSON. Do not return evidence download paths or session data. Use fictitious organisations and non-sensitive content in the demonstration because certificate metadata is public.

Metadata cannot be edited after creation. A corrected object has a different hash; it does not alter a previously submitted application. The initial version does not support replacing a submitted application's metadata.

## Application and Certificate Reads

| Method and path | Access | Filters and response |
|---|---|---|
| `GET /applications` | Producer or Admin | `status`, `cursor`, `limit`; own applications for Producer, all for Admin. Buyer receives 403. |
| `GET /applications/{id}` | Applicant or Admin | Contract fields, metadata integrity, review information and permitted evidence link. |
| `GET /certificates` | Public | `owner`, `status`, `listed`, `source`, `cursor`, `limit`; certificate summaries including quantity and total listing price. |
| `GET /certificates/{id}` | Public | Certificate quantity, total MWh, listing total price, source metadata, retirement declaration and snapshot block. |
| `GET /dashboard` | Public | Issued, active, listed, sold and retired counts; totalSalesWei; source breakdown. |
| `GET /wallet` | Authenticated | Role, owned certificate counts, claimableWei and wallet balanceWei. |

API status filters use the enum names defined in the contract specification. Each certificate response includes `metadataIntegrity` as `valid`, `missing` or `mismatch`. Missing metadata does not erase the on-chain certificate. The interface blocks purchase confirmation until the metadata can be verified.

Dashboard sales totals come from cumulative contract values. They must not be derived from only the most recent event page. Certificates with unavailable source metadata appear under `Unknown` in the source chart.

## Events and Activity

### GET /events

Public. Accept `certificateId`, `cursor` and `limit`. Each event includes `eventId`, contract address, event name, decoded arguments, transaction hash, log index, block number, block hash and `occurredAt`.

Read only the configured three contracts from their deployment blocks. Scan at most 1,000 blocks per RPC call and 5,000 blocks per API request. Use an opaque cursor containing the scan position and log position. Return `nextCursor`, `hasMore`, `scannedFrom` and `scannedTo`, including when a scan finds no matching events. A page limit must resume from the last consumed log without skipping the remainder of its block.

For a certificate's complete history, include its originating application events as well as issuance, listing, purchase and retirement events. Never accept a client-selected contract address to expand the scan.

### GET /transactions

Authenticated. Return the caller's server-verified transaction references, ordered by `verified_at DESC, tx_hash DESC`. Use an opaque cursor containing both values and the same exclusive ordering on subsequent pages. Return `nextCursor`; limits follow the general collection rules. Records may move when reverification changes their verification time, so clients merge pages by chain ID and transaction hash.

## Transaction Verification

### POST /transactions/verify

Authenticated write. The request contains only `txHash`. The server derives the sender, target, method, entity ID and amounts from the transaction rather than accepting client assertions.

1. Read the transaction and receipt on the configured chain.
2. Require the sender to match the session address and the target to be one of the deployed contracts.
3. Decode the input using the configured ABI and require an allowed user method.
4. If mined successfully, check the expected event, emitting contract, arguments and receipt status.
5. For application, rejection and retirement methods, load the referenced immutable content. Verify its creator, chain, target, kind and relevant entity or application fields.
6. Store the verified reference under the unique `(chain_id, tx_hash)` key.

Return 202 for a known pending transaction and 200 for a verified mined result. Repeated verification is idempotent. A reverted receipt is stored as `failed` and must not create successful content or business bindings. A successful on-chain transaction with incompatible metadata returns 422 and explicitly states that backend rejection does not reverse the transaction.

One mined receipt is sufficient for the classroom interface to display `confirmed`; this is not a claim of finality.

### GET /transactions/{txHash}

Authenticated and limited to the transaction sender. Recheck the current receipt and return `pending`, `confirmed`, `failed` or `orphaned`. A stored block hash that no longer matches the chain marks the reference as orphaned; refresh the affected business state from contracts. If the RPC request fails, return 503 instead of reporting cached information as a fresh confirmation.

The browser retains a submitted hash until a definite result is available. If verification is interrupted, it offers `Check transaction` rather than resubmitting the business operation.
