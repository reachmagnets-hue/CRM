<?php
/*
Plugin Name: MB Connector
Description: Connects WordPress to the ReachMagnets multi-tenant backend.
Version: 0.1.0
Author: ReachMagnets
*/

if (!defined('ABSPATH')) { exit; }

function mbc_settings_init() {
  add_option('mbc_api_base', '');
  add_option('mbc_site_id', '');
  add_option('mbc_api_key', '');

  add_settings_section('mbc_section', 'MB Connector', '__return_false', 'mbc');
  add_settings_field('mbc_api_base', 'API Base URL', 'mbc_input_api_base', 'mbc', 'mbc_section');
  add_settings_field('mbc_site_id', 'Site ID', 'mbc_input_site_id', 'mbc', 'mbc_section');
  add_settings_field('mbc_api_key', 'API Key', 'mbc_input_api_key', 'mbc', 'mbc_section');

  register_setting('mbc', 'mbc_api_base');
  register_setting('mbc', 'mbc_site_id');
  register_setting('mbc', 'mbc_api_key');
}
add_action('admin_init', 'mbc_settings_init');

function mbc_input_api_base() { echo '<input type="text" name="mbc_api_base" value="' . esc_attr(get_option('mbc_api_base')) . '" class="regular-text" />'; }
function mbc_input_site_id() { echo '<input type="text" name="mbc_site_id" value="' . esc_attr(get_option('mbc_site_id')) . '" class="regular-text" />'; }
function mbc_input_api_key() { echo '<input type="text" name="mbc_api_key" value="' . esc_attr(get_option('mbc_api_key')) . '" class="regular-text" />'; }

function mbc_menu() {
  add_options_page('MB Connector', 'MB Connector', 'manage_options', 'mbc', 'mbc_options_page');
}
add_action('admin_menu', 'mbc_menu');

function mbc_options_page() {
  echo '<div class="wrap"><h1>MB Connector</h1><form method="post" action="options.php">';
  settings_fields('mbc');
  do_settings_sections('mbc');
  submit_button();
  echo '</form></div>';
}

function mbc_enqueue_assets() {
  wp_enqueue_script('mbc-js', plugins_url('assets/js/mbc.js', __FILE__), array(), '0.1.0', true);
  wp_localize_script('mbc-js', 'mbcCfg', array(
    'apiBase' => esc_url_raw(get_option('mbc_api_base')),
    'siteId' => esc_html(get_option('mbc_site_id')),
    'apiKey' => esc_html(get_option('mbc_api_key')),
  ));
}
add_action('wp_enqueue_scripts', 'mbc_enqueue_assets');

function mbc_shortcode_chatbot() { return '<div id="mbc-chatbot"></div>'; }
function mbc_shortcode_appointment() { return '<div id="mbc-appointment"></div>'; }
function mbc_shortcode_upload() { return '<div id="mbc-upload"></div>'; }
function mbc_shortcode_voice() { return '<div id="mbc-voice"></div>'; }
add_shortcode('mbc_chatbot', 'mbc_shortcode_chatbot');
add_shortcode('mbc_appointment_form', 'mbc_shortcode_appointment');
add_shortcode('mbc_upload_form', 'mbc_shortcode_upload');
add_shortcode('mbc_voice_assistant', 'mbc_shortcode_voice');

?>
