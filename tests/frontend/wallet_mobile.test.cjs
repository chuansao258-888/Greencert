const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.resolve(__dirname, "../../static/js/wallet.js"), "utf8");
const context = {
  window: {
    location: { host: "greencert.onrender.com", pathname: "/certificates/2", search: "?source=market", hash: "#record" },
    GreenCertApi: { async get() { return { chainId: 11155111 }; } },
  },
  encodeURI,
};
vm.runInNewContext(source, context);

assert.equal(
  context.window.GreenCertWallet.deepLinkUrl(),
  "https://link.metamask.io/dapp/greencert.onrender.com/certificates/2?source=market#record",
);

process.stdout.write("MetaMask mobile deep-link check passed.\n");
