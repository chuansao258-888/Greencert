window.GreenCertContracts = {
  contracts: {},
  // Load the deployed contracts with the connected signer.
  async load(signer) {
    const config = await window.GreenCertApi.get("/config");
    if (!config.configured) throw new Error("Contract deployment is not configured yet.");
    for (const [key, name] of Object.entries({ roleRegistry: "RoleRegistry", certificateRegistry: "CertificateRegistry", certificateMarket: "CertificateMarket" })) {
      const response = await fetch(`/static/contracts/${name}.json`);
      const abi = await response.json();
      this.contracts[key] = new ethers.Contract(config.contracts[key], abi, signer);
    }
    return this.contracts;
  }
};
