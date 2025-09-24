(function () {
  function el(tag, cls) { const e = document.createElement(tag); if (cls) e.className = cls; return e; }
  function widget() {
    const cfg = window.OLLAMA_CHAT_CFG || {}; const root = document.getElementById('ollama-chat-widget'); if (!root) return;
    const tenantAttr = root.getAttribute('data-tenant') || 'auto';

    // Launcher button (right-bottom) with label 'Use me'
    const launcher = el('button', 'oc-launcher'); launcher.type = 'button'; launcher.textContent = 'Use me'; root.appendChild(launcher);

    // Panel with tabs: Chat, Appointment, Upload Document, Call
    const panel = el('div', 'oc-panel hidden');
    const tabs = el('div', 'oc-tabs');
    const tabChat = el('button', 'oc-tab active'); tabChat.textContent = 'Chat';
    const tabAppt = el('button', 'oc-tab'); tabAppt.textContent = 'Appointment';
    const tabUpload = el('button', 'oc-tab'); tabUpload.textContent = 'Upload Document';
    const tabCall = el('button', 'oc-tab'); tabCall.textContent = 'Call';
    tabs.appendChild(tabChat); tabs.appendChild(tabAppt); tabs.appendChild(tabUpload); tabs.appendChild(tabCall);

    // Chat UI
    const chatBox = el('div', 'oc-box'); const header = el('div', 'oc-header'); header.textContent = 'Assistant';
    const body = el('div', 'oc-body'); const form = el('form', 'oc-form');
    const input = el('textarea', 'oc-input'); input.placeholder = 'Ask a question...';
    const send = el('button', 'oc-send'); send.type = 'submit'; send.textContent = 'Send';
    form.appendChild(input); form.appendChild(send);
    chatBox.appendChild(header); chatBox.appendChild(body); chatBox.appendChild(form);

    // Appointment UI
    const apptWrap = el('div', 'oc-appt');
    const apptInfo = el('div', 'oc-appt-info'); apptInfo.textContent = 'Select a service to book:';
    const apptSelect = el('select', 'oc-appt-select');
    const apptBtn = el('a', 'oc-appt-btn'); apptBtn.textContent = 'Book Appointment'; apptBtn.target = '_blank'; apptBtn.rel = 'noopener';
    apptWrap.appendChild(apptInfo); apptWrap.appendChild(apptSelect); apptWrap.appendChild(apptBtn);

    // Upload UI
    const uploadWrap = el('div', 'oc-upload');
    const fileInput = el('input'); fileInput.type = 'file'; fileInput.accept = '.pdf,.txt,.docx';
    const uploadBtn = el('button', 'oc-upload-btn'); uploadBtn.type = 'button'; uploadBtn.textContent = 'Upload';
    uploadWrap.appendChild(fileInput); uploadWrap.appendChild(uploadBtn);

    // Call UI (Phase 1)
    const callWrap = el('div', 'oc-call');
    const callBtn = el('button', 'oc-call-btn'); callBtn.type = 'button'; callBtn.textContent = 'Start Call';
    const callLog = el('pre', 'oc-call-log');
    callWrap.appendChild(callBtn); callWrap.appendChild(callLog);

    panel.appendChild(tabs);
    const content = el('div', 'oc-content'); content.appendChild(chatBox); content.appendChild(apptWrap); content.appendChild(uploadWrap); content.appendChild(callWrap);
    panel.appendChild(content); root.appendChild(panel);

    function show(idx) {
      chatBox.style.display = idx === 0 ? 'flex' : 'none'; apptWrap.style.display = idx === 1 ? 'block' : 'none'; uploadWrap.style.display = idx === 2 ? 'block' : 'none'; callWrap.style.display = idx === 3 ? 'block' : 'none';
      tabChat.classList.toggle('active', idx === 0); tabAppt.classList.toggle('active', idx === 1); tabUpload.classList.toggle('active', idx === 2); tabCall.classList.toggle('active', idx === 3);
    }
    show(0);

    tabChat.onclick = () => show(0); tabAppt.onclick = () => show(1); tabUpload.onclick = () => show(2); tabCall.onclick = () => show(3);
    launcher.onclick = () => { panel.classList.toggle('hidden'); };

    function addMsg(role, text) { const m = el('div', 'oc-msg ' + role); m.textContent = text; body.appendChild(m); body.scrollTop = body.scrollHeight; }
    async function chat(message) {
      const api = cfg.api_base; if (!api) { addMsg('sys', 'No API configured'); return; }
      const headers = { 'Content-Type': 'application/json' }; if (cfg.public_key) headers['X-Public-Key'] = cfg.public_key; if (cfg.tenant_override && tenantAttr !== 'auto') headers['X-Tenant-Id'] = cfg.tenant_override;
      const payload = { message: message, top_k: 5 };
      if (!cfg.tenant_override && tenantAttr !== 'auto') { payload.tenant = tenantAttr; }
      const mode = (cfg.mode || 'stream');
      if (mode === 'json') {
        const res = await fetch(api.replace(/\/$/, '') + '/api/v1/chat', { method: 'POST', headers, body: JSON.stringify(payload) });
        if (!res.ok) { addMsg('sys', 'Error: ' + res.status); return; }
        const data = await res.json();
        addMsg('assistant', data && data.answer ? String(data.answer) : '(no answer)');
      } else {
        const res = await fetch(api.replace(/\/$/, '') + '/api/v1/chat/stream', { method: 'POST', headers, body: JSON.stringify(payload) });
        if (!res.ok) { addMsg('sys', 'Error: ' + res.status); return; }
        const reader = res.body.getReader(); const dec = new TextDecoder(); addMsg('assistant', ''); const last = body.lastChild;
        while (true) { const { done, value } = await reader.read(); if (done) break; last.textContent += dec.decode(value, { stream: true }); body.scrollTop = body.scrollHeight; }
      }
    }
    form.addEventListener('submit', function (e) { e.preventDefault(); const q = input.value.trim(); if (!q) return; addMsg('user', q); input.value = ''; chat(q); });

    // Appointment: fetch tenant info for services and booking URL
    async function loadTenantInfo() {
      const api = cfg.api_base; if (!api) return;
      const headers = {}; if (cfg.public_key) headers['X-Public-Key'] = cfg.public_key; if (cfg.tenant_override && tenantAttr !== 'auto') headers['X-Tenant-Id'] = cfg.tenant_override;
      const res = await fetch(api.replace(/\/$/, '') + '/api/v1/tenants/info', { headers });
      if (!res.ok) return; const data = await res.json();
      apptSelect.innerHTML = '';
      (data.services || []).forEach((s, i) => { const opt = document.createElement('option'); opt.value = s.url || ''; opt.textContent = s.name || ('Service ' + (i + 1)); apptSelect.appendChild(opt); });
      apptBtn.href = (data.booking_url || (apptSelect.value || '#'));
      apptSelect.onchange = () => { apptBtn.href = (data.booking_url || apptSelect.value || '#'); };
    }
    loadTenantInfo();

    // Upload: send file directly to backend ingest (admin key required so typically disable on public; here just UI placeholder)
    uploadBtn.onclick = async () => {
      const f = fileInput.files && fileInput.files[0]; if (!f) { alert('Choose a file'); return; }
      alert('Upload requires admin key; use dashboard tool instead.');
    };

    // Call: basic offer/answer with backend (no audio until Phase 2)
    callBtn.onclick = async () => {
      callLog.textContent = '';
      const api = cfg.api_base; if (!api) { callLog.textContent = 'No API configured'; return; }
      try {
        const pc = new RTCPeerConnection();
        pc.onconnectionstatechange = () => { callLog.textContent += `\nstate: ${pc.connectionState}`; };
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          for (const track of stream.getAudioTracks()) pc.addTrack(track, stream);
        } catch (e) { }
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        const res = await fetch(api.replace(/\/$/, '') + '/api/v1/rtc/offer', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type: offer.type, sdp: offer.sdp })
        });
        if (!res.ok) { callLog.textContent = 'Error: ' + res.status; return; }
        const answer = await res.json(); await pc.setRemoteDescription(answer);
        callLog.textContent = 'Connected.';
      } catch (err) { callLog.textContent = 'Exception: ' + err; }
    };
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', widget); else widget();
})();
