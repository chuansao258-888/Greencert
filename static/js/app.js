window.GreenCertApp = {
  // Display a short status message above the current page.
  notice(message, error = false) {
    const notice = document.getElementById("notice");
    if (!notice) return;
    notice.textContent = message;
    notice.hidden = false;
    notice.classList.toggle("error", error);
  },
  // Escape user-controlled text before adding it to a card.
  escape(value) {
    return String(value ?? "").replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);
  },
  // Format a wei value as test ETH.
  eth(value) {
    return `${ethers.formatEther(value || "0")} ETH`;
  }
};

// Connect the shared wallet button and refresh the active page.
document.addEventListener("DOMContentLoaded", () => {
  const connectButton = document.getElementById("connectWallet");
  connectButton?.addEventListener("click", async () => {
    try {
      const address = await window.GreenCertWallet.connect();
      connectButton.textContent = window.GreenCertWallet.shortAddress();
      const status = document.getElementById("walletStatus");
      if (status) status.textContent = `Connected: ${address}`;
      if (document.getElementById("rolePanel") && window.GreenCertWallet.role === "None") document.getElementById("rolePanel").hidden = false;
      await window.GreenCertPages?.refresh();
      window.GreenCertApp.notice(`Connected as ${window.GreenCertWallet.role}.`);
    } catch (error) {
      window.GreenCertApp.notice(error.message || "Wallet connection failed.", true);
    }
  });
  window.GreenCertPages?.refresh();
});
