# GreenCert Development Specification

GreenCert is a mobile-first web application for issuing, trading and retiring simulated renewable energy certificates (RECs). It uses test ETH and a small set of smart contracts to demonstrate a complete certificate lifecycle.

This specification describes the implemented prototype. Current test and deployment evidence is linked from the repository README; some acceptance checks remain open.

## Documents

1. [Product and Requirements](01-product.md): scope, roles, business rules and coursework deliverables.
2. [Architecture and Workflows](02-architecture-flow.md): system architecture, flowcharts, state transitions and transaction sequence.
3. [Smart Contract Design](03-contracts.md): contracts, transaction methods, events and accounting rules.
4. [API Design](04-api.md): endpoints, authentication, request formats and transaction verification.
5. [Data Model](05-data-model.md): on-chain records, SQLite tables, files and data relationships.
6. [Mobile Interface](06-ui.md): pages, navigation, layouts and interaction states.
7. [Implementation and Delivery](07-delivery.md): fixed project structure, file responsibilities, milestones, deployment and submission checklist.
8. [Testing Plan](08-testing.md): test tools, named test files, cases, commands and evidence format.

Mermaid diagrams can be viewed in a compatible Markdown reader or on GitHub. Prices in examples are illustrative test values.

## Scope

- Three roles: Producer, Buyer and Admin.
- Three interacting contracts: RoleRegistry, CertificateRegistry and CertificateMarket.
- Each certificate record represents a batch of 1–100 simulated RECs. Each REC corresponds to 1 MWh.
- Producers submit evidence for manual review, then list an approved batch at one fixed total price.
- Buyers purchase, hold or retire the complete batch. Partial purchase and batch splitting are outside the scope. The current registered owner may relist an active, unlisted batch.
- The application uses Solidity, Remix, HTML, CSS, JavaScript, ethers.js, MetaMask, Flask and SQLite.
- The interface is a responsive website, accessible through a mobile wallet browser.

Generation evidence is reviewed manually. The blockchain records decisions, ownership and retirement; it does not independently verify electricity generation. GreenCert does not issue accredited certificates or carbon offsets.

## Domain Sources

- [EPA: Renewable Energy Certificates](https://www.epa.gov/green-power-markets/renewable-energy-certificates-recs): certificate units and renewable energy attributes.
- [EPA: Market Instruments](https://www.epa.gov/green-power-markets/market-instruments): the distinction between RECs and carbon offsets.
- [EPA: Double Counting](https://www.epa.gov/green-power-markets/double-counting): exclusive claims and the purpose of retirement.

These sources explain the domain. They do not establish accreditation or market eligibility for GreenCert. The proposed user needs should be supported by research or interviews in the project report.
