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
| Validate through feedback, user testing, scenario evaluation or datasets | Domain evidence records bounded test scenarios and historical lifecycle | Evidence available for old deployment; current local scenarios executed | The brief permits scenario-based evaluation. Use the documented scenarios and their limits; further user data is needed only for claims that depend on it. |
| Constraints, ethics, regulation and adoption barriers | Domain evidence | Evidence available | Discuss jurisdiction-specific implications in the final report; no legal compliance claim is established. |

## Mandatory functional requirements — original §3, page 1

| Requirement | Evidence | Status | Remaining action |
|---|---|---|---|
| “at least three user roles” and role-based authentication | [Roles](development/01-product.md), `backend/auth.py`, `contracts/RoleRegistry.sol` | Complete in code; needs current signed workflow verification | Admin is distinct; Producer and Buyer share ordinary permissions. Current local test evidence is recorded; a new signed demonstration is not separately specified by the brief. |
| MetaMask integration and secure transaction signing | [User manual](user-manual.md), `static/js/wallet.js`, `static/js/transactions.js` | Evidence available for old deployment | Historical signed transactions and the implementation are documented; a message signature is not a transaction. |
| Three interacting contracts and at least ten blockchain transaction types | [Contract specification](development/03-contracts.md), transaction map below, Solidity source | Complete in code; old deployment receipts | Eleven user transaction types are defined. Identify the earlier deployment when citing its receipts; the brief does not explicitly require rerunning each type after redeployment. |
| REST API, “persistent data storage”, “comprehensive exception handling” | [API](development/04-api.md), [data model](development/05-data-model.md), backend tests | SQLite/files implemented; exception coverage needs verification | Free Render has no persistent disk; files may disappear. API and tests cover defined failures, not every possible failure. |
| Responsive dashboard, transaction history, event logs and relevant visualizations | [UI diagram](development/06-ui.md), `templates/`, current API and frontend tests | Implemented; needs demonstration | Current public metadata is unavailable for certificate 1; describe this observation accurately. |
| Gas estimation and optimization analysis, smart contract testing, public cloud deployment | [Gas analysis](../submission/gas/gas-analysis.md), [test results](../submission/testing/test-results.md), [live URL](https://greencert.onrender.com) | Current local contract tests passed; gas evidence on old deployment | A new gas run is needed only to claim a comparison with the guarded version. The script estimates gas; the website does not present its own explicit estimate. Optimization choices are reasoned, not experimentally benchmarked. |

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

The methods are distinct transaction types, not read calls or wallet signatures. Historical receipts below are from 13 October: RoleRegistry `0xc6ddfdef0eef7b9d2bb6df9e60bf439a2725a369`, Registry `0x338c972fcab0892448fa0ee939f3330fb42f6c04`, Market `0xd7f2b6c233e7044ab4a76317b834c58c2ff23f01`. The CSV row names point to full transaction hashes and gas. These do not prove the complete flow on the guarded contracts currently in `deployment.json`.

| Type | Historical receipt row in [CSV](../submission/gas/gas-results.csv) | Current guarded code |
|---|---|---|
| Register | `register_producer`, `register_buyer` | Local role tests pass; reused current RoleRegistry is a different deployment. |
| Submit | `submit_application`, `e2e_submit_for_withdrawal`, `e2e_submit_for_rejection` | Local submission and unregistered rejection pass. |
| Withdraw application | `e2e_withdraw_application` | Local test passes. |
| Approve and issue | `approve_application` | Local test passes; current `CertificateIssued` receipt also observed, see test results. |
| Reject | `e2e_reject_application` | Local test passes. |
| List | `list_certificate`, `e2e_relist` | Local test passes; current `CertificateListed` receipt also observed. |
| Reprice | `e2e_reprice` | Local test passes. |
| Cancel | `e2e_cancel` | Local test passes. |
| Buy | `e2e_buy` | Local purchase and unregistered rejection pass. |
| Withdraw proceeds | `e2e_withdraw_proceeds` | Local test passes. |
| Retire | `e2e_retire` | Local test passes. |

## Presentation and submission materials

The slides and demonstration recording are complete. Their locations and Git status are described in [presentation materials](../submission/presentation/README.md). The course brief does not specify an upload destination or media container; use the actual course submission instructions when submitting.
