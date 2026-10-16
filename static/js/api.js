window.GreenCertApi = {
  csrfToken: null,
  // Read a JSON response and surface its API error.
  async request(path, options = {}) {
    const headers = { ...(options.headers || {}) };
    if (this.csrfToken && options.method && options.method !== "GET") headers["X-CSRF-Token"] = this.csrfToken;
    const response = await fetch(`/api${path}`, { ...options, headers });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error?.message || "Request failed");
    return body.data;
  },
  // Fetch a JSON API resource.
  async get(path) {
    return this.request(path);
  },
  // Send a JSON API request.
  async post(path, payload) {
    return this.request(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  },
  // Upload an evidence file from the application form.
  async upload(file) {
    const form = new FormData();
    form.append("file", file);
    return this.request("/files", { method: "POST", body: form });
  }
};
