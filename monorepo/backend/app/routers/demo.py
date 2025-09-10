from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["demo"])


@router.get("/demo", response_class=HTMLResponse)
async def demo_page():
    html = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Backend Demo</title>
  <style>
    body { font: 14px system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 20px; }
    fieldset { margin-bottom: 16px; }
    label { display:block; margin: 6px 0 2px; }
    input[type=text], input[type=password], textarea { width: 100%; padding: 8px; }
    textarea { height: 100px; }
    button { padding: 8px 12px; cursor:pointer; }
    pre { background: #111; color: #0f0; padding: 10px; overflow:auto; max-height: 240px; }
    .row { display:flex; gap: 20px; }
    .col { flex:1; min-width: 280px; }
  </style>
  </head>
<body>
  <h1>Backend Demo</h1>
  <p>Use your site credentials to call the API. Nothing is stored here except via the backend.</p>

  <fieldset>
    <legend>Site Auth</legend>
    <label>Site ID</label>
    <input id="siteId" type="text" placeholder="e.g. gar_auto" />
    <label>API Key</label>
    <input id="apiKey" type="password" placeholder="site api key" />
  </fieldset>

  <div class="row">
    <div class="col">
      <fieldset>
        <legend>Chat (stream)</legend>
        <label>Message</label>
        <textarea id="chatMsg" placeholder="Ask a question..."></textarea>
        <button onclick="doChat()">Send</button>
        <pre id="chatOut"></pre>
      </fieldset>
    </div>

    <div class="col">
      <fieldset>
        <legend>Upload Document</legend>
        <label>File</label>
        <input id="fileInput" type="file" />
        <label>Customer ID (optional)</label>
        <input id="custId" type="text" />
        <button onclick="doUpload()">Upload</button>
        <pre id="uploadOut"></pre>
      </fieldset>
    </div>
  </div>

  <fieldset>
    <legend>Create Appointment</legend>
    <div class="row">
      <div class="col">
        <label>Customer ID</label>
        <input id="apptCust" type="text" placeholder="optional id" />
      </div>
      <div class="col">
        <label>Name</label>
        <input id="apptName" type="text" placeholder="John Doe" />
      </div>
    </div>
    <div class="row">
      <div class="col">
        <label>Phone</label>
        <input id="apptPhone" type="text" placeholder="+1 555 123 4567" />
      </div>
      <div class="col">
        <label>Service</label>
        <input id="apptService" type="text" placeholder="Dent Repair" />
      </div>
    </div>
    <label>Date & Time</label>
    <input id="apptWhen" type="datetime-local" />
    <div style="margin-top:8px">
      <button onclick="doAppt()">Create</button>
      <button onclick="loadAppts()" style="margin-left:8px">Load Appointments</button>
    </div>
    <pre id="apptOut"></pre>
  </fieldset>

  <script>
    function headers() {
      const siteId = document.getElementById('siteId').value.trim();
      const apiKey = document.getElementById('apiKey').value.trim();
      const h = { 'Content-Type': 'application/json' };
      if (siteId) h['X-Site-Id'] = siteId;
      if (apiKey) h['X-Api-Key'] = apiKey;
      return h;
    }

    async function doChat() {
      const out = document.getElementById('chatOut');
      out.textContent = '';
      const msg = document.getElementById('chatMsg').value;
      try {
        const resp = await fetch('/api/v1/chat/stream', {
          method: 'POST',
          headers: headers(),
          body: JSON.stringify({ message: msg })
        });
        if (!resp.ok || !resp.body) {
          out.textContent = 'Error: ' + resp.status + ' ' + resp.statusText;
          return;
        }
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          out.textContent += decoder.decode(value, { stream: true });
        }
      } catch (err) {
        out.textContent = 'Exception: ' + err;
      }
    }

    async function doUpload() {
      const out = document.getElementById('uploadOut');
      out.textContent = '';
      const fileInput = document.getElementById('fileInput');
      const custId = document.getElementById('custId').value.trim();
      if (!fileInput.files.length) { out.textContent = 'Pick a file first'; return; }
      const fd = new FormData();
      fd.append('file', fileInput.files[0]);
      if (custId) fd.append('customer_id', custId);
      try {
        const h = headers();
        delete h['Content-Type']; // browser sets multipart boundary
        const resp = await fetch('/api/v1/uploads', { method: 'POST', headers: h, body: fd });
        const data = await resp.json();
        out.textContent = JSON.stringify(data, null, 2);
      } catch (err) { out.textContent = 'Exception: ' + err; }
    }

    async function doAppt() {
      const out = document.getElementById('apptOut');
      out.textContent = '';
      try {
        const payload = {
          customer_id: document.getElementById('apptCust').value.trim() || undefined,
          name: document.getElementById('apptName').value.trim(),
          phone: document.getElementById('apptPhone').value.trim(),
          service: document.getElementById('apptService').value.trim(),
          time: document.getElementById('apptWhen').value
        };
        const resp = await fetch('/api/v1/appointments', { method: 'POST', headers: headers(), body: JSON.stringify(payload) });
        const data = await resp.json();
        out.textContent = JSON.stringify(data, null, 2);
      } catch (err) { out.textContent = 'Exception: ' + err; }
    }

    async function loadAppts() {
      const out = document.getElementById('apptOut');
      out.textContent = '';
      try {
        const resp = await fetch('/api/v1/appointments?limit=20', { headers: headers() });
        const data = await resp.json();
        out.textContent = JSON.stringify(data, null, 2);
      } catch (err) { out.textContent = 'Exception: ' + err; }
    }
  </script>
</body>
</html>
    """
    return HTMLResponse(html)
