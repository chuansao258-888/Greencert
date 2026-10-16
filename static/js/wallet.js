window.GreenCertWallet = {
  provider: null,
  signer: null,
  address: null,

  // Connect MetaMask and select the expected test network.
  async connect() {
    if (!window.ethereum) throw new Error("Install MetaMask to connect a wallet.");
    const config = await window.GreenCertApi.get("/config");
    const chainId = `0x${config.chainId.toString(16)}`;
    await window.ethereum.request({ method: "wallet_switchEthereumChain", params: [{ chainId }] });
    this.provider = new ethers.BrowserProvider(window.ethereum);
    await this.provider.send("eth_requestAccounts", []);
    this.signer = await this.provider.getSigner();
    this.address = await this.signer.getAddress();
    const challenge = await window.GreenCertApi.post("/auth/challenge", { address: this.address });
    const signature = await this.signer.signMessage(challenge.message);
    const session = await window.GreenCertApi.post("/auth/verify", { address: this.address, nonce: challenge.nonce, signature });
    window.GreenCertApi.csrfToken = session.csrfToken;
    this.role = session.role;
    return this.address;
  },

  // Show a compact wallet address.
  shortAddress() {
    return this.address ? `${this.address.slice(0, 6)}…${this.address.slice(-4)}` : "";
  }
};
