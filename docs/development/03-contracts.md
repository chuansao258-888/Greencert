# Smart Contract Design

## Deployment and Shared Types

Use Solidity 0.8.x with a fixed compiler version, EVM target and optimizer configuration recorded in `deployment.json`. The design uses structs, mappings, enums, modifiers, events and explicit checks. It does not require token standards or upgradeable proxies.

Deploy in this order:

1. `RoleRegistry(admin)`
2. `CertificateRegistry(roleRegistry)`
3. `CertificateMarket(roleRegistry, certificateRegistry)`
4. The Admin calls `CertificateRegistry.setMarket(market)`.

The certificate registry constructor rejects wallet addresses and checks that its role contract reports an Admin. The market constructor rejects wallet addresses and checks that the certificate registry points to the same role contract. Before approving either deployment in MetaMask, compare each constructor address with the previously recorded contract address rather than the currently selected wallet address. After deployment, read back the public registry references before continuing.

`setMarket` succeeds once. It checks a nonzero contract address and verifies that the market's registry and role references match. Certificate and market operations remain unavailable until binding is complete.

| Enum | Values |
|---|---|
| Role | None = 0, Producer = 1, Buyer = 2, Admin = 3 |
| ApplicationStatus | None = 0, Pending = 1, Approved = 2, Rejected = 3, Withdrawn = 4 |
| CertificateStatus | None = 0, Active = 1, Retired = 2 |

Identifiers start at 1. Zero denotes an absent record. The Admin is immutable. The role registry is used to identify the reviewer; ordinary certificate operations are authorized by wallet ownership and lifecycle state rather than Producer or Buyer labels.

## User Transactions

| ID | Contract method | Permission and preconditions | Result |
|---|---|---|---|
| TX-01 | `RoleRegistry.register(uint8 role)` | Unregistered address; role must be Producer or Buyer. | Register a permanent primary participation role from Account; emit `RoleRegistered`. Ordinary operations remain open to all wallets. |
| TX-02 | `CertificateRegistry.submitApplication(bytes32 siteHash, uint64 periodStart, uint64 periodEnd, uint32 batchIndex, uint32 quantity, bytes32 metadataHash)` | Any wallet; nonzero hashes; start < end <= block timestamp; positive batch index; quantity from 1 to 100; unused batch key. | Create Pending application; reserve batch key; emit `ApplicationSubmitted`. |
| TX-03 | `CertificateRegistry.withdrawApplication(uint256 applicationId)` | Applicant; Pending application. | Set Withdrawn; emit `ApplicationWithdrawn`. |
| TX-04 | `CertificateRegistry.approveApplication(uint256 applicationId)` | Admin; Pending application whose evidence supports its quantity. | Set Approved; issue one Active certificate record containing the complete batch quantity to the submitting wallet; emit `CertificateIssued`. |
| TX-05 | `CertificateRegistry.rejectApplication(uint256 applicationId, bytes32 reasonHash)` | Admin; Pending application; nonzero reason hash. | Set Rejected; retain reason hash; emit `ApplicationRejected`. |
| TX-06 | `CertificateMarket.listCertificate(uint256 certificateId, uint256 totalPriceWei)` | Current owner; Active and unlisted certificate batch; positive total price. | List the complete batch; set registry listing flag; emit `CertificateListed`. |
| TX-07 | `CertificateMarket.updatePrice(uint256 certificateId, uint256 newTotalPriceWei)` | Current seller; active listing; positive total price. | Change the complete batch price; emit `ListingPriceUpdated`. |
| TX-08 | `CertificateMarket.cancelListing(uint256 certificateId)` | Current seller; active listing. | Deactivate listing and clear registry flag; emit `ListingCancelled`. |
| TX-09 | `CertificateMarket.buyCertificate(uint256 certificateId, uint256 expectedPriceWei)` payable | Any wallet other than seller; active listing; current total price = expected price = msg.value. | Transfer ownership of the complete batch, close listing and credit seller; emit `CertificatePurchased`. |
| TX-10 | `CertificateMarket.withdraw()` | Caller has positive credit. | Clear caller's credit, reduce total credits and transfer proceeds; emit `Withdrawal`. |
| TX-11 | `CertificateRegistry.retireCertificate(uint256 certificateId, bytes32 retirementHash)` | Current owner; Active and unlisted certificate batch; nonzero declaration hash. | Retire the complete quantity; retain owner, quantity, hash and retirement timestamp; emit `CertificateRetired`. |

