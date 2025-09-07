(() => {
  const cfg = window.RMBC_Config || {};
  function $(sel, root=document){ return root.querySelector(sel); }
  function appendMessage(win, role, text){
    const div = document.createElement('div');
    div.className = `rm-bc-msg rm-bc-msg-${role}`;
    div.textContent = text;
    win.appendChild(div);
    win.scrollTop = win.scrollHeight;
  }
  function init(){
    if (!cfg.containerId) return;
    const root = document.getElementById(cfg.containerId);
    if (!root) return;
    const win = $(".rm-bc-chat-window", root);
    const ta = $("textarea", root);
    const btn = $("button", root);
    async function send(){
      const message = ta.value.trim();
      if (!message) return;
      ta.value = '';
      appendMessage(win, 'user', message);
      const url = (cfg.apiBase || '').replace(/\/$/, '') + '/api/v1/chat/stream';
      const headers = { 'Content-Type':'application/json' };
      if (cfg.publicKey) headers['X-Public-Key'] = cfg.publicKey;
      if (cfg.tenantId) headers['X-Tenant-Id'] = cfg.tenantId;
      const body = { message, history: [], top_k: 5 };
      if (cfg.tenantId) body.tenant = cfg.tenantId;
      const respDiv = document.createElement('div');
      respDiv.className = 'rm-bc-msg rm-bc-msg-assistant';
      win.appendChild(respDiv);
      win.scrollTop = win.scrollHeight;
      try {
        const res = await fetch(url, { method:'POST', headers, body: JSON.stringify(body) });
        if (!res.ok || !res.body) {
          respDiv.textContent = `Error: ${res.status}`;
          return;
        }
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        while (true) {
          const {done, value} = await reader.read();
          if (done) break;
          respDiv.textContent += decoder.decode(value, {stream:true});
          win.scrollTop = win.scrollHeight;
        }
      } catch (e) {
        respDiv.textContent = 'Network error';
      }
    }
    btn.addEventListener('click', send);
    ta.addEventListener('keydown', (e)=>{ if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); send(); } });
  }
  document.addEventListener('DOMContentLoaded', init);
})();
