const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const list = { innerHTML: "Loading applications…" };
const marketList = { innerHTML: "" };
const archive = { innerHTML: "" };
const details = { innerHTML: "", hidden: true };
const form = { hidden: true };
let requests = 0;
let applicationItems = [];
const wallet = { address: null, role: null };
const context = {
  window: {},
  document: {
    getElementById(id) {
      return { applicationList: list, applicationFormPanel: form, marketList, certificateArchive: archive, applicationDetails1: details }[id] || null;
    },
    addEventListener() {},
  },
  GreenCertWallet: wallet,
  GreenCertApp: {
    escape(value) { return String(value).replaceAll("<", "&lt;").replaceAll(">", "&gt;"); },
  },
  GreenCertApi: {
    async get(path) {
      if (path === "/certificates") return [
        { id: "1", metadata: { siteName: "Demo Solar Site" }, quantity: "5", status: "Retired", listed: false },
      ];
      if (path === "/applications/1") return applicationItems[0];
      assert.equal(path, "/applications");
      requests += 1;
      return applicationItems;
    },
  },
};
vm.runInNewContext(fs.readFileSync(path.resolve(__dirname, "../../static/js/pages.js"), "utf8"), context);

async function run() {
  const applications = context.window.GreenCertPages.applications.bind(context.window.GreenCertPages);
  await applications();
  assert.match(list.innerHTML, /Connect a wallet/);
  assert.equal(requests, 0);

  wallet.address = "0x280d860553cb04d14cefc35b8726fb360df633ff";
  wallet.role = "Buyer";
  await applications();
  assert.match(list.innerHTML, /Connected as Buyer/);
  assert.match(list.innerHTML, /my-certificates/);
  assert.doesNotMatch(list.innerHTML, /Connect a wallet/);
  assert.equal(requests, 0);

  wallet.role = "Producer";
  await applications();
  assert.equal(form.hidden, false);
  assert.match(list.innerHTML, /No applications/);
  assert.equal(requests, 1);

  applicationItems = [
    { id: "1", status: "Approved", quantity: "5", producer: wallet.address, metadataHash: "0xabc", metadata: { siteName: "Demo Solar Site", periodStart: "1790812800", periodEnd: "1790985599" }, evidenceFileId: "proof-1" },
    { id: "2", status: "Withdrawn", quantity: "2", producer: wallet.address, metadataHash: "0xdef", metadata: null, evidenceFileId: null },
    { id: "3", status: "Rejected", quantity: "3", producer: wallet.address, metadataHash: "0xeee", metadata: null, evidenceFileId: null },
  ];
  await applications();
  for (const status of ["approved", "withdrawn", "rejected"]) {
    assert.match(list.innerHTML, new RegExp(`status-${status}`));
  }
  assert.match(list.innerHTML, /Approved<\/span>/);
  assert.match(list.innerHTML, /Download evidence/);
  assert.match(list.innerHTML, /Evidence unavailable/);
  assert.equal(requests, 2);

  const pages = context.window.GreenCertPages;
  const button = { dataset: {}, textContent: "View details", setAttribute(name, value) { this[name] = value; } };
  await pages.action("details", "1", button);
  assert.equal(details.hidden, false);
  assert.match(details.innerHTML, /Demo Solar Site/);
  assert.equal(button["aria-expanded"], "true");
  await pages.action("details", "1", button);
  assert.equal(details.hidden, true);

  await pages.market();
  assert.match(marketList.innerHTML, /No listings yet/);
  assert.match(archive.innerHTML, /Certificate #1/);
  assert.match(archive.innerHTML, /status-retired/);
  const validHash = "0x" + "a".repeat(64);
  assert.match(pages.transactionLink(validHash), /sepolia\.etherscan\.io\/tx/);
  assert.doesNotMatch(pages.transactionLink("<script>"), /href=/);

  const unknown = context.window.GreenCertPages.statusBadge("<script>");
  assert.match(unknown, /status-other/);
  assert.match(unknown, /&lt;script&gt;/);
  process.stdout.write("Application role states passed.\n");
}

run().catch((error) => { process.stderr.write(`${error.stack}\n`); process.exitCode = 1; });
