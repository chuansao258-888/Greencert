window.GreenCertTransactions = {
  // Submit one wallet transaction and wait for its receipt.
  async send(label, action) {
    window.GreenCertApp.notice(`${label}: confirm the request in MetaMask.`);
    const transaction = await action();
    window.GreenCertApp.notice(`${label}: waiting for confirmation.`);
    const receipt = await transaction.wait();
    if (receipt.status !== 1) throw new Error(`${label} failed on-chain.`);
    await GreenCertApi.post("/transactions/verify", { txHash: transaction.hash });
    window.GreenCertApp.notice(`${label}: confirmed.`);
    return transaction;
  }
};
