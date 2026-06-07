// ─── InternLink Global JS ────────────────────────────────────
const API = window.location.origin + '/api';

// ─── Token helpers ───────────────────────────────────────────
const Auth = {
  getToken:  ()      => localStorage.getItem('il_token'),
  getUser:   ()      => JSON.parse(localStorage.getItem('il_user') || 'null'),
  setAuth:   (t, u)  => { localStorage.setItem('il_token', t); localStorage.setItem('il_user', JSON.stringify(u)); },
  clear:     ()      => { localStorage.removeItem('il_token'); localStorage.removeItem('il_user'); },
  isLoggedIn:()      => !!localStorage.getItem('il_token'),
  isAdmin:   ()      => { const u = Auth.getUser(); return u && u.role === 'ADMIN'; },
  isStudent: ()      => { const u = Auth.getUser(); return u && u.role === 'STUDENT'; },
};

// ─── Fetch wrapper ───────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Token ${token}`;
  if (options.body instanceof FormData) delete headers['Content-Type'];

  const res = await fetch(`${API}${path}`, { ...options, headers });
  const data = res.headers.get('content-type')?.includes('application/json')
    ? await res.json() : {};

  if (!res.ok) {
    const msg = data.detail || data.non_field_errors?.[0]
      || Object.values(data).flat()[0] || 'Something went wrong';
    throw new Error(msg);
  }
  return data;
}

// ─── Toast notifications ─────────────────────────────────────
function toast(msg, type = 'default', duration = 3500) {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = { success: '✓', error: '✕', warning: '⚠', default: 'ℹ' };
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span>${icons[type] || icons.default}</span><span>${msg}</span>`;
  container.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(120%)';
    setTimeout(() => t.remove(), 300); }, duration);
}

// ─── Navbar builder ──────────────────────────────────────────
function buildNav(activePage = '') {
  const user  = Auth.getUser();
  const pages = [
    { label: 'Home',          href: '/',              key: 'home' },
    { label: 'Opportunities', href: '/opportunities/',         key: 'opportunities' },
    { label: 'About',         href: '/about/',                 key: 'about' },
  ];

  const links = pages.map(p =>
    `<a href="${p.href}" class="${activePage === p.key ? 'active' : ''}">${p.label}</a>`
  ).join('');

  let actions = '';
  if (Auth.isLoggedIn()) {
    const initials = user ? `${user.first_name[0]}${user.last_name[0]}` : 'U';
    const dash = user?.role === 'ADMIN' ? '/admin-panel/' : '/dashboard/';
    actions = `
      <a href="${dash}" class="btn btn-outline btn-sm">Dashboard</a>
      <div class="nav-user">
        <div class="nav-avatar">${initials}</div>
        <span>${user?.first_name}</span>
      </div>
      <button onclick="logout()" class="btn btn-primary btn-sm">Logout</button>
    `;
  } else {
    actions = `
      <a href="/login/"    class="btn btn-outline btn-sm">Login</a>
      <a href="/register/" class="btn btn-primary btn-sm">Get Started</a>
    `;
  }

  return `
    <nav class="navbar">
      <div class="nav-inner">
        <a href="../index.html" class="nav-logo">Intern<span>Link</span><div class="logo-dot"></div></a>
        <div class="nav-links">${links}</div>
        <div class="nav-actions">${actions}</div>
      </div>
    </nav>
  `;
}

function logout() {
  apiFetch('/auth/logout/', { method: 'POST' }).catch(() => {});
  Auth.clear();
  window.location.href = '/';
}

// ─── Redirect guards ─────────────────────────────────────────
function requireAuth() {
  if (!Auth.isLoggedIn()) { window.location.href = '/login/'; return false; }
  return true;
}
function requireAdmin() {
  if (!Auth.isLoggedIn() || !Auth.isAdmin()) { window.location.href = '/login/'; return false; }
  return true;
}
function redirectIfLoggedIn() {
  if (Auth.isLoggedIn()) {
    window.location.href = Auth.isAdmin() ? '/admin-panel/' : '/dashboard/';
  }
}

// ─── Format helpers ──────────────────────────────────────────
function formatDate(d) {
  if (!d) return 'No deadline';
  return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}
function timeAgo(d) {
  const diff = Date.now() - new Date(d);
  const days = Math.floor(diff / 86400000);
  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 30)  return `${days}d ago`;
  if (days < 365) return `${Math.floor(days/30)}mo ago`;
  return `${Math.floor(days/365)}y ago`;
}
function statusBadge(status) {
  const map = {
    PENDING:  'badge-yellow', REVIEWED: 'badge-blue',
    ACCEPTED: 'badge-green',  REJECTED: 'badge-red',
    OPEN:     'badge-green',  CLOSED:   'badge-red',
    INTERNSHIP: 'badge-blue', SCHOLARSHIP: 'badge-orange',
  };
  return `<span class="badge ${map[status] || 'badge-gray'}">${status}</span>`;
}

// ─── Debounce ────────────────────────────────────────────────
function debounce(fn, delay = 350) {
  let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}

// ─── Modal helpers ───────────────────────────────────────────
function openModal(id)  { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }
