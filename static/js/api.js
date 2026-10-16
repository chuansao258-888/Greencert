window.GreenCertApi = {
  async get(path) {
    const response = await fetch(`/api${path}`);
    const body = await response.json();
    if (!response.ok) throw new Error(body.error?.message || "Request failed");
    return body.data;
  }
};
