# Connect your VPS backend to WordPress sites

There are a few clean ways to hook a VPS backend to one or more WordPress sites. Pick the pattern that fits how you want data to flow.

## The three common patterns

1) WP → Your VPS API (pull data)

- Expose your backend as an HTTPS API (e.g., `https://api.yourdomain.com`).
- From WordPress, call that API (server-to-server) and render results with a shortcode or block.
- Best for reading data (lists, dashboards, prices, CRM widgets) into pages.

2) Your VPS → WP (push/webhooks)

- Your backend calls a custom REST endpoint in WordPress to create/update posts, users, ACF fields, etc.
- Best when your system “owns” the data and wants to push updates to WP.

3) Reverse proxy under the same domain

- Route `https://yourwp.com/api/*` to the VPS internally (Nginx).
- Avoids CORS entirely and lets your frontend (AJAX) call `/api/...`.
- Best when you want browser-side calls without CORS headaches.

---

## Fastest path (recommended): WP pulls from your VPS API

### 1) Prep your VPS API

- Put it behind HTTPS with a real domain (Let’s Encrypt is fine).
- Choose auth: Bearer JWT or a long-lived API key.
- Enable CORS for your WP domains if you’ll call it from the browser; for server-to-server (PHP) you usually don’t need CORS.

Minimal CORS considerations:
- Allow origins: `https://site1.com, https://site2.com`
- Allow headers: `Authorization, Content-Type`
- Methods: `GET,POST,PUT,DELETE,OPTIONS`

### 2) Add a tiny WordPress plugin (server-to-server pull)

Create `wp-content/mu-plugins/crm-backend-connector.php`:

```php
<?php
/**
 * Plugin Name: CRM Backend Connector
 */
add_shortcode('crm_data', function($atts){
  $atts = shortcode_atts([
    'endpoint' => '/v1/customers', // change as needed
    'limit'    => 10
  ], $atts);

  $base   = 'https://api.example.com'; // <-- your VPS API base
  $url    = trailingslashit($base) . ltrim($atts['endpoint'], '/');
  $cache_key = 'crm_cache_' . md5($url . serialize($atts));
  if ($html = get_transient($cache_key)) return $html;

  $token = defined('CRM_API_TOKEN') ? CRM_API_TOKEN : '';
  $resp = wp_remote_get($url, [
    'headers' => [
      'Authorization' => $token ? ('Bearer ' . $token) : '',
      'Accept'        => 'application/json',
    ],
    'timeout' => 15,
  ]);

  if (is_wp_error($resp)) return 'Error: ' . esc_html($resp->get_error_message());
  if (wp_remote_retrieve_response_code($resp) !== 200) return 'API error';

  $data = json_decode(wp_remote_retrieve_body($resp), true);
  if (!is_array($data)) return 'Bad API response';

  $items = array_slice($data, 0, intval($atts['limit']));
  ob_start();
  echo '<ul class="crm-list">';
  foreach ($items as $row) {
    $name = isset($row['name']) ? $row['name'] : '';
    $email = isset($row['email']) ? $row['email'] : '';
    echo '<li>' . esc_html($name) . ($email ? ' (' . esc_html($email) . ')' : '') . '</li>';
  }
  echo '</ul>';
  $html = ob_get_clean();

  set_transient($cache_key, $html, 300); // cache 5 minutes
  return $html;
});
```

In `wp-config.php`, keep the token out of the DB:

```php
define('CRM_API_TOKEN', 'paste-your-jwt-or-api-key-here');
```

Use it in content:

```
[crm_data endpoint="/v1/customers" limit="8"]
```

Optional: refresh cache via cron:

```php
if (!wp_next_scheduled('crm_refresh')) {
  wp_schedule_event(time()+60, 'hourly', 'crm_refresh');
}
add_action('crm_refresh', function() {
  // call do_shortcode('[crm_data ...]') or make a wp_remote_get to warm cache
});
```

---

## Alternative: Backend pushes into WordPress (webhook)

Add a secure WP REST endpoint to accept data:

```php
<?php
add_action('rest_api_init', function () {
  register_rest_route('crm/v1', '/lead', [
    'methods'  => 'POST',
    'permission_callback' => function($req) {
      $secret = defined('CRM_WEBHOOK_SECRET') ? CRM_WEBHOOK_SECRET : '';
      $sig = $req->get_header('x-crm-signature');
      return $secret && hash_equals(hash_hmac('sha256', $req->get_body(), $secret), $sig);
    },
    'callback' => function(WP_REST_Request $req) {
      $p = $req->get_json_params();
      $post_id = wp_insert_post([
        'post_type'   => 'lead',
        'post_status' => 'publish',
        'post_title'  => sanitize_text_field($p['name'] ?? 'Lead'),
        'post_content'=> wp_kses_post($p['notes'] ?? ''),
      ]);
      return rest_ensure_response(['ok' => true, 'id' => $post_id]);
    }
  ]);
});
```

Then from your VPS, POST JSON to `https://yourwp.com/wp-json/crm/v1/lead` with header:

```
X-CRM-Signature: HMAC_SHA256(body, CRM_WEBHOOK_SECRET)
```

---

## Reverse proxy (same-origin, no CORS)

If WP is on Nginx, proxy `/api/` to the VPS:

```nginx
location /api/ {
  proxy_pass http://127.0.0.1:8000/;   # or your VPS upstream
  proxy_set_header Host $host;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
}
```

Now in the browser you can call `https://yourwp.com/api/v1/customers` via `fetch` or `jQuery.ajax` without CORS. (Add auth via cookie, header, or query as you prefer.)

---

## Security & reliability checklist

- HTTPS everywhere: valid certs on WP and API.
- Auth: Bearer token/JWT, or signed webhooks (HMAC). Never rely on obscurity.
- CORS: If doing browser calls cross-origin, lock `Access-Control-Allow-Origin` to your exact WP domains.
- Rate limit & WAF: Nginx `limit_req`, Cloudflare/NGINX WAF if exposed publicly.
- Secrets in env/`wp-config.php`, not posts/options.
- Timeouts & retries: backend should respond <10–15s; add retries/backoff in WP calls.
- Caching: WP Transients or an object cache (Redis) to reduce API load.
- Logging: log request IDs on both sides to trace issues.
- Version your API: `/v1/...` so you can change later.
- Backups & monitoring: uptime alerts, error alerts.

---

## Tell us your choices and we’ll tailor it

- Which pattern: pull, push, or reverse proxy?
- Which backend endpoints will you expose/consume?
- Are WP and API on the same domain/subdomain?

If you’re using our included chat widget, also see `wp-plugins/ollama-chat/readme.txt`.
