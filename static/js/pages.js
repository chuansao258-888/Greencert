window.GreenCertPages = {
  // Refresh data for the page currently on screen.
  async refresh() {
    try {
      if (document.getElementById("statIssued")) {
        const totals = await GreenCertApi.get("/dashboard");
        for (const name of ["Issued", "Listed", "Sold", "Retired"]) document.getElementById(`stat${name}`).textContent = totals[name.toLowerCase()];
      }
      if (document.getElementById("marketList")) await this.market();
      if (GreenCertWallet.address && document.getElementById("applicationList")) await this.applications();
      if (GreenCertWallet.address && document.getElementById("ownedList")) await this.owned();
      if (GreenCertWallet.address && document.getElementById("walletPanel")) await this.wallet();
      if (GreenCertWallet.address && document.getElementById("activityList")) await this.activity();
    } catch (error) {
      if (!error.message.includes("not configured")) GreenCertApp.notice(error.message, true);
    }
  },
  // Show available batches and their whole-batch prices.
  async market() {
    const items = await GreenCertApi.get("/certificates?listed=true");
    document.getElementById("marketList").innerHTML = items.length ? items.map((item) =>
      `<article class="record-card"><h2>${GreenCertApp.escape(item.metadata?.siteName || "Metadata unavailable")}</h2><p>${GreenCertApp.escape(item.metadata?.source || "Unknown")} · ${item.quantity} RECs / ${item.quantity} MWh</p><p>Total price: ${GreenCertApp.eth(item.listing.totalPriceWei)}</p><p>Certificate #${item.id}</p><div class="button-row"><button class="button primary" data-action="buy" data-id="${item.id}" data-price="${item.listing.totalPriceWei}">Buy whole batch</button></div></article>`
    ).join("") : "<div class='empty-state'><h2>No listings yet</h2></div>";
  },
  // Show the connected Producer's applications or the Admin queue.
  async applications() {
    const role = GreenCertWallet.role;
    document.getElementById("applicationFormPanel").hidden = role !== "Producer";
    if (!["Producer", "Admin"].includes(role)) return;
    const items = await GreenCertApi.get("/applications");
    document.getElementById("applicationList").innerHTML = items.length ? items.reverse().map((item) => {
      const actions = item.status !== "Pending" ? "" : role === "Admin"
        ? `<button class="button primary" data-action="approve" data-id="${item.id}">Approve</button><button class="button secondary" data-action="reject" data-id="${item.id}">Reject</button>`
        : `<button class="button secondary" data-action="withdraw" data-id="${item.id}">Withdraw</button>`;
      return `<article class="record-card"><h2>Application #${item.id}</h2><p>${item.status} · ${item.quantity} RECs</p><p>Producer: ${GreenCertApp.escape(item.producer)}</p><div class="button-row"><button class="button secondary" data-action="details" data-id="${item.id}">View evidence</button>${actions}</div></article>`;
    }).join("") : "<div class='empty-state'><h2>No applications</h2></div>";
  },
  // Show owned certificates and their available actions.
  async owned() {
    const items = await GreenCertApi.get(`/certificates?owner=${GreenCertWallet.address}`);
    document.getElementById("ownedList").innerHTML = items.length ? items.reverse().map((item) => {
      let actions = "";
      if (item.status === "Active" && GreenCertWallet.role === "Producer") actions = item.listed
        ? `<button class="button secondary" data-action="reprice" data-id="${item.id}">Change price</button><button class="button secondary" data-action="cancel" data-id="${item.id}">Cancel listing</button>`
        : `<button class="button primary" data-action="list" data-id="${item.id}">List batch</button>`;
      if (item.status === "Active" && GreenCertWallet.role === "Buyer") actions = `<button class="button primary" data-action="retire" data-id="${item.id}">Retire whole batch</button>`;
      return `<article class="record-card"><h2>Certificate #${item.id}</h2><p>${GreenCertApp.escape(item.metadata?.siteName || "Metadata unavailable")} · ${item.quantity} RECs</p><p>${item.status}${item.listed ? " · Listed" : ""}</p>${item.listed ? `<p>Total price: ${GreenCertApp.eth(item.listing.totalPriceWei)}</p>` : ""}<div class="button-row">${actions}</div></article>`;
    }).join("") : "<div class='empty-state'><h2>No certificates owned</h2></div>";
  },
  // Display the connected wallet's balance and sale proceeds.
  async wallet() {
    const data = await GreenCertApi.get("/wallet");
    document.getElementById("walletPanel").hidden = false;
    document.getElementById("walletBalance").textContent = `Balance: ${GreenCertApp.eth(data.balanceWei)}`;
    document.getElementById("walletProceeds").textContent = `Claimable sales: ${GreenCertApp.eth(data.claimableWei)}`;
    document.getElementById("withdrawProceeds").disabled = BigInt(data.claimableWei) === 0n;
  },
  // Show saved transaction receipts for this wallet.
  async activity() {
    const items = await GreenCertApi.get("/transactions");
    document.getElementById("activityList").innerHTML = items.length ? items.map((item) =>
      `<article class="record-card"><h2>${GreenCertApp.escape(item.method)}</h2><p>${GreenCertApp.escape(item.status)} · gas used ${GreenCertApp.escape(item.gas_used || "pending")}</p><p>${GreenCertApp.escape(item.tx_hash)}</p></article>`
    ).join("") : "<div class='empty-state'><h2>No verified transactions yet</h2></div>";
  },
  // Upload evidence and submit its certificate application.
  async submitApplication(form) {
    const values = new FormData(form);
    const evidence = await GreenCertApi.upload(values.get("evidence"));
    const payload = Object.fromEntries(["siteCode", "siteName", "source", "country", "batchIndex", "quantity"].map((key) => [key, values.get(key)]));
    payload.periodStart = String(Math.floor(new Date(`${values.get("periodStart")}T00:00:00Z`).getTime() / 1000));
    payload.periodEnd = String(Math.floor(new Date(`${values.get("periodEnd")}T23:59:59Z`).getTime() / 1000));
    payload.proofFileId = evidence.fileId;
    const content = await GreenCertApi.post("/content", { kind: "application", payload });
    if (ethers.keccak256(ethers.toUtf8Bytes(content.canonicalJson)) !== content.contentHash) throw new Error("Metadata hash does not match.");
    const args = content.chainArgs;
    await GreenCertTransactions.send("Submit application", () => GreenCertContracts.contracts.certificateRegistry.submitApplication(args.siteHash, args.periodStart, args.periodEnd, args.batchIndex, args.quantity, args.metadataHash));
    form.reset();
    await this.refresh();
  },
  // Execute one application, market or retirement action.
  async action(name, id, button) {
    const market = GreenCertContracts.contracts.certificateMarket;
    const registry = GreenCertContracts.contracts.certificateRegistry;
    if (!market || !registry) throw new Error("Connect a wallet first.");
    if (name === "details") {
      const item = await GreenCertApi.get(`/applications/${id}`);
      const metadata = item.metadata || {};
      const summary = `${metadata.siteName || "Metadata unavailable"} · ${metadata.source || "Unknown"} · ${item.quantity} RECs`;
      GreenCertApp.notice(summary);
      if (item.evidenceFileId) window.open(`/api/files/${encodeURIComponent(item.evidenceFileId)}`, "_blank", "noopener");
      return;
    }
    if (name === "approve") await GreenCertTransactions.send("Approve application", () => registry.approveApplication(id));
    if (name === "withdraw") await GreenCertTransactions.send("Withdraw application", () => registry.withdrawApplication(id));
    if (name === "buy") {
      const price = button.dataset.price;
      await GreenCertTransactions.send("Buy certificate", () => market.buyCertificate(id, price, { value: price }));
    }
    if (name === "list" || name === "reprice") {
      const input = prompt("Total price for the whole batch in ETH:");
      if (!input) return;
      const price = ethers.parseEther(input);
      if (price <= 0n) throw new Error("Price must be greater than zero.");
      await GreenCertTransactions.send(name === "list" ? "List certificate" : "Update price", () => name === "list" ? market.listCertificate(id, price) : market.updatePrice(id, price));
    }
    if (name === "cancel") await GreenCertTransactions.send("Cancel listing", () => market.cancelListing(id));
    if (name === "reject" || name === "retire") {
      const payload = name === "reject"
        ? { applicationId: id, reason: prompt("Reason for rejection:") }
        : { certificateId: id, beneficiary: prompt("Retirement beneficiary:"), purpose: prompt("Retirement purpose:") };
      if (Object.values(payload).some((value) => !value)) return;
      const kind = name === "reject" ? "rejection" : "retirement";
      const content = await GreenCertApi.post("/content", { kind, payload });
      if (ethers.keccak256(ethers.toUtf8Bytes(content.canonicalJson)) !== content.contentHash) throw new Error("Metadata hash does not match.");
      await GreenCertTransactions.send(name === "reject" ? "Reject application" : "Retire certificate", () =>
        name === "reject" ? registry.rejectApplication(id, content.chainArgs.reasonHash) : registry.retireCertificate(id, content.chainArgs.retirementHash));
    }
    await this.refresh();
  }
};

