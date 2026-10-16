const fs = require("node:fs");
const path = require("node:path");
const solc = require("solc");

const root = path.resolve(__dirname, "..");

// Collect contract and test sources for a single compiler run.
function collect(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) return collect(fullPath);
    if (!entry.name.endsWith(".sol")) return [];
    return [[path.relative(root, fullPath).replaceAll("\\", "/"), { content: fs.readFileSync(fullPath, "utf8") }]];
  });
}

const input = {
  language: "Solidity",
  sources: {
    ...Object.fromEntries([...collect(path.join(root, "contracts")), ...collect(path.join(root, "tests", "contracts"))]),
    "remix_tests.sol": {
      content: "pragma solidity ^0.8.20; library Assert { event AssertionEvent(bool result, string message, string method); function ok(bool condition, string memory message) internal returns (bool) { emit AssertionEvent(condition, message, 'ok'); return condition; } }"
    }
  },
  settings: { evmVersion: "prague", optimizer: { enabled: true, runs: 200 }, outputSelection: { "*": { "*": ["abi"] } } }
};
const output = JSON.parse(solc.compile(JSON.stringify(input)));
const errors = (output.errors || []).filter((item) => item.severity === "error");
if (errors.length) {
  console.error(errors.map((item) => item.formattedMessage).join("\n"));
  process.exit(1);
}
console.log("Contract test sources compiled successfully.");
