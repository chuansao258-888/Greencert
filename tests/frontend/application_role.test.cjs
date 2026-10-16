const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const list = { innerHTML: "Loading applications…" };
const form = { hidden: true };
let requests = 0;
let applicationItems = [];
const wallet = { address: null, role: null };
const context = {
  window: {},
  document: {
    getElementById(id) {
      return { applicationList: list, applicationFormPanel: form }[id] || null;
    },
    addEventListener() {},
  },
  GreenCertWallet: wallet,
  GreenCertApp: {
    escape(value) { return String(value).replaceAll("<", "&lt;").replaceAll(">", "&gt;"); },
  },
  GreenCertApi: {
    async get(path) {
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
    { id: "1", status: "Approved", quantity: "5", producer: wallet.address },
    { id: "2", status: "Withdrawn", quantity: "2", producer: wallet.address },
    { id: "3", status: "Rejected", quantity: "3", producer: wallet.address },
  ];
  await applications();
  for (const status of ["approved", "withdrawn", "rejected"]) {
    assert.match(list.innerHTML, new RegExp(`status-${status}`));
  }
  assert.match(list.innerHTML, /Approved<\/span>/);
  assert.equal(requests, 2);

  const unknown = context.window.GreenCertPages.statusBadge("<script>");
  assert.match(unknown, /status-other/);
  assert.match(unknown, /&lt;script&gt;/);
  process.stdout.write("Application role states passed.\n");
}

run().catch((error) => { process.stderr.write(`${error.stack}\n`); process.exitCode = 1; });
