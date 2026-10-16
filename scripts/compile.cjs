const fs = require("node:fs");
const path = require("node:path");
const solc = require("solc");

const root = path.resolve(__dirname, "..");
const contractsDir = path.join(root, "contracts");
const artifactsDir = path.join(root, "artifacts");

// Collect Solidity sources with stable relative import paths.
function sourcesFrom(directory, prefix = "") {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const relativePath = path.join(prefix, entry.name);
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) return sourcesFrom(fullPath, relativePath);
    if (!entry.name.endsWith(".sol")) return [];
    return [[relativePath.replaceAll("\\", "/"), { content: fs.readFileSync(fullPath, "utf8") }]];
  });
}

const input = {
  language: "Solidity",
  sources: Object.fromEntries(sourcesFrom(contractsDir)),
  settings: {
    evmVersion: "prague",
    optimizer: { enabled: true, runs: 200 },
    outputSelection: { "*": { "*": ["abi", "evm.bytecode.object"] } }
  }
};

const output = JSON.parse(solc.compile(JSON.stringify(input)));
const errors = (output.errors || []).filter((item) => item.severity === "error");
if (errors.length) {
  console.error(errors.map((item) => item.formattedMessage).join("\n"));
  process.exit(1);
}

fs.rmSync(artifactsDir, { recursive: true, force: true });
fs.mkdirSync(artifactsDir, { recursive: true });
for (const [source, contracts] of Object.entries(output.contracts)) {
  for (const [name, artifact] of Object.entries(contracts)) {
    fs.writeFileSync(
      path.join(artifactsDir, `${name}.json`),
      JSON.stringify({ contractName: name, source, abi: artifact.abi, bytecode: `0x${artifact.evm.bytecode.object}` }, null, 2)
    );
  }
}
console.log(`Compiled ${Object.keys(output.contracts).length} source files.`);
