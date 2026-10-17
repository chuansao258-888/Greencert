const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.resolve(__dirname, "../../static/js/transactions.js"), "utf8");
const messages = [];
const verified = [];
const wallet = { address: "0x280d860553cb04d14cefc35b8726fb360df633ff", signer: {}, async ensureTargetNetwork() {} };
const context = {
  window: {
    GreenCertWallet: wallet,
    GreenCertApi: { async post(pathname, payload) { verified.push([pathname, payload.txHash]); } },
    GreenCertApp: { notice(message, error = false) { messages.push([message, error]); }, walletError(error) { return error.message; } },
  },
  GreenCertWallet: wallet,
  GreenCertApi: { async post(pathname, payload) { verified.push([pathname, payload.txHash]); } },
};
vm.runInNewContext(source, context);

async function run() {
  const txHash = "0x" + "a".repeat(64);
  await context.window.GreenCertTransactions.send("List certificate", async () => ({
    hash: txHash,
    async wait(confirms, timeout) {
      assert.equal(confirms, 1);
      assert.equal(timeout, 180000);
      return { status: 1 };
    },
  }));
  assert.deepEqual(verified, [["/transactions/verify", txHash], ["/transactions/verify", txHash]]);
  assert.match(messages.map(([message]) => message).join("\n"), /waiting for MetaMask approval/i);
  assert.match(messages.at(-1)[0], /confirmed and recorded/i);

  const pendingHash = "0x" + "b".repeat(64);
  await assert.rejects(
    context.window.GreenCertTransactions.send("Buy certificate", async () => ({
      hash: pendingHash,
      async wait() { const error = new Error("timeout"); error.code = "TIMEOUT"; throw error; },
    })),
    /still pending/,
  );
  assert.match(messages.at(-1)[0], /Do not submit it again/);
  process.stdout.write("Transaction lifecycle checks passed.\n");
}

run().catch((error) => { process.stderr.write(`${error.stack}\n`); process.exitCode = 1; });
