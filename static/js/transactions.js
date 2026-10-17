window.GreenCertTransactions = {
  pendingStorageKey: "greencert.pendingTransactions",
  // Preserve submitted hashes across a reload; a hash is not permission to resend it.
  pendingHashes() {
    try {
      const saved = JSON.parse(window.localStorage?.getItem(this.pendingStorageKey) || "[]");
      return Array.isArray(saved) ? saved.filter((hash) => /^0x[0-9a-fA-F]{64}$/.test(hash)) : [];
    } catch (error) {
      return [];
    }
  },
  savePendingHash(txHash) {
    try {
      const hashes = this.pendingHashes();
      if (!hashes.includes(txHash)) window.localStorage?.setItem(this.pendingStorageKey, JSON.stringify([...hashes, txHash]));
    } catch (error) {
      // Browser storage is supplementary; the wallet still retains the submitted transaction.
    }
  },
  clearPendingHash(txHash) {
    try {
      window.localStorage?.setItem(this.pendingStorageKey, JSON.stringify(this.pendingHashes().filter((hash) => hash !== txHash)));
    } catch (error) {
      // No business state depends on browser storage.
    }
  },
  // Ask the server to update receipts for hashes retained after an earlier timeout.
  async resumePending() {
    for (const txHash of this.pendingHashes()) {
      try {
        const record = await GreenCertApi.post("/transactions/verify", { txHash });
        if (record.status !== "pending") this.clearPendingHash(txHash);
      } catch (error) {
        // Keep the hash for a later refresh when the RPC provider can see it.
      }
    }
  },
  // Submit one wallet transaction, preserve its hash, then verify its receipt and event.
  async send(label, action) {
    await GreenCertWallet.ensureTargetNetwork();
    if (!GreenCertWallet.address || !GreenCertWallet.signer) throw new Error("Connect and authorize a MetaMask account first.");
    window.GreenCertApp.notice(`${label}: checking wallet and preparing the transaction.`);
    let transaction;
    try {
      window.GreenCertApp.notice(`${label}: waiting for MetaMask approval.`);
      transaction = await action();
    } catch (error) {
      throw new Error(window.GreenCertApp.walletError(error));
    }
    this.savePendingHash(transaction.hash);
    try {
      await GreenCertApi.post("/transactions/verify", { txHash: transaction.hash });
    } catch (error) {
      // The chain transaction remains valid even if the supporting activity record is delayed.
    }
    window.GreenCertApp.notice(`${label}: submitted. Waiting for a Sepolia confirmation.`);
    let receipt;
    try {
      receipt = await transaction.wait(1, 180000);
    } catch (error) {
      if (transaction.hash && (error?.code === "TIMEOUT" || /timeout/i.test(error?.message || ""))) {
        const message = `${label}: transaction ${transaction.hash} is still pending. Do not submit it again; check MetaMask or Etherscan and refresh this page later.`;
        window.GreenCertApp.notice(message, true);
        throw new Error(message);
      }
      throw new Error(window.GreenCertApp.walletError(error));
    }
    if (receipt.status !== 1) throw new Error(`${label} failed on-chain.`);
    window.GreenCertApp.notice(`${label}: receipt confirmed. Verifying the contract event.`);
    try {
      await GreenCertApi.post("/transactions/verify", { txHash: transaction.hash });
      this.clearPendingHash(transaction.hash);
      window.GreenCertApp.notice(`${label}: confirmed and recorded.`);
    } catch (error) {
      window.GreenCertApp.notice(`${label}: receipt confirmed. Server verification will retry when the page refreshes.`);
    }
    return transaction;
  }
};
