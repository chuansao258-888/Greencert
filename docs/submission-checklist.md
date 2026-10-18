# SC6113 submission checklist

Checked against the original local `docs/SC6113 Group Project.docx`, rendered in Word as two pages on 18 October 2026. Section and page references below refer to that source, not the internal delivery plan. This is a working submission checklist, not the 10–15 page technical report. “Complete” means the material exists at the cited location, not that a lecturer has accepted it. The course brief does not specify a file upload destination or require a separate contribution file. Individual contributions are planned for the technical report.

## Project brief — page 1

| Original requirement | Current evidence | Status | Remaining action |
|---|---|---|---|
| Enterprise financial or business DApp integrating blockchain, contracts, backend, frontend, database and cloud | [Architecture](development/02-architecture-flow.md), source and public URL | Implemented prototype; production readiness unproven | Present its simulated REC scope and deployment limitations accurately. |
| Secure engineering, scalability, innovation, measurable impact and professional project management | [Contract design](development/03-contracts.md), [tests](../submission/testing/test-results.md), Git history and [evaluation](../submission/evaluation/problem-evaluation.md) | Needs evaluation | Assess security and scaling limitations, explain the project's contribution and management, and report only measured impact. |

## Real-world problem requirements — original §1, page 1

| Original requirement / source wording | Current evidence | Status | Remaining action |
|---|---|---|---|
| Specific significant problem suitable for blockchain | [Product](development/01-product.md), [domain evidence](../submission/evaluation/problem-evaluation.md) | Evidence available | Explain the problem and significance in the final report without claiming validated user demand. |
| Target users, stakeholders, pain points, limitations of existing solutions | Product roles; domain evidence | Needs verification | Complete stakeholder analysis and substantiate specific user pain points in the final report. |
| “credible evidence” of importance | EPA sources in domain evidence | Evidence available | Relate the sources to the specific target users; they do not establish GreenCert adoption. |
| Why blockchain is appropriate and centralized solution may be insufficient | Domain evidence compares public verification and trade-offs | Evidence available | Develop the comparison in the final report; do not assert a centralized database cannot provide audit controls. |
| Functional, non-functional, security and usability requirements | [Product requirements](development/01-product.md), [contract design](development/03-contracts.md), [UI](development/06-ui.md) | Evidence available | Review actual security, usability and deployment limitations in the final report. |
| Define measurable success indicators | Domain evidence proposes indicators; test and gas results have observed counts | Needs verification | Scenario indicators and observed results are recorded. Discuss their limits in the final report; no real-world time savings, adoption or satisfaction has been measured. |
| Validate through feedback, user testing, scenario evaluation or datasets | Domain evidence records bounded scenarios using the current source | Current local scenarios executed | The brief permits scenario-based evaluation. Further user data is needed only for claims that depend on user behaviour or adoption. |
| Constraints, ethics, regulation and adoption barriers | Domain evidence | Evidence available | Discuss jurisdiction-specific implications in the final report; no legal compliance claim is established. |

## Mandatory functional requirements — original §3, page 1