Registration counts as one transaction type. Deployment, binding, read calls, wallet connection, message signatures and file uploads are separate operations and are not included in these eleven types.

## Contract-to-Contract Methods

| Method | Access and behaviour |
|---|---|
| `registry.setListed(uint256 certificateId, address seller, bool listed)` | Bound market only. Require an Active certificate, matching owner and a genuine flag change. |
| `registry.transferOnSale(uint256 certificateId, address seller, address buyer)` | Bound market only. Require Active, listed and owner = seller. Update owner and clear the listing flag. |
| `market.roleRegistry()` | Return the configured role contract address. |
| `market.certificateRegistry()` | Return the configured certificate contract address. |
| `roles.roleOf(address account)` | Return the account's role. |
| `roles.admin()` | Return the immutable Admin address. |

External users cannot invoke market-only registry operations successfully.

## Records and Read Methods

| Record | Fields |
|---|---|
| Application | id, producer, batchKey, siteHash, periodStart, periodEnd, batchIndex, quantity, metadataHash, status, certificateId, rejectionHash |
| Certificate | id, applicationId, producer, owner, quantity, metadataHash, status, listed, issuedAt, retiredAt, retirementHash |
| Listing | certificateId, seller, totalPriceWei, active |
| Market accounting | credits[address], totalCredits, totalSalesWei, soldCount |

`getApplication(id)` and `getCertificate(id)` revert for nonexistent IDs. `getListing(id)` returns `active=false` for an existing, unlisted certificate. `applicationCount` and `certificateCount` support bounded enumeration. Each certificate copies the application's immutable `quantity` and metadata hash. One unit of quantity represents one simulated REC and 1 MWh.

The contract calculates the batch key itself:

```solidity
keccak256(abi.encode(
    block.chainid,
    msg.sender,
    siteHash,
    periodStart,
    periodEnd,
    batchIndex
))
```

`siteHash` is the keccak256 hash of the UTF-8 normalised site code. The application accepts uppercase ASCII letters, digits and hyphens, with a length of 1 to 40 characters. `quantity` is an integer from 1 to 100. The batch key remains reserved after rejection or withdrawal. Quantity is immutable after submission and is not used to bypass a reserved batch key.

## Events

Use indexed fields for IDs and principal participants, with no more than three indexed arguments per event.

```text
RoleRegistered(account, role)
ApplicationSubmitted(applicationId, producer, batchKey, quantity, metadataHash)
ApplicationWithdrawn(applicationId, producer)
ApplicationRejected(applicationId, admin, reasonHash)
CertificateIssued(certificateId, applicationId, producer, quantity, metadataHash)
CertificateListed(certificateId, seller, totalPriceWei)
ListingPriceUpdated(certificateId, seller, oldTotalPriceWei, newTotalPriceWei)
ListingCancelled(certificateId, seller)
CertificatePurchased(certificateId, seller, buyer, quantity, totalPriceWei)
Withdrawal(seller, amountWei)
CertificateRetired(certificateId, owner, retirementHash, retiredAt)
```

## Accounting and Correctness

- Repeated review, purchase, retirement or withdrawal must not duplicate effects.
- A stale total price causes a revert. The interface asks the purchaser to refresh and confirm the new price.
- Listing, purchase, ownership transfer and retirement always apply to the complete immutable quantity. No function accepts a purchase or retirement quantity.
- The purchase updates the listing, registry ownership and accounting atomically. Any failed internal call reverts the whole transaction.
- Withdrawal clears the balance before sending ETH and uses a reentrancy guard. A failed transfer reverts the balance update.
- `sum(credits) == totalCredits` and `address(this).balance >= totalCredits`. An unsolicited ETH balance does not create seller credit.
- `totalSalesWei` and `soldCount` increase only on a successful purchase. Withdrawal does not reduce sales totals.
- All monetary arithmetic uses integer wei. Browser code uses `BigInt` and `parseEther`, never floating-point calculations.
- Only the authorised reviewer can approve issuance. Evidence quality remains a manual assessment.
