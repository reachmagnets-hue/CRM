<?php
/*
Plugin Name: RM Backend Connector
Description: Connects WordPress to your FastAPI backend (chat + search) via shortcodes and settings.
Version: 0.1.0
Author: Reach Magnets
*/

if (!defined('ABSPATH')) { exit; }

define('RM_BC_VERSION', '0.1.0');
define('RM_BC_SLUG', 'rm-backend-connector');
define('RM_BC_OPTION_API_BASE', 'rm_bc_api_base');
define('RM_BC_OPTION_PUBLIC_KEY', 'rm_bc_public_key');
define('RM_BC_OPTION_TENANT_ID', 'rm_bc_tenant_id');

// Register settings on admin init
add_action('admin_init', function () {
    register_setting('rm_bc_settings', RM_BC_OPTION_API_BASE, ['type' => 'string', 'sanitize_callback' => 'esc_url_raw']);
    register_setting('rm_bc_settings', RM_BC_OPTION_PUBLIC_KEY, ['type' => 'string', 'sanitize_callback' => 'sanitize_text_field']);
    register_setting('rm_bc_settings', RM_BC_OPTION_TENANT_ID, ['type' => 'string', 'sanitize_callback' => 'sanitize_text_field']);
});

// Admin menu
add_action('admin_menu', function () {
    add_options_page(
        'RM Backend Connector',
        'RM Backend Connector',
        'manage_options',
        RM_BC_SLUG,
        'rm_bc_render_settings_page'
    );
});

function rm_bc_render_settings_page() {
    if (!current_user_can('manage_options')) { return; }
    ?>
    <div class="wrap">
        <h1>RM Backend Connector</h1>
        <form method="post" action="options.php">
            <?php settings_fields('rm_bc_settings'); ?>
            <table class="form-table" role="presentation">
                <tr>
                    <th scope="row"><label for="rm_bc_api_base">API Base URL</label></th>
                    <td>
                        <input type="url" id="rm_bc_api_base" name="<?php echo esc_attr(RM_BC_OPTION_API_BASE); ?>" value="<?php echo esc_attr(get_option(RM_BC_OPTION_API_BASE, '')); ?>" class="regular-text" placeholder="https://api.example.com" />
                        <p class="description">Your FastAPI base (e.g., https://api.yourdomain.com). Endpoints: /api/v1/chat/stream, /api/v1/search</p>
                    </td>
                </tr>
                <tr>
                    <th scope="row"><label for="rm_bc_public_key">Public API Key</label></th>
                    <td>
                        <input type="text" id="rm_bc_public_key" name="<?php echo esc_attr(RM_BC_OPTION_PUBLIC_KEY); ?>" value="<?php echo esc_attr(get_option(RM_BC_OPTION_PUBLIC_KEY, '')); ?>" class="regular-text" />
                        <p class="description">Must match one of API_PUBLIC_KEYS on your backend. Sent as X-Public-Key.</p>
                    </td>
                </tr>
                <tr>
                    <th scope="row"><label for="rm_bc_tenant_id">Tenant ID (optional)</label></th>
                    <td>
                        <input type="text" id="rm_bc_tenant_id" name="<?php echo esc_attr(RM_BC_OPTION_TENANT_ID); ?>" value="<?php echo esc_attr(get_option(RM_BC_OPTION_TENANT_ID, '')); ?>" class="regular-text" />
                        <p class="description">If using multi-tenant, set the tenant id. Sent as X-Tenant-Id and in the chat body.</p>
                    </td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>
        <hr/>
        <h2>Shortcodes</h2>
        <ul>
            <li><code>[rm_chatbot]</code> – Renders a simple chat UI that streams responses.</li>
            <li><code>[rm_search]</code> – Renders a search box and shows top results.</li>
        </ul>
    </div>
    <?php
}

// Enqueue shared styles only when our shortcodes are used
function rm_bc_enqueue_style_once() {
    static $enqueued = false;
    if ($enqueued) { return; }
    $enqueued = true;
    wp_enqueue_style('rm-bc-style', plugins_url('assets/css/style.css', __FILE__), [], RM_BC_VERSION);
}

// Register shortcodes
add_action('init', function () {
    add_shortcode('rm_chatbot', function ($atts) {
        rm_bc_enqueue_style_once();
        $container_id = 'rm-bc-chat-' . wp_generate_uuid4();
        $api_base = esc_url_raw(get_option(RM_BC_OPTION_API_BASE, ''));
        $public_key = sanitize_text_field(get_option(RM_BC_OPTION_PUBLIC_KEY, ''));
        $tenant_id = sanitize_text_field(get_option(RM_BC_OPTION_TENANT_ID, ''));

        // Enqueue JS and pass config
        wp_enqueue_script('rm-bc-chat', plugins_url('assets/js/chat.js', __FILE__), [], RM_BC_VERSION, true);
        wp_add_inline_script('rm-bc-chat', 'window.RMBC_Config = ' . wp_json_encode([
            'apiBase' => $api_base,
            'publicKey' => $public_key,
            'tenantId' => $tenant_id,
            'containerId' => $container_id,
        ]) . ';', 'before');

        ob_start();
        ?>
        <div class="rm-bc-chat" id="<?php echo esc_attr($container_id); ?>">
            <div class="rm-bc-chat-window" aria-live="polite"></div>
            <div class="rm-bc-chat-input">
                <textarea placeholder="Type your message..."></textarea>
                <button type="button">Send</button>
            </div>
        </div>
        <?php
        return ob_get_clean();
    });

    add_shortcode('rm_search', function ($atts) {
        rm_bc_enqueue_style_once();
        $container_id = 'rm-bc-search-' . wp_generate_uuid4();
        $api_base = esc_url_raw(get_option(RM_BC_OPTION_API_BASE, ''));
        $public_key = sanitize_text_field(get_option(RM_BC_OPTION_PUBLIC_KEY, ''));
        $tenant_id = sanitize_text_field(get_option(RM_BC_OPTION_TENANT_ID, ''));

        // Enqueue JS and pass config
        wp_enqueue_script('rm-bc-search', plugins_url('assets/js/search.js', __FILE__), [], RM_BC_VERSION, true);
        wp_add_inline_script('rm-bc-search', 'window.RMBC_Search_Config = ' . wp_json_encode([
            'apiBase' => $api_base,
            'publicKey' => $public_key,
            'tenantId' => $tenant_id,
            'containerId' => $container_id,
        ]) . ';', 'before');

        ob_start();
        ?>
        <div class="rm-bc-search" id="<?php echo esc_attr($container_id); ?>">
            <form class="rm-bc-search-form">
                <input type="text" name="q" placeholder="Search..." required />
                <button type="submit">Search</button>
            </form>
            <div class="rm-bc-search-results" aria-live="polite"></div>
        </div>
        <?php
        return ob_get_clean();
    });
});
