# Problem and Scenario Evaluation Evidence

## Problem and limits

In a REC market, a producer, buyer and reviewer need to establish which generation attributes a certificate represents, who holds it and whether it has been retired before a claim is made. GreenCert models a shared ownership and retirement history for simulated REC batches.

A central database can also implement these controls. GreenCert uses blockchain so different participants can inspect signed state changes and public events. This adds gas, wallet management and dependence on an RPC and chain. It does not prove that generation evidence is true, detect duplicates in another registry or replace an accredited REC system. Admin review remains necessary.

The prototype also depends on off-chain metadata and uploaded evidence. The free Render filesystem can lose those files after a restart or deployment. A chain record may remain available while its supporting evidence is incomplete.

## Scenario results

| Indicator | Expected outcome | Current result | Evidence and scope |
|---|---|---|---|
| Backend behaviour | Selected API, authentication, verification and persistence checks pass | 18 of 18 tests passed | [Test results](../testing/test-results.md); local automated tests |
| Frontend behaviour | Selected dashboard, wallet, mobile, transaction and registration checks pass | 7 of 7 scripts passed | [Test results](../testing/test-results.md); browser logic tests |
| Current contract tests | Selected state and rejection assertions pass | 14 of 14 functions passed | [Local output](../testing/contract-test-local.txt); current source on Ganache Shanghai |
| Registration guard | Unregistered submission and purchase are rejected | 2 of 2 local cases passed; deployed read-only calls also reverted | [Test results](../testing/test-results.md) |
| Current contract workflow | Every recorded state transaction succeeds and final states match | 16 of 16 transactions succeeded | [Gas CSV](../gas/gas-results.csv); fresh local deployment of current source |
| Gas for eleven business types | Record one successful receipt for every defined business transaction type | 1,075,912 gas in total | [Gas analysis](../gas/gas-analysis.md); local EVM gas, not a Sepolia fee |
| Evidence verification | Matching data verifies; missing data is incomplete; changed data is a mismatch | Selected verification tests passed | Backend fixtures use temporary storage and mocked chain reads |

These figures evaluate the prototype scenarios only. No conventional workflow baseline, user satisfaction survey, operating-cost comparison or adoption study was conducted. The results therefore do not establish real-world time savings, cost reduction or market adoption.
