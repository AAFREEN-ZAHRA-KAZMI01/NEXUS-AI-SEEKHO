// ── Nexus AI — Shared State (localStorage) ──────────────────────

const State = {
  KEY: 'nexus_state',

  get() {
    try {
      return JSON.parse(localStorage.getItem(this.KEY) || '{}');
    } catch { return {}; }
  },

  set(data) {
    const current = this.get();
    localStorage.setItem(this.KEY, JSON.stringify({ ...current, ...data }));
  },

  clear() {
    localStorage.removeItem(this.KEY);
  },

  // Convenience getters/setters
  getSessionId()  { return this.get().sessionId || null; },
  getResult()     { return this.get().result || null; },
  getDomain()     { return this.get().domain || 'finance'; },
  getInputType()  { return this.get().inputType || 'text'; },
  getUser()       { return this.get().user || { name: 'User', email: '' }; },

  setSessionId(id)     { this.set({ sessionId: id }); },
  setResult(result)    { this.set({ result }); },
  setDomain(domain)    { this.set({ domain }); },
  setInputType(type)   { this.set({ inputType: type }); },
  setUser(user)        { this.set({ user }); },
};
