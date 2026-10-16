const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const account = "0x280d860553cb04d14cefc35b8726fb360df633ff";
const other = "0x7ac1c7fb0c77332b2d74688fca86b9c9a3d5b028";
const source = fs.readFileSync(path.resolve(__dirname, "../../static/js/wallet.js"), "utf8");

function createWallet({ accounts = [account], sessionAddress = account, chainId = "0xaa36a7" } = {}) {
  const calls = [];
  const api = {
    csrfToken: null,
    async get(route) {
      calls.push(route);
      if (route === "/auth/me") return { address: sessionAddress, role: "Buyer", csrfToken: "csrf" };
      return { chainId: 11155111 };
    },
  };
  const context = {
    window: {
      GreenCertApi: api,
      ethereum: {
        async request({ method }) {
          if (method === "eth_accounts") return accounts;
          if (method === "eth_chainId") return chainId;
          throw new Error(`Unexpected wallet request: ${method}`);
        },
      },
    },
    ethers: {
      BrowserProvider: class {
        async getSigner(address) {
          return { async getAddress() { return address; } };
        }
      },
    },
  };
  vm.runInNewContext(source, context);
  return { wallet: context.window.GreenCertWallet, api, calls };
}

async function run() {
  const valid = createWallet();
  assert.equal(await valid.wallet.restore(), true);
  assert.equal(valid.wallet.address, account);
  assert.equal(valid.wallet.role, "Buyer");
  assert.equal(valid.api.csrfToken, "csrf");
  assert.equal(valid.wallet.signer && typeof valid.wallet.signer.getAddress, "function");

  const changedAccount = createWallet({ accounts: [other] });
  assert.equal(await changedAccount.wallet.restore(), false);
  assert.equal(changedAccount.wallet.address, null);
  assert.equal(changedAccount.api.csrfToken, null);

  const wrongChain = createWallet({ chainId: "0x1" });
  assert.equal(await wrongChain.wallet.restore(), false);
  assert.equal(wrongChain.wallet.signer, null);

  const disconnected = createWallet({ accounts: [] });
  assert.equal(await disconnected.wallet.restore(), false);
  assert.equal(disconnected.calls.length, 0);

  const startup = [];
  const button = { textContent: "Connect wallet", addEventListener() {} };
  let onReady;
  const appContext = {
    window: {
      GreenCertWallet: {
        address: null,
        role: null,
        async restore() {
          startup.push("restore");
          this.address = account;
          this.role = "Buyer";
          return true;
        },
        shortAddress() { return "0x280d…33ff"; },
      },
      GreenCertPages: { async refresh() { startup.push("refresh"); } },
      ethereum: { on() {} },
    },
    document: {
      addEventListener(name, handler) { if (name === "DOMContentLoaded") onReady = handler; },
      getElementById(id) { return id === "connectWallet" ? button : null; },
    },
  };
  const appSource = fs.readFileSync(path.resolve(__dirname, "../../static/js/app.js"), "utf8");
  vm.runInNewContext(appSource, appContext);
  await onReady();
  assert.deepEqual(startup, ["restore", "refresh"]);
  assert.equal(button.textContent, "0x280d…33ff");

  process.stdout.write("Wallet session restoration checks passed.\n");
}

run().catch((error) => { process.stderr.write(`${error.stack}\n`); process.exitCode = 1; });
