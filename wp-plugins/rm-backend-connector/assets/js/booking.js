(() => {
  const cfg = window.RMBC_Booking_Config || {};
  function init(){
    document.addEventListener('click', async (e) => {
      const btn = e.target.closest('.rm-bc-booking-btn');
      if (!btn) return;
      const url = (cfg.apiBase || '').replace(/\/$/, '') + '/api/v1/tenants/info';
      const headers = {};
      if (cfg.publicKey) headers['X-Public-Key'] = cfg.publicKey;
      if (cfg.tenantId) headers['X-Tenant-Id'] = cfg.tenantId;
      try {
        const res = await fetch(url, { headers });
        if (!res.ok) { alert('Error loading booking info'); return; }
        const data = await res.json();
        const target = (data && data.booking_url) || null;
        if (target) { window.location.href = target; }
        else { alert('No booking URL configured for this tenant'); }
      } catch (err) {
        alert('Network error');
      }
    });
  }
  document.addEventListener('DOMContentLoaded', init);
})();
