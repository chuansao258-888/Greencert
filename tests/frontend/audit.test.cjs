const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const hash = "0x" + "a".repeat(64);
const report = {
  certificateId: "1", applicationId: "1", status: "verified",
  checks: { approvedApplication: "passed", metadataHash: "passed", metadataFields: "passed", evidenceFile: "passed" },
  summary: { siteName: "Demo Solar Site", source: "Solar", country: "SG", periodStart: "1790812800", periodEnd: "1790899200", proofSha256: "b".repeat(64) },
};
const elements = Object.fromEntries([
  "certificateDetail", "certificateEvidence", "certificateEvents", "auditReports", "auditEvents",
  "auditVerified", "auditIncomplete", "auditMismatch", "auditFilter",
].map((id) => [id, { innerHTML: "", textContent: "", dataset: { certificateId: "1" }, value: "all" }]));
const context = {
  window: {},
  document: { getElementById(id) { return elements[id] || null; }, addEventListener() {} },
  GreenCertApp: { escape(value) { return String(value ?? "").replaceAll("<", "&lt;").replaceAll(">", "&gt;"); }, eth() { return "0 ETH"; } },
  GreenCertApi: { async get(resource) {
    if (resource === "/certificates/1") return { id: "1", metadata: report.summary, quantity: "5", status: "Retired", listed: false, owner: "0x123", metadataHash: hash };
    if (resource === "/certificates/1/evidence-summary") return report;
    if (resource === "/certificates/1/events") return [{ event: "CertificateIssued", blockNumber: "10", transactionHash: hash }];
    if (resource === "/audit") return { reports: [report], totals: { verified: 1, incomplete: 0, mismatch: 0 }, eventStatus: "available", events: [{ event: "CertificateIssued", certificateId: "1", blockNumber: "10", transactionHash: hash }] };
    throw new Error(`Unexpected resource: ${resource}`);
  } },
};
vm.runInNewContext(fs.readFileSync(path.resolve(__dirname, "../../static/js/pages.js"), "utf8"), context);

async function run() {
  const pages = context.window.GreenCertPages;
  await pages.certificateDetail();
  assert.match(elements.certificateEvidence.innerHTML, /Evidence integrity/);
  assert.match(elements.certificateEvidence.innerHTML, /status-verified/);
  assert.match(elements.certificateEvidence.innerHTML, /Demo Solar Site/);
  assert.doesNotMatch(elements.certificateEvidence.innerHTML, /proof-1/);
  await pages.audit();
  assert.equal(elements.auditVerified.textContent, 1);
  assert.match(elements.auditReports.innerHTML, /Certificate #1/);
  assert.match(elements.auditEvents.innerHTML, /sepolia\.etherscan\.io\/tx/);
  elements.auditFilter.value = "mismatch";
  pages.renderAuditReports();
  assert.match(elements.auditReports.innerHTML, /No matching records/);
  process.stdout.write("Evidence and audit views passed.\n");
}

run().catch((error) => { process.stderr.write(`${error.stack}\n`); process.exitCode = 1; });
