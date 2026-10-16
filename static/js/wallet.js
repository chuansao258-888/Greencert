window.GreenCertWallet = {
  provider: null,
  signer: null,
  address: null,

  async connect() {
    if (!window.ethereum) throw new Error("Install MetaMask to connect a wallet.");
    this.provider = new ethers.BrowserProvider(window.ethereum);
    await this.provider.send("eth_requestAccounts", []);
    this.signer = await this.provider.getSigner();
    this.address = await this.signer.getAddress();
    return this.address;
  },

  shortAddress() {
    return this.address ? `${this.address.slice(0, 6)}…${this.address.slice(-4)}` : "";
  }
};
