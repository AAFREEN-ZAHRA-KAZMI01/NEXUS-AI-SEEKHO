// ── Nexus AI — API Client ────────────────────────────────────────
// Backend: FastAPI @ https://nexus-ai-seekho.onrender.com

const BASE_URL = 'https://nexus-ai-seekho.onrender.com';

const Api = {
  async _fetch(path, options = {}) {
    const url = BASE_URL + path;
    // Remove Content-Type for FormData (browser sets it with boundary)
    const headers = options.isFormData
      ? { ...options.headers }
      : { 'Content-Type': 'application/json', ...options.headers };
    delete options.isFormData;

    const res = await fetch(url, { headers, ...options });
    if (!res.ok) {
      const err = await res.text().catch(() => res.statusText);
      throw new Error(err || `HTTP ${res.status}`);
    }
    return res.json();
  },

  // ── Analysis ───────────────────────────────────────────────────
  // FIX #1: Backend schema uses 'content' not 'text'
  analyseText(text, domain) {
    return this._fetch('/api/analyse/text', {
      method: 'POST',
      body: JSON.stringify({ content: text, domain }),
    });
  },

  analyseUrl(url, domain) {
    return this._fetch('/api/analyse/url', {
      method: 'POST',
      body: JSON.stringify({ url, domain }),
    });
  },

  // FIX #2: Backend requires 'input_type' in FormData
  analyseFile(file, domain, inputType = 'pdf') {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('input_type', inputType);   // required by backend
    if (domain) fd.append('domain', domain);
    return this._fetch('/api/analyse/file', {
      method: 'POST',
      body: fd,
      isFormData: true,                   // skip Content-Type header
    });
  },

  // ── Session ────────────────────────────────────────────────────
  getSessionStatus(id) {
    return this._fetch(`/api/session/${id}/status`);
  },

  getSessionTrace(id) {
    return this._fetch(`/api/session/${id}/trace`);
  },

  // FIX #3: Backend returns { sessions: [...], total: N } not bare array
  async getRecentSessions() {
    const data = await this._fetch('/api/sessions');
    return Array.isArray(data) ? data : (data.sessions || []);
  },

  resetState() {
    return this._fetch('/api/state/reset', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  },

  getDomainState(domain) {
    return this._fetch(`/api/state/${domain}`);
  },

  // ── Health check ───────────────────────────────────────────────
  async ping() {
    try {
      const res = await fetch(BASE_URL + '/', {
        signal: AbortSignal.timeout(3000),
      });
      return res.ok;
    } catch { return false; }
  },
};
