window.GreenCertContracts = {
  roleRegistry: null,
  async loadRoleRegistry(provider, address) {
    const response = await fetch("/static/contracts/RoleRegistry.json");
    const abi = await response.json();
    this.roleRegistry = new ethers.Contract(address, abi, provider);
    return this.roleRegistry;
  }
};
