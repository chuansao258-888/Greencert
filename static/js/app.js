window.GreenCertApp = {
  notice(message, error = false) {
    const notice = document.getElementById("notice");
    if (!notice) return;
    notice.textContent = message;
    notice.hidden = false;
    notice.classList.toggle("error", error);
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const connectButton = document.getElementById("connectWallet");
  connectButton?.addEventListener("click", async () => {
    try {
      const address = await window.GreenCertWallet.connect();
      connectButton.textContent = window.GreenCertWallet.shortAddress();
      const status = document.getElementById("walletStatus");
      if (status) status.textContent = `Connected: ${address}`;
      document.getElementById("rolePanel")?.removeAttribute("hidden");
      window.GreenCertApp.notice("Wallet connected. Configure deployed contracts to register a role.");
    } catch (error) {
      window.GreenCertApp.notice(error.message || "Wallet connection failed.", true);
    }
  });
});
