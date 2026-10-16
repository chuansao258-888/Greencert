window.GreenCertWallet = {
  provider: null,
  signer: null,
  address: null,
  role: null,

  // Restore a valid server session for the wallet currently selected in MetaMask.
  async restore() {
    if (!window.ethereum) return false;
    const accounts = await window.ethereum.request({ method: "eth_accounts" });
    if (!accounts.length) return false;
    let session;
    try {
      session = await window.GreenCertApi.get("/auth/me");
    } catch (error) {
      return false;
    }
    if (accounts[0].toLowerCase() !== session.address.toLowerCase()) return false;
    const config = await window.GreenCertApi.get("/config");
    const activeChain = await window.ethereum.request({ method: "eth_chainId" });
    if (Number(activeChain) !== Number(config.chainId)) return false;
    this.provider = new ethers.BrowserProvider(window.ethereum);
    this.signer = await this.provider.getSigner(accounts[0]);
    this.address = await this.signer.getAddress();
    this.role = session.role;
    window.GreenCertApi.csrfToken = session.csrfToken;
    return true;
  },

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
