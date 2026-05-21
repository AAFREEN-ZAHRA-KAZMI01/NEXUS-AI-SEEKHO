// ── Nexus AI — API Client ────────────────────────────────────────

const BASE_URL = 'http://localhost:8000';

const Api = {
  async _fetch(path, options = {}) {
    const url = BASE_URL + path;
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    if (!res.ok) {
      const err = await res.text().catch(() => res.statusText);
      throw new Error(err || `HTTP ${res.status}`);
    }
    return res.json();
  },

  // ── Analysis ───────────────────────────────────────────────────
  analyseText(text, domain) {
    return this._fetch('/api/analyse/text', {
      method: 'POST',
      body: JSON.stringify({ text, domain }),
    });
  },

  analyseUrl(url, domain) {
    return this._fetch('/api/analyse/url', {
      method: 'POST',
      body: JSON.stringify({ url, domain }),
    });
  },

  analyseFile(file, domain) {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('domain', domain);
    return fetch(BASE_URL + '/api/analyse/file', {
      method: 'POST',
      body: fd,
    }).then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    });
  },

  // ── Session ────────────────────────────────────────────────────
  getSessionStatus(id) {
    return this._fetch(`/api/session/${id}/status`);
  },

  getSessionTrace(id) {
    return this._fetch(`/api/session/${id}/trace`);
  },

  getRecentSessions() {
    return this._fetch('/api/sessions');
  },

  resetState() {
    return this._fetch('/api/state/reset', { method: 'POST', body: '{}' });
  },

  // ── Health check ───────────────────────────────────────────────
  async ping() {
    try {
      const res = await fetch(BASE_URL + '/', { signal: AbortSignal.timeout(3000) });
      return res.ok;
    } catch { return false; }
  },
};
