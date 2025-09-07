<?php
/*
Plugin Name: Ollama Chat (Multi-tenant)
Description: Floating chat widget connecting to shared FastAPI backend. Shortcode: [ollama_chat tenant="auto"].
Version: 0.1.0
Author: You
*/

if (!defined('ABSPATH')) { exit; }

class Ollama_Chat_Plugin {
  const OPTION_GROUP = 'ollama_chat_options_group';
  const OPTION_NAME = 'ollama_chat_options';

  public function __construct() {
    add_action('admin_menu', [$this, 'add_settings_page']);
    add_action('admin_init', [$this, 'register_settings']);
    add_shortcode('ollama_chat', [$this, 'shortcode']);
    add_action('wp_enqueue_scripts', [$this, 'enqueue_assets']);
  add_action('wp_footer', [$this, 'inject_widget']);
  }

  public function add_settings_page() {
    add_options_page('Ollama Chat', 'Ollama Chat', 'manage_options', 'ollama-chat', [$this, 'render_settings_page']);
  }

  public function register_settings() {
    register_setting(self::OPTION_GROUP, self::OPTION_NAME, [
      'type' => 'array',
      'sanitize_callback' => [$this, 'sanitize_options'],
      'default' => [
        'api_base' => '',
        'public_key' => '',
  'tenant_override' => '',
  'auto_inject' => '0'
      ],
    ]);
    add_settings_section('ollama_chat_main', 'Main Settings', function() {
      echo '<p>Configure backend API and keys.</p>';
    }, 'ollama-chat');
    add_settings_field('api_base', 'API Base URL', [$this, 'field_api_base'], 'ollama-chat', 'ollama_chat_main');
    add_settings_field('public_key', 'Public Client Key', [$this, 'field_public_key'], 'ollama-chat', 'ollama_chat_main');
    add_settings_field('tenant_override', 'Tenant Override (optional)', [$this, 'field_tenant_override'], 'ollama-chat', 'ollama_chat_main');
  add_settings_field('auto_inject', 'Show widget on all pages', [$this, 'field_auto_inject'], 'ollama-chat', 'ollama_chat_main');
  }

  public function sanitize_options($opts) {
    $clean = [];
    $clean['api_base'] = esc_url_raw($opts['api_base'] ?? '');
    $clean['public_key'] = sanitize_text_field($opts['public_key'] ?? '');
    $clean['tenant_override'] = sanitize_text_field($opts['tenant_override'] ?? '');
  $clean['auto_inject'] = isset($opts['auto_inject']) && $opts['auto_inject'] ? '1' : '0';
    return $clean;
  }

  public function field_api_base() {
    $opts = get_option(self::OPTION_NAME);
    printf('<input type="url" name="%s[api_base]" value="%s" class="regular-text" placeholder="https://api.example.com" />', self::OPTION_NAME, esc_attr($opts['api_base'] ?? ''));
  }
  public function field_public_key() {
    $opts = get_option(self::OPTION_NAME);
    printf('<input type="text" name="%s[public_key]" value="%s" class="regular-text" />', self::OPTION_NAME, esc_attr($opts['public_key'] ?? ''));
  }
  public function field_tenant_override() {
    $opts = get_option(self::OPTION_NAME);
    printf('<input type="text" name="%s[tenant_override]" value="%s" class="regular-text" placeholder="site_a" />', self::OPTION_NAME, esc_attr($opts['tenant_override'] ?? ''));
  }
  public function field_auto_inject() {
    $opts = get_option(self::OPTION_NAME);
    $checked = !empty($opts['auto_inject']) && $opts['auto_inject'] === '1' ? 'checked' : '';
    printf('<label><input type="checkbox" name="%s[auto_inject]" value="1" %s /> Enable floating widget on all pages</label>', self::OPTION_NAME, $checked);
  }

  public function render_settings_page() {
    if (!current_user_can('manage_options')) { return; }
    echo '<div class="wrap"><h1>Ollama Chat Settings</h1><form method="post" action="options.php">';
    settings_fields(self::OPTION_GROUP);
    do_settings_sections('ollama-chat');
    submit_button();
    echo '</form></div>';
  }

  public function enqueue_assets() {
    $opts = get_option(self::OPTION_NAME);
    wp_register_style('ollama-chat-css', plugins_url('assets/chat.css', __FILE__), [], '0.1.0');
    wp_register_script('ollama-chat-js', plugins_url('assets/chat.js', __FILE__), [], '0.1.0', true);
    wp_localize_script('ollama-chat-js', 'OLLAMA_CHAT_CFG', [
      'api_base' => $opts['api_base'] ?? '',
      'public_key' => $opts['public_key'] ?? '',
      'tenant_override' => $opts['tenant_override'] ?? '',
    ]);
  }

  public function shortcode($atts) {
    $atts = shortcode_atts(['tenant' => 'auto'], $atts, 'ollama_chat');
    wp_enqueue_style('ollama-chat-css');
    wp_enqueue_script('ollama-chat-js');
    $tenant_attr = esc_attr($atts['tenant']);
    return '<div id="ollama-chat-widget" data-tenant="' . $tenant_attr . '"></div>';
  }

  public function inject_widget() {
    if (is_admin()) { return; }
    $opts = get_option(self::OPTION_NAME);
    if (empty($opts['auto_inject']) || $opts['auto_inject'] !== '1') { return; }
    // Enqueue assets and print container at footer
    wp_enqueue_style('ollama-chat-css');
    wp_enqueue_script('ollama-chat-js');
    echo '<div id="ollama-chat-widget" data-tenant="auto"></div>';
  }
}

new Ollama_Chat_Plugin();
