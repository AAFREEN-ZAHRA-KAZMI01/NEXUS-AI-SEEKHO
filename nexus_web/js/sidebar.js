// ── Renders sidebar into #sidebar-mount and sets active link ────
function renderSidebar(activePage) {
  const user = State.getUser();
  const name    = user.name  || 'User';
  const initial = name[0].toUpperCase();

  const links = [
    { id: 'home',     href: 'home.html',    icon: '🏠', label: 'Dashboard' },
    { id: 'analyze',  href: 'analyze.html', icon: '🔬', label: 'Analyze' },
    { id: 'insight',  href: 'insight.html', icon: '💡', label: 'Insights' },
    { id: 'trace',    href: 'trace.html',   icon: '📋', label: 'Agent Trace' },
    { id: 'profile',  href: 'profile.html', icon: '👤', label: 'Profile' },
  ];

  const navHtml = links.map(l => `
    <a href="${l.href}" class="nav-link ${activePage === l.id ? 'active' : ''}">
      <span class="nav-icon">${l.icon}</span>${l.label}
    </a>`).join('');

  const html = `
    <div class="sidebar-logo">
      <div class="logo-mark">
        <div class="logo-icon">⚡</div>
        <div>
          <div class="logo-text">NEXUS <span>AI</span></div>
          <div class="logo-sub">AI Ops Platform</div>
        </div>
      </div>
    </div>
    <nav class="sidebar-nav">
      <div class="sidebar-section-label">Navigation</div>
      ${navHtml}
    </nav>
    <div class="sidebar-footer">
      <div class="user-pill" onclick="window.location.href='profile.html'">
        <div class="user-avatar">${initial}</div>
        <div class="user-info">
          <div class="user-name">${name}</div>
          <div class="user-role">AI Analyst</div>
        </div>
        <span style="color:var(--text3);font-size:12px;">⚙</span>
      </div>
    </div>`;

  const mount = document.getElementById('sidebar-mount');
  if (mount) mount.innerHTML = html;
}
