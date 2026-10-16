window.GreenCertTransactions = {
  async send(label, action) {
    window.GreenCertApp.notice(`${label}: confirm the request in MetaMask.`);
    const transaction = await action();
    window.GreenCertApp.notice(`${label}: waiting for confirmation.`);
    await transaction.wait();
    window.GreenCertApp.notice(`${label}: confirmed.`);
    return transaction;
  }
};
