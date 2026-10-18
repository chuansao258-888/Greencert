# Problem and scenario evaluation evidence

## The problem and its limits

In a REC market, a producer, buyer and reviewer need to establish which generation attributes are represented, who holds them, and whether they have been retired before a claim is made. The [US EPA explanation of RECs](https://www.epa.gov/green-power-markets/renewable-energy-certificates-recs) describes ownership and tracking of attributes for one MWh of renewable generation. Its [double-counting guidance](https://www.epa.gov/green-power-markets/double-counting) describes competing claims and retirement as a control. These are US market sources, not evidence of GreenCert users, their costs, or Singapore regulatory acceptance.

GreenCert models a shared, inspectable ownership and retirement history across parties. A conventional central database can also implement those controls; blockchain makes signed state transitions and public event history independently inspectable but adds gas, key management and dependence on an RPC and chain. It does not make a generation claim true, prevent duplicate certificates in other systems, ensure privacy for on-chain data, or replace an accredited registry. Admin review and truthful evidence remain necessary. Producer/Buyer labels do not restrict ordinary business functions to one role. The current UI does not prevent an Admin from approving when evidence is unavailable.

Practical barriers include accredited registry integration, cross-system duplicate detection, actual generation measurement, local legal and accounting requirements, key loss, wallet usability, public data exposure, RPC availability, operating costs and durability of off-chain evidence. The public service is a free prototype with an ephemeral SQLite and upload filesystem; it is not a production-ready storage arrangement.

## Scenario observations and measurable indicators

| Scenario / indicator | Observation and evidence | What it establishes |
|---|---|---|
| Role guard on current code | Two local EVM tests rejected unregistered submission and purchase; 14 current Solidity test functions passed in total. [Local test output](contract-test-local.txt) and [test results](test-results.md). | Specific tested cases only; no real user study or full current Sepolia lifecycle. |
| Demonstrated lifecycle | Historical Sepolia transaction rows cover registration, application, approval, listing, repricing, cancellation, purchase, withdrawal and retirement; [transaction mapping](../submission-checklist.md#transaction-evidence-map). | A prototype scenario on the historical contracts, not current-deployment completion or an impact study. |
| Gas cost | Historical ten-step run consumed 2,997,934 gas; [receipt CSV](gas-results.csv) and [analysis](gas-analysis.md). | Testnet transaction costs for those paths and states, not cost savings against a baseline. |
| Evidence availability | On 18 October the public current deployment returned one certificate with incomplete integrity status and unavailable metadata/file. [Test results](test-results.md). | A concrete limitation of the observed service; its cause is not established. |

Candidate measures for later evaluation are successful guarded lifecycle steps / attempted steps, fraction of records with all integrity checks available, gas used by transaction type, and completion time or task success from an actual user study. No business cost reduction, time saving, satisfaction or adoption result has been measured. Before claiming real-world impact, collect a comparison baseline and suitable stakeholder or user evidence, or explicitly report why the prototype results do not establish impact.
