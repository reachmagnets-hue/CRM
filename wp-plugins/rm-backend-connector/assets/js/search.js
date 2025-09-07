(() => {
  const cfg = window.RMBC_Search_Config || {};
  function $(sel, root=document){ return root.querySelector(sel); }
  function init(){
    if (!cfg.containerId) return;
    const root = document.getElementById(cfg.containerId);
    if (!root) return;
    const form = $(".rm-bc-search-form", root);
    const results = $(".rm-bc-search-results", root);
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const q = new FormData(form).get('q');
      if (!q) return;
      results.textContent = 'Searching...';
      const urlBase = (cfg.apiBase || '').replace(/\/$/, '') + '/api/v1/search';
      const url = urlBase + '?q=' + encodeURIComponent(q) + '&top_k=5';
      const headers = {};
      if (cfg.publicKey) headers['X-Public-Key'] = cfg.publicKey;
      if (cfg.tenantId) headers['X-Tenant-Id'] = cfg.tenantId;
      try {
        const res = await fetch(url, { headers });
        if (!res.ok) { results.textContent = 'Error: ' + res.status; return; }
        const data = await res.json();
        const list = document.createElement('div');
        (data.results || []).forEach((r) => {
          const item = document.createElement('div');
          item.className = 'rm-bc-search-item';
          const title = document.createElement('div');
          title.className = 'rm-bc-search-title';
          title.textContent = `${r.filename} (score ${Number(r.score).toFixed(2)})`;
          const snip = document.createElement('div');
          snip.className = 'rm-bc-search-snippet';
          snip.textContent = r.snippet || '';
          list.appendChild(item);
          item.appendChild(title);
          item.appendChild(snip);
        });
        results.innerHTML = '';
        results.appendChild(list);
      } catch (e) {
        results.textContent = 'Network error';
      }
    });
  }
  document.addEventListener('DOMContentLoaded', init);
})();