// Bind buttons for role registration and certificate actions.
document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-register-role], [data-action], #withdrawProceeds");
  if (!button) return;
  try {
    if (!GreenCertWallet.signer) throw new Error("Connect a wallet first.");
    if (!GreenCertContracts.contracts.roleRegistry) await GreenCertContracts.load(GreenCertWallet.signer);
    if (button.dataset.registerRole) {
      await GreenCertTransactions.send("Register role", () => GreenCertContracts.contracts.roleRegistry.register(Number(button.dataset.registerRole)));
      GreenCertWallet.role = Number(button.dataset.registerRole) === 1 ? "Producer" : "Buyer";
      document.getElementById("rolePanel").hidden = true;
    } else if (button.id === "withdrawProceeds") {
      await GreenCertTransactions.send("Withdraw proceeds", () => GreenCertContracts.contracts.certificateMarket.withdraw());
    } else {
      await GreenCertPages.action(button.dataset.action, button.dataset.id, button);
    }
    await GreenCertPages.refresh();
  } catch (error) {
    GreenCertApp.notice(error.message || "Transaction failed.", true);
  }
});

// Submit the Producer's application form.
document.addEventListener("submit", async (event) => {
  if (event.target.id !== "applicationForm") return;
  event.preventDefault();
  try {
    if (!GreenCertContracts.contracts.certificateRegistry) await GreenCertContracts.load(GreenCertWallet.signer);
    await GreenCertPages.submitApplication(event.target);
  } catch (error) {
    GreenCertApp.notice(error.message || "Application failed.", true);
  }
});
