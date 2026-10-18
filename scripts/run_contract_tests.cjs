// Execute the Remix-style Solidity tests on an isolated local EVM.
// Assert.ok is made reverting so a failed assertion fails the transaction.
const fs = require('node:fs');
const path = require('node:path');
const solc = require('solc');
const ganache = require('ganache');
const { ethers } = require('ethers');
const root = path.resolve(__dirname, '..');
function collect(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(e => {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) return collect(full);
    return e.name.endsWith('.sol') ? [[path.relative(root, full).replaceAll('\\', '/'), {content: fs.readFileSync(full, 'utf8')}]] : [];
  });
}
const input = {language:'Solidity', sources:{
  ...Object.fromEntries([...collect(path.join(root, 'contracts')), ...collect(path.join(root, 'tests', 'contracts'))]),
  'remix_tests.sol':{content:'pragma solidity ^0.8.20; library Assert { function ok(bool condition, string memory message) internal pure returns (bool) { require(condition, message); return condition; } }'}
}, settings:{evmVersion:'shanghai', optimizer:{enabled:true,runs:200}, outputSelection:{'*':{'*':['abi','evm.bytecode.object']}}}};
const compiled = JSON.parse(solc.compile(JSON.stringify(input)));
const errors = (compiled.errors || []).filter(e => e.severity === 'error');
if (errors.length) throw new Error(errors.map(e => e.formattedMessage).join('\n'));
async function main() {
  const server = ganache.provider({logging:{quiet:true}, chain:{hardfork:'shanghai',allowUnlimitedContractSize:true,allowUnlimitedInitCodeSize:true}, miner:{blockGasLimit:100000000}, wallet:{defaultBalance:1000}});
  const provider = new ethers.BrowserProvider(server);
  const signer = await provider.getSigner();
  let passed = 0, failed = 0;
  for (const suite of ['RoleRegistry','CertificateRegistry','CertificateMarket']) {
    const contract = compiled.contracts[`tests/contracts/${suite}_test.sol`][`${suite}Test`];
    for (const fn of contract.abi.filter(x => x.type === 'function' && x.name.startsWith('test_'))) {
      try {
        const instance = await new ethers.ContractFactory(contract.abi, contract.evm.bytecode.object, signer).deploy({gasLimit:80000000});
        await instance.waitForDeployment();
        const options = {gasLimit:80000000};
        if (fn.stateMutability === 'payable') options.value = 100n;
        const receipt = await (await instance[fn.name](options)).wait();
        if (receipt.status !== 1) throw new Error('receipt status is not 1');
        console.log(`PASS ${suite}.${fn.name}`); passed++;
      } catch (e) { console.error(`FAIL ${suite}.${fn.name}: ${e.shortMessage || e.message}`); failed++; }
    }
  }
  console.log(`RESULT ${passed} passed, ${failed} failed; solc ${solc.version()}; local Ganache Shanghai EVM`);
  await server.disconnect();
  if (failed) process.exitCode = 1;
}
main().catch(e => { console.error(e); process.exitCode=1; });
