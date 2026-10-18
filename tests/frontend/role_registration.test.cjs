const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

const elements = { walletRole: {}, roleRegistration: { hidden: true }, walletPanel: {}, walletBalance: {}, walletProceeds: {}, withdrawProceeds: {} };
const wallet = { address: "0x1234", role: "None", signer: {}, async ensureTargetNetwork() {} };
let click;
let registeredRole = null;
let chainRole = "None";
const context = {
  window: { GreenCertWallet: wallet },
  GreenCertWallet: wallet,
  document: {
    getElementById(id) { return elements[id] || null; },
    addEventListener(name, handler) { if (name === "click") click = handler; },
  },
  confirm() { return true; },
  ethers: { formatEther() { return "0"; } },
  GreenCertContracts: { contracts: { roleRegistry: { async register(role) { registeredRole = role; chainRole = role === 1 ? "Producer" : "Buyer"; } } } },
  GreenCertTransactions: { async send(label, action) { await action(); } },
  GreenCertApi: { async get(route) { return route === "/auth/me" ? { role: chainRole } : { balanceWei: "0", claimableWei: "0" }; } },
};
for (const file of ["app.js", "pages.js"]) vm.runInNewContext(fs.readFileSync(path.join(__dirname, "../../static/js", file), "utf8"), context);
context.GreenCertApp = context.window.GreenCertApp;
context.GreenCertPages = context.window.GreenCertPages;
context.GreenCertPages.refresh = async () => context.GreenCertPages.wallet();

async function run() {
  for (const role of ["None", "Producer", "Buyer", "Admin"]) {
    wallet.role = role;
    context.GreenCertApp.renderRole();
    assert.equal(elements.roleRegistration.hidden, role !== "None");
    assert.equal(elements.walletRole.textContent, `Role: ${role === "None" ? "Not registered" : role}`);
  }
  for (const role of [1, 2]) {
    wallet.role = chainRole = "None";
    const button = { dataset: { registerRole: String(role) } };
    await click({ target: { closest() { return button; } } });
    assert.equal(registeredRole, role);
    assert.equal(wallet.role, role === 1 ? "Producer" : "Buyer");
    assert.equal(elements.roleRegistration.hidden, true);
    assert.equal(button.disabled, false);
  }
  registeredRole = null;
  context.confirm = () => false;
  await click({ target: { closest() { return { dataset: { registerRole: "1" } }; } } });
  assert.equal(registeredRole, null);
  process.stdout.write("Role display, registration and cancellation checks passed.\n");
}
run().catch(error => { process.stderr.write(`${error.stack}\n`); process.exitCode = 1; });
