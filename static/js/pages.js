window.GreenCertPages = {
  // Keep status text visible while adding a predictable color for known states.
  statusBadge(status) {
    const label = String(status ?? "Unknown");
    const known = ["Approved", "Active", "confirmed", "Rejected", "failed", "Pending", "pending", "Listed", "Withdrawn", "Retired"];
    const variant = known.includes(label) ? label.toLowerCase() : "other";
    return `<span class="status-badge status-${variant}">${GreenCertApp.escape(label)}</span>`;
  },
  integrityBadge(status) {
    const labels = { verified: "Verified", incomplete: "Incomplete", mismatch: "Mismatch" };
    const known = Object.prototype.hasOwnProperty.call(labels, status);
    return `<span class="status-badge status-${known ? status : "other"}">${known ? labels[status] : "Unknown"}</span>`;
  },
  transactionLink(hash, label = null) {
    const value = String(hash ?? "");
    if (!/^0x[0-9a-fA-F]{64}$/.test(value)) return GreenCertApp.escape(value);
    return `<a class="explorer-link" href="https://sepolia.etherscan.io/tx/${value}" target="_blank" rel="noopener noreferrer" aria-label="View transaction ${value} on Sepolia Etherscan">${label ? GreenCertApp.escape(label) : value}</a>`;
  },
  periodDate(value) {
    const timestamp = Number(value);
    if (!Number.isFinite(timestamp) || timestamp <= 0) return "Unavailable";
    const date = new Date(timestamp * 1000);
    return Number.isNaN(date.getTime()) ? "Unavailable" : date.toISOString().slice(0, 10);
  },
  // Refresh data for the page currently on screen.
  async refresh() {
    try {
      if (document.getElementById("statIssued")) {
        const totals = await GreenCertApi.get("/dashboard");
        for (const name of ["Issued", "Listed", "Sold", "Retired"]) document.getElementById(`stat${name}`).textContent = totals[name.toLowerCase()];
        this.dashboard(totals);
      }
      if (document.getElementById("marketList")) await this.market();
      if (document.getElementById("applicationList")) await this.applications();
      if (GreenCertWallet.address && document.getElementById("ownedList")) await this.owned();
      if (GreenCertWallet.address && document.getElementById("walletPanel")) await this.wallet();
      if (GreenCertWallet.address && document.getElementById("activityList")) await this.activity();
      if (document.getElementById("certificateDetail")) await this.certificateDetail();
      if (document.getElementById("auditReports")) await this.audit();
    } catch (error) {
      if (error.message.includes("not configured")) {
        for (const id of ["sourceChart", "statusChart"]) {
          const root = document.getElementById(id);
          if (root) root.innerHTML = '<p class="chart-empty">Configure the Sepolia contracts to load chart data.</p>';
        }
        for (const id of ["marketList", "certificateArchive", "certificateEvents", "auditReports", "auditEvents"]) {
          const root = document.getElementById(id);
          if (root) root.innerHTML = "<div class='empty-state'><h2>Contracts not configured</h2><p>Add the Sepolia deployment settings to load live records.</p></div>";
        }
      } else GreenCertApp.notice(error.message, true);
    }
  },
  // Render the source and lifecycle charts from the dashboard response.
  dashboard(totals) {
    const sources = totals.sourceBreakdown
      .filter((item) => Number(item.quantityMWh) > 0)
      .map((item) => ({ label: item.source, value: Number(item.quantityMWh), color: item.source.toLowerCase() }));
    this.renderChart("sourceChart", sources, "MWh");
    const statuses = Number(totals.issued) > 0
      ? [{ label: "Active", value: Number(totals.active), color: "active" }, { label: "Retired", value: Number(totals.retired), color: "retired" }]
      : [];
    this.renderChart("statusChart", statuses, "batches");
  },
  // Build labeled horizontal bars without a charting library.
  renderChart(id, rows, unit) {
    const root = document.getElementById(id);
    if (!rows.length) {
      root.innerHTML = '<p class="chart-empty">No issued certificates yet.</p>';
      return;
    }
    const maximum = Math.max(...rows.map((row) => row.value));
    root.innerHTML = `<ul class="chart-list">${rows.map((row) => {
      const width = maximum ? Math.round(row.value / maximum * 100) : 0;
      return `<li><div class="chart-label"><span>${GreenCertApp.escape(row.label)}</span><span class="chart-value">${row.value} ${unit}</span></div><div class="chart-track" aria-hidden="true"><span class="chart-fill ${row.color}" style="width:${width}%"></span></div></li>`;
    }).join("")}</ul>`;
  },
  // Show available batches and their whole-batch prices.
  async market() {
    const items = await GreenCertApi.get("/certificates");
    const listed = items.filter((item) => item.listed);
    document.getElementById("marketList").innerHTML = listed.length ? listed.map((item) =>
      `<article class="record-card"><h2>${GreenCertApp.escape(item.metadata?.siteName || "Metadata unavailable")}</h2><p>${GreenCertApp.escape(item.metadata?.source || "Unknown")} · ${item.quantity} RECs / ${item.quantity} MWh</p><p>Total price: ${GreenCertApp.eth(item.listing.totalPriceWei)}</p><p><a href="/certificates/${item.id}">View certificate #${item.id}</a></p><div class="button-row"><button class="button primary" data-action="buy" data-id="${item.id}" data-price="${item.listing.totalPriceWei}" data-quantity="${item.quantity}">Buy whole batch</button></div></article>`
    ).join("") : "<div class='empty-state'><h2>No listings yet</h2></div>";
    document.getElementById("certificateArchive").innerHTML = items.length ? items.slice().reverse().map((item) =>
      `<article class="record-card"><h2>Certificate #${item.id}</h2><p>${GreenCertApp.escape(item.metadata?.siteName || "Metadata unavailable")} · ${item.quantity} RECs</p><p class="status-row">${this.statusBadge(item.status)}${item.listed ? this.statusBadge("Listed") : ""}</p><p><a href="/certificates/${item.id}">View public record</a></p></article>`
    ).join("") : "<div class='empty-state'><h2>No certificates issued yet</h2></div>";
  },
  // Show the connected wallet's applications or the Admin review queue.
  async applications() {
    const role = GreenCertWallet.role;
    const list = document.getElementById("applicationList");
    document.getElementById("applicationFormPanel").hidden = !GreenCertWallet.address;
    if (!GreenCertWallet.address) {
      list.innerHTML = "<div class='empty-state'><p>Connect a wallet to view or submit applications.</p></div>";
      return;
    }
    const items = await GreenCertApi.get("/applications");
    list.innerHTML = items.length ? items.slice().reverse().map((item) => {
      const actions = item.status !== "Pending" ? "" : role === "Admin"
        ? `<button class="button primary" data-action="approve" data-id="${item.id}">Approve</button><button class="button secondary" data-action="reject" data-id="${item.id}">Reject</button>`
        : `<button class="button secondary" data-action="withdraw" data-id="${item.id}">Withdraw</button>`;
      const site = item.metadata?.siteName ? `<p>Site: ${GreenCertApp.escape(item.metadata.siteName)}</p>` : "<p>Metadata unavailable in this app.</p>";
      const evidence = item.evidenceFileId
        ? `<a href="/api/files/${encodeURIComponent(item.evidenceFileId)}" target="_blank" rel="noopener noreferrer">Download evidence</a>`
        : "<span class=\"muted\">Evidence unavailable</span>";
      return `<article class="record-card"><h2>Application #${item.id}</h2><p class="status-row">${this.statusBadge(item.status)}<span>· ${item.quantity} RECs</span></p>${site}<p>Applicant: ${GreenCertApp.escape(item.producer)}</p><div class="button-row"><button class="button secondary" data-action="details" data-id="${item.id}" aria-expanded="false">View details</button>${actions}</div><div class="application-details" id="applicationDetails${item.id}" hidden></div><p class="evidence-state">${evidence}</p></article>`;
    }).join("") : "<div class='empty-state'><h2>No applications</h2></div>";
  },
  // Show owned certificates and actions allowed by ownership, not account type.
  async owned() {
    const items = await GreenCertApi.get(`/certificates?owner=${GreenCertWallet.address}`);
    document.getElementById("ownedList").innerHTML = items.length ? items.reverse().map((item) => {
      let actions = "";
      if (item.status === "Active") actions = item.listed
        ? `<button class="button secondary" data-action="reprice" data-id="${item.id}">Change price</button><button class="button secondary" data-action="cancel" data-id="${item.id}">Cancel listing</button>`
        : `<button class="button primary" data-action="list" data-id="${item.id}">List batch</button><button class="button secondary" data-action="retire" data-id="${item.id}">Retire whole batch</button>`;
      return `<article class="record-card"><h2>Certificate #${item.id}</h2><p>${GreenCertApp.escape(item.metadata?.siteName || "Metadata unavailable")} · ${item.quantity} RECs</p><p class="status-row">${this.statusBadge(item.status)}${item.listed ? this.statusBadge("Listed") : ""}</p>${item.listed ? `<p>Total price: ${GreenCertApp.eth(item.listing.totalPriceWei)}</p>` : ""}<p><a href="/certificates/${item.id}">View public record</a></p><div class="button-row">${actions}</div></article>`;
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
      `<article class="record-card"><h2>${GreenCertApp.escape(item.method)}</h2><p class="status-row">${this.statusBadge(item.status)}<span>· gas used ${GreenCertApp.escape(item.gas_used || "pending")}</span></p><p>${this.transactionLink(item.tx_hash)}</p></article>`
    ).join("") : "<div class='empty-state'><h2>No verified transactions yet</h2></div>";
  },
  // Show a certificate's current state and matching contract events.
  async certificateDetail() {
    const root = document.getElementById("certificateDetail");
    const id = root.dataset.certificateId;
    const item = await GreenCertApi.get(`/certificates/${id}`);
    const metadata = item.metadata || {};
    root.innerHTML = `<h2>${GreenCertApp.escape(metadata.siteName || "Metadata unavailable")}</h2><p>${GreenCertApp.escape(metadata.source || "Unknown")} · ${GreenCertApp.escape(metadata.country || "")}</p><p>Quantity: ${item.quantity} RECs / ${item.quantity} MWh</p><p class="status-row">Status: ${this.statusBadge(item.status)}${item.listed ? this.statusBadge("Listed") : ""}</p><p>Owner: ${GreenCertApp.escape(item.owner)}</p><p>Total listing price: ${item.listed ? GreenCertApp.eth(item.listing.totalPriceWei) : "Not listed"}</p><p>Metadata hash: ${GreenCertApp.escape(item.metadataHash)}</p>${item.retirement ? `<p>Retired for ${GreenCertApp.escape(item.retirement.beneficiary)}: ${GreenCertApp.escape(item.retirement.purpose)}</p>` : ""}`;
    try {
      const evidence = await GreenCertApi.get(`/certificates/${id}/evidence-summary`);
      const checkLabels = { approvedApplication: "Approved application linked", metadataHash: "Stored metadata matches on-chain hash", metadataFields: "Batch details match the application", evidenceFile: "Local evidence file matches SHA-256" };
      const summary = evidence.summary;
      document.getElementById("certificateEvidence").innerHTML = `<h2>Evidence integrity</h2><p class="status-row">Record integrity: ${this.integrityBadge(evidence.status)}</p>${summary ? `<p>${GreenCertApp.escape(summary.siteName || "Site unavailable")} · ${GreenCertApp.escape(summary.source || "Unknown source")} · ${GreenCertApp.escape(summary.country || "")}</p><p>Generation period: ${this.periodDate(summary.periodStart)} to ${this.periodDate(summary.periodEnd)}</p><p>Evidence SHA-256: <code>${GreenCertApp.escape(summary.proofSha256 || "Unavailable")}</code></p>` : "<p>A verified metadata summary is unavailable.</p>"}<ul class="integrity-checks">${Object.entries(checkLabels).map(([key, label]) => `<li><span>${label}</span><strong class="check-${GreenCertApp.escape(evidence.checks[key])}">${GreenCertApp.escape(evidence.checks[key])}</strong></li>`).join("")}</ul><p>Hash checks show record consistency; they do not independently prove generation. Uploaded files remain private.</p><p><a class="text-link" href="/audit">Open public audit →</a></p>`;
    } catch (error) {
      document.getElementById("certificateEvidence").innerHTML = `<h2>Evidence integrity</h2><p>Integrity checks are temporarily unavailable.</p>`;
    }
    const events = await GreenCertApi.get(`/certificates/${id}/events`);
    document.getElementById("certificateEvents").innerHTML = events.length ? events.map((event) =>
      `<p><strong>${GreenCertApp.escape(event.event)}</strong> · block ${GreenCertApp.escape(event.blockNumber)}<br><small>${this.transactionLink(event.transactionHash)}</small></p>`
    ).join("") : "<p>No matching events found.</p>";
  },
  // Show cross-certificate checks and the on-chain lifecycle timeline.
  async audit() {
    const data = await GreenCertApi.get("/audit");
    this.auditData = data;
    document.getElementById("auditVerified").textContent = data.totals.verified;
    document.getElementById("auditIncomplete").textContent = data.totals.incomplete;
    document.getElementById("auditMismatch").textContent = data.totals.mismatch;
    this.renderAuditReports();
    document.getElementById("auditEvents").innerHTML = data.eventStatus === "unavailable"
      ? "<p>Event history is temporarily unavailable from the Sepolia RPC provider.</p>"
      : data.events.length ? `<div class="audit-timeline">${data.events.map((event) =>
        `<article class="audit-event"><div class="audit-event-card"><p class="audit-event-title">${GreenCertApp.escape(String(event.event).replace(/([a-z])([A-Z])/g, "$1 $2"))}</p><p class="audit-event-meta"><span>Certificate #${GreenCertApp.escape(event.certificateId)}</span><span>Block ${GreenCertApp.escape(event.blockNumber)}</span></p><div class="audit-event-actions"><a class="text-link" href="/certificates/${encodeURIComponent(event.certificateId)}">View record</a>${this.transactionLink(event.transactionHash, "View transaction ↗")}</div></div></article>`
      ).join("")}</div>` : "<p>No certificate events found.</p>";
  },
  renderAuditReports() {
    if (!this.auditData) return;
    const filter = document.getElementById("auditFilter").value;
    const items = this.auditData.reports.filter((report) => filter === "all" || report.status === filter);
    document.getElementById("auditReports").innerHTML = items.length ? items.map((report) =>
      `<article class="audit-record"><div class="audit-record-top"><h3>Certificate #${GreenCertApp.escape(report.certificateId)}</h3>${this.integrityBadge(report.status)}</div><p class="audit-record-site">${GreenCertApp.escape(report.summary?.siteName || "Metadata summary unavailable")}</p><p class="audit-record-meta"><span>Application #${GreenCertApp.escape(report.applicationId)}</span><span>Evidence: ${GreenCertApp.escape(report.checks.evidenceFile)}</span></p><a class="audit-record-link" href="/certificates/${encodeURIComponent(report.certificateId)}"><span>Review checks and history</span><span aria-hidden="true">→</span></a></article>`
    ).join("") : `<div class="empty-state"><h2>${filter === "all" ? "No certificates issued yet" : "No matching records"}</h2></div>`;
  },
  // Parse an English-format calendar date without locale-dependent browser controls.
  parsePeriodDate(value, endOfDay = false) {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(value));
    if (!match) throw new Error("Enter dates as YYYY-MM-DD.");
    const year = Number(match[1]);
    const month = Number(match[2]);
    const day = Number(match[3]);
    const date = new Date(Date.UTC(year, month - 1, day));
    if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) {
      throw new Error("Enter a valid calendar date.");
    }
    return String(Math.floor(date.getTime() / 1000) + (endOfDay ? 86399 : 0));
  },
  // Upload evidence and submit its certificate application.
  async submitApplication(form) {
    const values = new FormData(form);
    const periodStart = this.parsePeriodDate(values.get("periodStart"));
    const periodEnd = this.parsePeriodDate(values.get("periodEnd"), true);
    const evidence = await GreenCertApi.upload(values.get("evidence"));
    const payload = Object.fromEntries(["siteCode", "siteName", "source", "country", "batchIndex", "quantity"].map((key) => [key, values.get(key)]));
    payload.periodStart = periodStart;
    payload.periodEnd = periodEnd;
    payload.proofFileId = evidence.fileId;
    const content = await GreenCertApi.post("/content", { kind: "application", payload });
    if (ethers.keccak256(ethers.toUtf8Bytes(content.canonicalJson)) !== content.contentHash) throw new Error("Metadata hash does not match.");
    const args = content.chainArgs;
    await GreenCertTransactions.send("Submit application", () => GreenCertContracts.contracts.certificateRegistry.submitApplication(args.siteHash, args.periodStart, args.periodEnd, args.batchIndex, args.quantity, args.metadataHash));
    form.reset();
    document.getElementById("selectedEvidence").textContent = "No file selected";
    await this.refresh();
  },
  // Execute one application, market or retirement action.
  async action(name, id, button) {
    if (name === "details") {
      const root = document.getElementById(`applicationDetails${id}`);
      if (!root.hidden) {
        root.hidden = true;
        button.setAttribute("aria-expanded", "false");
        button.textContent = "View details";
        return;
      }
      const item = await GreenCertApi.get(`/applications/${id}`);
      const metadata = item.metadata;
      root.innerHTML = metadata ? `<h3>Application details</h3><dl><div><dt>Site code</dt><dd>${GreenCertApp.escape(metadata.siteCode || "Unavailable")}</dd></div><div><dt>Site name</dt><dd>${GreenCertApp.escape(metadata.siteName || "Unavailable")}</dd></div><div><dt>Energy source</dt><dd>${GreenCertApp.escape(metadata.source || "Unavailable")}</dd></div><div><dt>Country code</dt><dd>${GreenCertApp.escape(metadata.country || "Unavailable")}</dd></div><div><dt>Period</dt><dd>${this.periodDate(metadata.periodStart)} to ${this.periodDate(metadata.periodEnd)}</dd></div><div><dt>Batch index</dt><dd>${GreenCertApp.escape(metadata.batchIndex ?? "Unavailable")}</dd></div><div><dt>Quantity</dt><dd>${GreenCertApp.escape(item.quantity)} RECs</dd></div></dl><p>Metadata hash: ${GreenCertApp.escape(item.metadataHash)}</p>`
        : `<h3>Application details</h3><p>This application exists on Sepolia, but its metadata and evidence were not stored in this app.</p><p>Metadata hash: ${GreenCertApp.escape(item.metadataHash)}</p>`;
      root.hidden = false;
      button.setAttribute("aria-expanded", "true");
      button.textContent = "Hide details";
      return;
    }
    const market = GreenCertContracts.contracts.certificateMarket;
    const registry = GreenCertContracts.contracts.certificateRegistry;
    if (!market || !registry) throw new Error("Connect a wallet first.");
    if (name === "approve") await GreenCertTransactions.send("Approve application", () => registry.approveApplication(id));
    if (name === "withdraw") await GreenCertTransactions.send("Withdraw application", () => registry.withdrawApplication(id));
    if (name === "buy") {
      const price = button.dataset.price;
      if (!confirm(`Buy all ${button.dataset.quantity} RECs for ${GreenCertApp.eth(price)} plus the network fee?`)) return;
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
      if (name === "retire") {
        const certificate = await GreenCertApi.get(`/certificates/${id}`);
        if (!confirm(`Permanently retire all ${certificate.quantity} RECs in this batch?`)) return;
      }
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

// Bind certificate and proceeds actions.
document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-action], #withdrawProceeds");
  if (!button) return;
  try {
    if (button.dataset.action === "details") {
      await GreenCertPages.action("details", button.dataset.id, button);
      return;
    }
    await GreenCertApp.withWalletRequest(button, async () => {
      if (!GreenCertWallet.signer) throw new Error("Connect a wallet first.");
      await GreenCertWallet.ensureTargetNetwork();
      if (!GreenCertContracts.contracts.roleRegistry) await GreenCertContracts.load(GreenCertWallet.signer);
      if (button.id === "withdrawProceeds") {
        await GreenCertTransactions.send("Withdraw proceeds", () => GreenCertContracts.contracts.certificateMarket.withdraw());
      } else {
        await GreenCertPages.action(button.dataset.action, button.dataset.id, button);
      }
      await GreenCertPages.refresh();
    });
  } catch (error) {
    GreenCertApp.notice(GreenCertApp.walletError(error), true);
  }
});

// Submit an application from the connected wallet.
document.addEventListener("submit", async (event) => {
  if (event.target.id !== "applicationForm") return;
  event.preventDefault();
  try {
    const submitButton = event.target.querySelector('button[type="submit"]');
    await GreenCertApp.withWalletRequest(submitButton, async () => {
      if (!GreenCertWallet.signer) throw new Error("Connect a wallet first.");
      await GreenCertWallet.ensureTargetNetwork();
      if (!GreenCertContracts.contracts.certificateRegistry) await GreenCertContracts.load(GreenCertWallet.signer);
      await GreenCertPages.submitApplication(event.target);
    });
  } catch (error) {
    GreenCertApp.notice(GreenCertApp.walletError(error), true);
  }
});

// Show the chosen evidence filename without browser-localized file-input text.
document.addEventListener("change", (event) => {
  if (event.target.id === "auditFilter") {
    GreenCertPages.renderAuditReports();
    return;
  }
  if (event.target.id !== "evidenceFile") return;
  document.getElementById("selectedEvidence").textContent = event.target.files?.[0]?.name || "No file selected";
});
