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

// Show the authenticated wallet on every page.
function showConnectedWallet() {
  const connectButton = document.getElementById("connectWallet");
  if (connectButton) connectButton.textContent = window.GreenCertWallet.shortAddress();
  const status = document.getElementById("walletStatus");
  if (status) status.textContent = `Connected: ${window.GreenCertWallet.address}`;
  const rolePanel = document.getElementById("rolePanel");
  if (rolePanel) rolePanel.hidden = window.GreenCertWallet.role !== "None";
}

// Restore the existing session before loading wallet-specific page data.
document.addEventListener("DOMContentLoaded", async () => {
  const connectButton = document.getElementById("connectWallet");
  connectButton?.addEventListener("click", async () => {
    try {
      await window.GreenCertWallet.connect();
      showConnectedWallet();
      await window.GreenCertPages?.refresh();
      window.GreenCertApp.notice(`Connected as ${window.GreenCertWallet.role}.`);
    } catch (error) {
      window.GreenCertApp.notice(error.message || "Wallet connection failed.", true);
    }
  });
  window.ethereum?.on?.("accountsChanged", (accounts) => {
    if (window.GreenCertWallet.address && accounts[0]?.toLowerCase() !== window.GreenCertWallet.address.toLowerCase()) window.location.reload();
  });
  window.ethereum?.on?.("chainChanged", () => {
    if (window.GreenCertWallet.address) window.location.reload();
  });
  try {
    if (await window.GreenCertWallet.restore()) showConnectedWallet();
  } catch (error) {
    window.GreenCertApp.notice(error.message || "Wallet session could not be restored.", true);
  }
  await window.GreenCertPages?.refresh();
});
