const fs = require('node:fs');
const path = require('node:path');
const solc = require('solc');
const ganache = require('ganache');
const { ethers } = require('ethers');

const root = path.resolve(__dirname, '..');

function collect(directory, prefix = '') {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const relative = path.join(prefix, entry.name);
    const full = path.join(directory, entry.name);
    if (entry.isDirectory()) return collect(full, relative);
    return entry.name.endsWith('.sol')
      ? [[relative.replaceAll('\\', '/'), { content: fs.readFileSync(full, 'utf8') }]]
      : [];
  });
}

function compile() {
  const input = {
    language: 'Solidity',
    sources: Object.fromEntries(collect(path.join(root, 'contracts'))),
    settings: {
      evmVersion: 'shanghai',
      optimizer: { enabled: true, runs: 200 },
      outputSelection: { '*': { '*': ['abi', 'evm.bytecode.object'] } }
    }
  };
  const output = JSON.parse(solc.compile(JSON.stringify(input)));
  const errors = (output.errors || []).filter((item) => item.severity === 'error');
  if (errors.length) throw new Error(errors.map((item) => item.formattedMessage).join('\n'));
  return output.contracts;
}

async function main() {
  const contracts = compile();
  const chain = ganache.provider({
    logging: { quiet: true },
    chain: { hardfork: 'shanghai' },
    wallet: { defaultBalance: 1000 }
  });
  const provider = new ethers.BrowserProvider(chain);
  const admin = await provider.getSigner(0);
  const producer = await provider.getSigner(1);
  const buyer = await provider.getSigner(2);

  function factory(source, name, signer) {
    const artifact = contracts[source][name];
    return new ethers.ContractFactory(artifact.abi, artifact.evm.bytecode.object, signer);
  }

  const roles = await factory('RoleRegistry.sol', 'RoleRegistry', admin).deploy(await admin.getAddress());
  await roles.waitForDeployment();
  const registry = await factory('CertificateRegistry.sol', 'CertificateRegistry', admin).deploy(await roles.getAddress());
  await registry.waitForDeployment();
  const market = await factory('CertificateMarket.sol', 'CertificateMarket', admin).deploy(await roles.getAddress(), await registry.getAddress());
  await market.waitForDeployment();

  const rows = [];
  async function record(name, transactionPromise) {
    const receipt = await (await transactionPromise).wait();
    if (receipt.status !== 1) throw new Error(`${name} failed`);
    rows.push({ name, gasUsed: receipt.gasUsed.toString(), status: receipt.status });
  }

  await record('Set market', registry.connect(admin).setMarket(await market.getAddress()));
  await record('Register producer', roles.connect(producer).register(1));
  await record('Register buyer', roles.connect(buyer).register(2));

  const now = BigInt((await provider.getBlock('latest')).timestamp);
  const site = ethers.keccak256(ethers.toUtf8Bytes('SC6113-current-site'));
  const metadata = ethers.keccak256(ethers.toUtf8Bytes('SC6113-current-metadata'));
  await record('Submit application', registry.connect(producer).submitApplication(site, now - 2000n, now - 1000n, 1, 5, metadata));
  await record('Approve application', registry.connect(admin).approveApplication(1));
  await record('List certificate', market.connect(producer).listCertificate(1, 100000n));
  await record('Update listing price', market.connect(producer).updatePrice(1, 200000n));
  await record('Cancel listing', market.connect(producer).cancelListing(1));
  await record('Relist certificate', market.connect(producer).listCertificate(1, 100000n));
  await record('Buy certificate', market.connect(buyer).buyCertificate(1, 100000n, { value: 100000n }));
  await record('Withdraw proceeds', market.connect(producer).withdraw());
  await record('Retire certificate', registry.connect(buyer).retireCertificate(1, ethers.keccak256(ethers.toUtf8Bytes('SC6113-current-retirement'))));

  await record('Submit withdrawal application', registry.connect(producer).submitApplication(site, now - 4000n, now - 3000n, 2, 2, ethers.keccak256(ethers.toUtf8Bytes('withdraw'))));
  await record('Withdraw application', registry.connect(producer).withdrawApplication(2));
  await record('Submit rejection application', registry.connect(producer).submitApplication(site, now - 6000n, now - 5000n, 3, 3, ethers.keccak256(ethers.toUtf8Bytes('reject'))));
  await record('Reject application', registry.connect(admin).rejectApplication(3, ethers.keccak256(ethers.toUtf8Bytes('reason'))));

  const certificate = await registry.getCertificate(1);
  const withdrawalApplication = await registry.getApplication(2);
  const rejectedApplication = await registry.getApplication(3);
  if (certificate.status !== 2n || withdrawalApplication.status !== 4n || rejectedApplication.status !== 3n) {
    throw new Error('Final state checks failed');
  }

  const total = rows.reduce((sum, row) => sum + BigInt(row.gasUsed), 0n);
  const csv = ['transaction,gas_used,status', ...rows.map((row) => `${row.name},${row.gasUsed},${row.status}`), `Total,${total},success`].join('\n') + '\n';
  const output = path.join(root, 'submission', 'gas', 'gas-results.csv');
  fs.writeFileSync(output, csv);
  console.log(`PASS ${rows.length} current-contract transactions; total gas ${total}; solc ${solc.version()}; local Ganache Shanghai EVM`);
  console.log(output);
  await chain.disconnect();
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
