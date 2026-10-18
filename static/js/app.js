window.GreenCertApp = {
  walletRequestActive: false,
  openRegistration() {
    const dialog = document.getElementById("registrationDialog");
    if (window.GreenCertWallet.address && window.GreenCertWallet.role === "None" && dialog && !dialog.open) dialog.showModal();
  },
  // Show the role read from the authenticated session's on-chain lookup.
  renderRole() {
    const label = document.getElementById("walletRole");
    const registration = document.getElementById("roleRegistration");
    const wallet = window.GreenCertWallet;
    const unregistered = wallet.role === "None";
    if (label) label.textContent = wallet.address ? (unregistered ? "Role: Not registered" : `Role: ${wallet.role}`) : "";
    if (registration) registration.hidden = !wallet.address || !unregistered;
    const dialog = document.getElementById("registrationDialog");
    if (!unregistered && dialog?.open) dialog.close();
  },
  // Display a short status message above the current page.
  notice(message, error = false) {
    const registrationNotice = document.getElementById("registrationNotice");
    if (registrationNotice) {
      registrationNotice.textContent = message;
      registrationNotice.classList.toggle("error", error);
      registrationNotice.hidden = false;
    }
    const notice = document.getElementById("notice");
    if (!notice) return;
    notice.textContent = message;
    notice.hidden = false;
    notice.classList.toggle("error", error);
    notice.scrollIntoView?.({ behavior: "smooth", block: "center" });
  },
  // Convert nested provider errors into the action the wallet user can take.
  walletError(error) {
    const seen = new Set();
    const inspect = (value) => {
      if (!value || typeof value !== "object" || seen.has(value)) return null;
      seen.add(value);
      if (Number(value.code) === -32002) return "MetaMask already has a request waiting. Open MetaMask and approve or reject it before trying again.";
      if (Number(value.code) === 4001 || /user rejected|user denied/i.test(String(value.message || ""))) return "The request was rejected in MetaMask.";
      for (const key of ["error", "info", "data", "cause"]) {
        const result = inspect(value[key]);
        if (result) return result;
      }
      return null;
    };
    return inspect(error) || error?.shortMessage || error?.message || "Wallet request failed.";
  },
  // Lock one visible control while a wallet request is in progress.
  async withWalletRequest(button, work) {
    if (this.walletRequestActive) throw new Error("Another wallet request is already in progress. Finish it in MetaMask before trying again.");
    this.walletRequestActive = true;
    if (button) {
      button.disabled = true;
      button.setAttribute?.("aria-busy", "true");
    }
    try {
      return await work();
    } finally {
      this.walletRequestActive = false;
      if (button) {
        button.disabled = false;
        button.removeAttribute?.("aria-busy");
      }
    }
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
  window.GreenCertApp.renderRole();
  const connectButton = document.getElementById("connectWallet");
  if (connectButton) connectButton.textContent = window.GreenCertWallet.shortAddress();
  const status = document.getElementById("walletStatus");
  if (status) status.textContent = `Connected as ${window.GreenCertWallet.shortAddress()}`;
  const addressDetails = document.getElementById("walletAddressDetails");
  const fullAddress = document.getElementById("walletFullAddress");
  if (addressDetails && fullAddress) {
    fullAddress.textContent = window.GreenCertWallet.address;
    addressDetails.hidden = false;
  }
}

// Show the wallet's actual chain rather than only the application's target chain.
async function refreshNetworkBadge() {
  const badge = document.getElementById("networkBadge");
  const switchButton = document.getElementById("switchNetwork");
  if (!badge) return;
  if (!window.ethereum) {
    badge.textContent = "Sepolia · MetaMask needed";
    badge.classList.add("wrong-network");
    if (switchButton) switchButton.hidden = true;
    return;
  }
  try {
    const config = await GreenCertWallet.configuration();
    const activeChainId = Number(await window.ethereum.request({ method: "eth_chainId" }));
    const correct = activeChainId === Number(config.chainId);
    badge.textContent = correct ? "Wallet: Sepolia" : "Wallet: wrong network";
    badge.classList.toggle("wrong-network", !correct);
    if (switchButton) switchButton.hidden = correct;
  } catch (error) {
    badge.textContent = "Wallet network unavailable";
    badge.classList.add("wrong-network");
    if (switchButton) switchButton.hidden = true;
  }
}

function setupMobileWalletEntry() {
  if (window.ethereum) return;
  const help = document.getElementById("walletHelp");
  const open = document.getElementById("openMetaMask");
  const copy = document.getElementById("copyPageLink");
  if (!help || !open || !copy) return;
  help.hidden = false;
  open.href = GreenCertWallet.deepLinkUrl();
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      GreenCertApp.notice("Page link copied. Open it from MetaMask’s browser.");
    } catch (error) {
      GreenCertApp.notice("Copy the address from your browser and open it from MetaMask’s browser.", true);
    }
  });
}

// Restore the existing session before loading wallet-specific page data.
document.addEventListener("DOMContentLoaded", async () => {
  const connectButton = document.getElementById("connectWallet");
  const switchButton = document.getElementById("switchNetwork");
  connectButton?.addEventListener("click", async () => {
    try {
      if (!window.ethereum) {
        window.location.assign(GreenCertWallet.deepLinkUrl());
        return;
      }
      await GreenCertApp.withWalletRequest(connectButton, async () => {
        GreenCertApp.notice("Requesting MetaMask account access.");
        await window.GreenCertWallet.connect();
        showConnectedWallet();
        GreenCertApp.openRegistration();
        await refreshNetworkBadge();
        await window.GreenCertPages?.refresh();
        window.GreenCertApp.notice(`Connected as ${window.GreenCertWallet.shortAddress()}.`);
      });
    } catch (error) {
      window.GreenCertApp.notice(GreenCertApp.walletError(error), true);
    }
  });
  switchButton?.addEventListener("click", async () => {
    try {
      await GreenCertApp.withWalletRequest(switchButton, async () => {
        GreenCertApp.notice("Requesting a switch to the Sepolia test network.");
        await GreenCertWallet.ensureTargetNetwork({ switchNetwork: true });
        await refreshNetworkBadge();
        GreenCertApp.notice("MetaMask is now on Sepolia.");
      });
    } catch (error) {
      GreenCertApp.notice(GreenCertApp.walletError(error), true);
    }
  });
  window.ethereum?.on?.("accountsChanged", (accounts) => {
    if (window.GreenCertWallet.address && accounts[0]?.toLowerCase() !== window.GreenCertWallet.address.toLowerCase()) window.location.reload();
  });
  window.ethereum?.on?.("chainChanged", () => {
    if (window.GreenCertWallet.address) window.location.reload();
  });
  setupMobileWalletEntry();
  await refreshNetworkBadge();
  try {
    if (await window.GreenCertWallet.restore()) {
      showConnectedWallet();
      GreenCertApp.openRegistration();
      await window.GreenCertTransactions?.resumePending();
    }
  } catch (error) {
    window.GreenCertApp.notice(error.message || "Wallet session could not be restored.", true);
  }
  await window.GreenCertPages?.refresh();
});
