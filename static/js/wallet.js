window.GreenCertWallet = {
  provider: null,
  signer: null,
  address: null,
  role: null,
  chainId: null,
  targetChainId: null,

  // Build MetaMask's official mobile-browser link for the exact page in view.
  deepLinkUrl() {
    const page = `${window.location.host}${window.location.pathname}${window.location.search}${window.location.hash}`;
    return `https://link.metamask.io/dapp/${encodeURI(page)}`;
  },

  // Read the configured network once per wallet operation.
  async configuration() {
    const config = await window.GreenCertApi.get("/config");
    this.targetChainId = Number(config.chainId);
    return config;
  },

  // Check the wallet's actual network, optionally asking MetaMask to switch it.
  async ensureTargetNetwork({ switchNetwork = false } = {}) {
    if (!window.ethereum) throw new Error("MetaMask is not available in this browser. Open this page in MetaMask to continue.");
    const config = await this.configuration();
    let activeChainId = Number(await window.ethereum.request({ method: "eth_chainId" }));
    if (activeChainId !== this.targetChainId && switchNetwork) {
      const chainId = `0x${this.targetChainId.toString(16)}`;
      try {
        await window.ethereum.request({ method: "wallet_switchEthereumChain", params: [{ chainId }] });
      } catch (error) {
        if (Number(error?.code) === 4902) throw new Error("Sepolia is not configured in MetaMask. Add Sepolia, then try again.");
        throw error;
      }
      activeChainId = Number(await window.ethereum.request({ method: "eth_chainId" }));
    }
    this.chainId = activeChainId;
    if (activeChainId !== this.targetChainId) throw new Error("Switch MetaMask to the Sepolia test network before continuing.");
    return config;
  },

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
    try {
      await this.ensureTargetNetwork();
    } catch (error) {
      return false;
    }
    this.provider = new ethers.BrowserProvider(window.ethereum);
    this.signer = await this.provider.getSigner(accounts[0]);
    this.address = await this.signer.getAddress();
    this.role = session.role;
    window.GreenCertApi.csrfToken = session.csrfToken;
    return true;
  },

  // Connect MetaMask, then validate its actual network before creating a session.
  async connect() {
    if (!window.ethereum) throw new Error("MetaMask is not available in this browser. Open this page in MetaMask to continue.");
    const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
    if (!accounts.length) throw new Error("MetaMask did not provide an account.");
    await this.ensureTargetNetwork({ switchNetwork: true });
    this.provider = new ethers.BrowserProvider(window.ethereum);
    this.signer = await this.provider.getSigner();
    this.address = await this.signer.getAddress();
    const challenge = await window.GreenCertApi.post("/auth/challenge", { address: this.address });
    const signature = await this.signer.signMessage(challenge.message);
    const session = await window.GreenCertApi.post("/auth/verify", { address: this.address, nonce: challenge.nonce, signature });
    window.GreenCertApi.csrfToken = session.csrfToken;
    this.role = session.role;
    return this.address;
  },

  // Recheck on-chain registration before a business operation.
  async requireRegistration() {
    const session = await window.GreenCertApi.get("/auth/me");
    this.role = session.role;
    window.GreenCertApp.renderRole();
    if (!["Producer", "Buyer", "Admin"].includes(this.role)) {
      window.GreenCertApp.openRegistration();
      throw new Error("Register as Producer or Buyer before continuing.");
    }
  },

  // Show a compact wallet address.
  shortAddress() {
    return this.address ? `${this.address.slice(0, 6)}…${this.address.slice(-4)}` : "";
  }
};