| Requirement | Evidence | Status | Remaining action |
|---|---|---|---|
| “at least three user roles” and role-based authentication | [Roles](development/01-product.md), `backend/auth.py`, `contracts/RoleRegistry.sol` | Complete in code; needs current signed workflow verification | Admin is distinct; Producer and Buyer share ordinary permissions. Current local test evidence is recorded; a new signed demonstration is not separately specified by the brief. |
| MetaMask integration and secure transaction signing | [User manual](user-manual.md), `static/js/wallet.js`, `static/js/transactions.js` | Implemented | MetaMask signs login challenges and prepares state-changing transactions. A login signature is not a blockchain transaction. |
| Three interacting contracts and at least ten blockchain transaction types | [Contract specification](development/03-contracts.md), transaction map below, Solidity source | Complete in code and current local workflow | Eleven user transaction types are defined and measured on a fresh local deployment of the current source. |
| REST API, “persistent data storage”, “comprehensive exception handling” | [API](development/04-api.md), [data model](development/05-data-model.md), backend tests | SQLite/files implemented; exception coverage needs verification | Free Render has no persistent disk; files may disappear. API and tests cover defined failures, not every possible failure. |
| Responsive dashboard, transaction history, event logs and relevant visualizations | [UI diagram](development/06-ui.md), `templates/`, current API and frontend tests | Implemented; needs demonstration | Current public metadata is unavailable for certificate 1; describe this observation accurately. |
| Gas estimation and optimization analysis, smart contract testing, public cloud deployment | [Gas analysis](../submission/gas/gas-analysis.md), [test results](../submission/testing/test-results.md), [live URL](https://greencert.onrender.com) | Current tests and gas workflow passed | The current local workflow records gas for all eleven business transaction types. The website relies on MetaMask for fee preparation. Optimization choices are reasoned, not benchmarked against an alternative contract. |

## Required deliverables — original §5, pages 1–2

| Original item | Current evidence / material | Status | Remaining action |
|---|---|---|---|
| “10-15 page technical report” with problem, stakeholders, evidence and measurable impact | Supporting evidence in this checklist and [evaluation](../submission/evaluation/problem-evaluation.md) | With final report | Write the report later; measurable real-world impact is not established. |
| Architecture, contract interaction, data model, process flow, UI diagrams | [Architecture and interaction](development/02-architecture-flow.md), [data model](development/05-data-model.md), [UI layout and navigation](development/06-ui.md) | Complete in repository | Mermaid needs a compatible viewer such as GitHub; include in submission format chosen by the team. |
| GitHub source, documentation, setup and contribution history | [README](../README.md) and Git history | Repository available on GitHub | Keep the submitted repository current; the free Render deployment uses ephemeral files. |
| Public deployment URL, contract details and testing report | [README](../README.md), [deployment record](development/09-registration-deployment.md), [test report](../submission/testing/test-results.md) | Available with limitations | The current evidence file and metadata for certificate 1 are unavailable. The brief does not require this particular record to be restored. |
| Presentation slides and “a 10-minute demonstration video or live demonstration” | [Presentation materials](../submission/presentation/README.md) | Completed according to the group | The brief specifies no location or exact media format. |
| User manual and “individual contribution report” | [User manual](user-manual.md); Git history | Manual complete; contribution with final report | Include the individual contribution information in the final report. |

The learning outcomes in original §2 and the rubric in §6 additionally call for evaluation of security, scalability, usability, feasibility and impact, and describe a production-ready cloud system. The free-service and test limitations above mean production readiness and real-world impact are not established. The brief does not explicitly require phone-device tests, performance benchmarks, screenshots, a paid disk or a separate contribution file.

## Transaction evidence map

The methods are distinct state-changing transaction types, not read calls or wallet signatures. The gas CSV was generated from a fresh local deployment of the current guarded source.

| Type | Current receipt row in [CSV](../submission/gas/gas-results.csv) | Verification |
|---|---|---|
| Register | `Register producer`, `Register buyer` | Both roles were stored. |
| Submit | `Submit application` and the two additional submission rows | Pending applications were created. |
| Withdraw application | `Withdraw application` | The application became Withdrawn. |
| Approve and issue | `Approve application` | An active certificate was issued. |
| Reject | `Reject application` | The application became Rejected. |
| List | `List certificate`, `Relist certificate` | Listing state became active. |
| Reprice | `Update listing price` | The active price changed. |
| Cancel | `Cancel listing` | Listing state became inactive. |
| Buy | `Buy certificate` | Ownership and seller credit changed. |
| Withdraw proceeds | `Withdraw proceeds` | Seller credit returned to zero. |
| Retire | `Retire certificate` | The certificate became Retired. |

## Presentation and submission materials

The slides and demonstration recording are complete. Their locations and Git status are described in [presentation materials](../submission/presentation/README.md). The course brief does not specify an upload destination or media container; use the actual course submission instructions when submitting.
