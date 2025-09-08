(function () {
    const base = (window.mbcCfg?.apiBase || '').replace(/\/$/, '');
    const siteId = window.mbcCfg?.siteId || '';
    const apiKey = window.mbcCfg?.apiKey || '';
    function headers() { return { 'X-Site-Id': siteId, 'X-Api-Key': apiKey }; }

    async function chat() {
        const el = document.getElementById('mbc-chatbot'); if (!el) return;
        const form = document.createElement('form');
        form.innerHTML = '<input name="q" placeholder="Ask..."/><input name="customer_id" placeholder="Customer ID (optional)"/><button>Send</button><pre class="out"></pre>';
        const out = form.querySelector('.out');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const q = form.q.value;
            out.textContent = '';
            try {
                const resp = await fetch(base + '/api/v1/chat/stream', { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers() }, body: JSON.stringify({ message: q, top_k: 5, customer_id: form.customer_id.value || null }) });
                if (!resp.ok || !resp.body) { out.textContent = 'Chat unavailable'; return; }
                const reader = resp.body.getReader();
                const decoder = new TextDecoder();
                while (true) { const { done, value } = await reader.read(); if (done) break; out.textContent += decoder.decode(value); }
            } catch (err) { out.textContent = 'Chat unavailable'; }
        });
        el.appendChild(form);
    }

    async function appointment() {
        const el = document.getElementById('mbc-appointment'); if (!el) return;
        const form = document.createElement('form');
        form.innerHTML = '<input name="name" placeholder="Name"/><input name="phone" placeholder="Phone"/><input name="customer_id" placeholder="Customer ID (optional)"/><button>Book</button><pre class="out"></pre>';
        const out = form.querySelector('.out');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = { name: form.name.value, phone: form.phone.value, customer_id: form.customer_id.value || null };
            try {
                const r = await fetch(base + '/api/v1/appointments', { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers() }, body: JSON.stringify(payload) });
                const j = await r.json();
                out.textContent = j.ok ? 'Booked' : 'Failed';
            } catch (err) { out.textContent = 'Booking unavailable'; }
        });
        el.appendChild(form);
    }

    async function upload() {
        const el = document.getElementById('mbc-upload'); if (!el) return;
        const form = document.createElement('form');
        form.innerHTML = '<input type="file" name="file"/><input name="customer_id" placeholder="Customer ID (optional)"/><button>Upload</button><pre class="out"></pre>';
        const out = form.querySelector('.out');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData(); fd.append('file', form.file.files[0]); if (form.customer_id.value) { fd.append('customer_id', form.customer_id.value); }
            try {
                const r = await fetch(base + '/api/v1/ingest/upload', { method: 'POST', headers: headers(), body: fd });
                out.textContent = r.ok ? 'Uploaded' : 'Failed';
            } catch (err) { out.textContent = 'Upload unavailable'; }
        });
        el.appendChild(form);
    }

    async function voice() {
        const el = document.getElementById('mbc-voice'); if (!el) return;
        const box = document.createElement('div');
        box.innerHTML = '<div class="mbc-voice"><p>Call our AI assistant at:</p><ul class="nums"></ul></div>';
        el.appendChild(box);
        try {
            const r = await fetch(base + '/api/v1/sites/info', { headers: headers() });
            const info = await r.json();
            const ul = box.querySelector('.nums');
            (info.numbers || []).forEach(n => {
                const li = document.createElement('li');
                const a = document.createElement('a'); a.href = 'tel:' + n; a.textContent = n; li.appendChild(a); ul.appendChild(li);
            });
        } catch (e) { const ul = box.querySelector('.nums'); const li = document.createElement('li'); li.textContent = 'Voice assistant unavailable'; ul.appendChild(li); }
    }

    chat(); appointment(); upload(); voice();
})();
