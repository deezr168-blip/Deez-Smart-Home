// CasaRay V3 prototype — demonstration data.
//
// EVERY VALUE IN THIS FILE IS DEMONSTRATION DATA. Nothing here is read from
// Home Assistant and nothing the prototype does reaches a device.
//
// Every key in DEMO_STATES is a real entity ID taken from
// docs/live/states_export_2026-09-05.txt; tools/verify_entities.py fails if
// one is not. Where the house has no entity for something the design shows,
// the item carries `entity: null` and a `gap` explaining what is missing,
// instead of a made-up ID.

// ---------------------------------------------------------------- states --
// Shape: entity_id -> { s: state, a: attributes, ago: minutes since last change }
window.DEMO_STATES = {
  // Household
  'input_boolean.chinese_dashboard': { s: 'off' },
  'input_boolean.guest_mode': { s: 'off' },
  'todo.shopping_list': { s: '3', a: { items: ['Milk', 'Rice 5 kg', 'AA batteries'] } },
  'sensor.house_lights_on': { s: '3' },

  // People
  'person.raymond_du': { s: 'home', ago: 184 },
  'person.vinh_du': { s: 'home', ago: 52 },
  'person.ai_q_huang': { s: 'not_home', ago: 95, a: { zone: 'Work' } },
  'sensor.raymonds_iphone_battery_level': { s: '64' },
  'sensor.vine_s_phone_battery_level': { s: '81' },
  'sensor.ais_iphone_battery_level': { s: '38' },
  'sensor.raymonds_ipad_battery_level': { s: '100' },

  // Weather and outside
  'weather.forecast_home': {
    s: 'cloudy',
    a: {
      temperature: 10, humidity: 96,
      forecast: [
        { d: 'sun', hi: 14, lo: 7, c: 'partly' },
        { d: 'mon', hi: 13, lo: 8, c: 'rainy' },
        { d: 'tue', hi: 16, lo: 6, c: 'cloudy' },
        { d: 'wed', hi: 18, lo: 7, c: 'sunny' },
      ],
    },
  },
  'sensor.sun_next_setting': { s: '18:02' },

  // Living room
  'light.living_room': { s: 'on', a: { brightness: 89, color: 'warm white' }, ago: 41 },
  'light.living_room_hue_ambiance_spot_1': { s: 'unavailable' },
  'light.living_room_hue_ambiance_spot_2': { s: 'unavailable' },
  'light.living_room_hue_ambiance_spot_3': { s: 'unavailable' },
  'light.living_room_hue_ambiance_spot_4': { s: 'unavailable' },
  'binary_sensor.living_room_living_hue_hue_sensor_motion': { s: 'off', ago: 22 },
  'sensor.living_room_living_hue_hue_sensor_temperature': { s: '19.7' },
  'sensor.living_room_living_hue_hue_sensor_illuminance': { s: '41' },
  'fan.living_room_air_purifier': { s: 'on', a: { speed: 'high' } },
  'sensor.living_room_air_purifier_pm2_5': { s: '5' },
  'media_player.living_room_tv_samsung_q9_series_65': { s: 'on', a: { source: 'Netflix', volume: 26 } },
  'switch.genio_power_board_with_usb_livingroom_socket_1': { s: 'on' },
  'switch.genio_power_board_with_usb_livingroom_socket_2': { s: 'off' },
  'scene.living_room_living_room_bright': { s: 'scening' },
  'scene.living_room_living_room_relax': { s: 'scening' },
  'scene.living_room_living_room_read': { s: 'scening' },
  'scene.living_room_living_room_dimmed': { s: 'scening' },
  'scene.living_room_living_room_nightlight': { s: 'scening' },

  // Dining — note the Hue sensor here is named "living_room_living_room_*"
  // but Home Assistant assigns it to the Dining area.
  'light.dining': { s: 'on', a: { brightness: 62, color: 'warm white' }, ago: 18 },
  'switch.dinning_light_switch_1': { s: 'on' },
  'binary_sensor.living_room_living_room_motion': { s: 'off', ago: 64 },
  'sensor.living_room_living_room_temperature': { s: '17.9' },
  'camera.smart_pet_feeder': { s: 'idle' },
  'scene.dining_dining_relax': { s: 'scening' },
  'scene.dining_dining_read': { s: 'scening' },

  // Kitchen
  'binary_sensor.k_motion_sensor_motion': { s: 'on', ago: 1 },
  'switch.k_bot_p100': { s: 'on' },
  'switch.k_coffee_p100': { s: 'on' },
  'switch.k_top_p100': { s: 'on' },
  'sensor.kitchen_electrolux_fridge_temperature': { s: '3.4' },
  'binary_sensor.lg_fridge_door': { s: 'off', ago: 37 },
  'number.lg_fridge_fridge_temperature': { s: '3' },
  'number.lg_fridge_freezer_temperature': { s: '-18' },

  // Parents' room
  'climate.bedroom_parents_room_ac': { s: 'off', a: { current: 23.3, target: 22, mode: 'off' } },
  'switch.mainroomlight_switch_1': { s: 'off' },
  'binary_sensor.bedroom_motion_sensor_motion': { s: 'off', ago: 4 },
  'binary_sensor.bedroom_parents_room_ac_room_occupied': { s: 'on', ago: 4 },
  'sensor.bedroom_motion_sensor_temperature': { s: '17.6' },
  'sensor.bedroom_motion_sensor_humidity': { s: '58' },
  'media_player.55_qled_4k_ai_qa55q7faawxxy': { s: 'off' },
  'binary_sensor.m_contact_sensor_door': { s: 'off', ago: 40 },
  'event.master_bedroom_emergency_button_dad_main': { s: 'unavailable' },
  'event.master_bedroom_emergency_button_mum_main': { s: 'unavailable' },
  'binary_sensor.emergency_button_dad_cloud_connection': { s: 'on' },
  'binary_sensor.emergency_button_mum_cloud_connection': { s: 'on' },

  // Ray's bedroom
  'light.bedroom_bedroom': { s: 'off', a: { brightness: 0 } },
  'light.bedroom_nightlight': { s: 'off', a: { brightness: 0 } },
  'cover.aqara_roller_shade_driver_e1': { s: 'closed', a: { position: 0 } },
  'sensor.aqara_roller_shade_driver_e1_battery': { s: '71' },
  'media_player.q70f8036': { s: 'off' },
  'switch.r_energy_monitor_p110m': { s: 'on' },
  'sensor.r_energy_monitor_p110m_current_consumption': { s: '34.1' },
  'sensor.r_energy_monitor_p110m_voltage': { s: '230.8' },
  'sensor.r_energy_monitor_p110m_this_month_s_consumption': { s: '12.9' },
  'scene.bedroom_bedroom_read': { s: 'scening' },
  'scene.bedroom_bedroom_nightlight': { s: 'scening' },
  'scene.bedroom_bedroom_concentrate': { s: 'scening' },

  // Garage
  'switch.g_monitor_freezer_p110m': { s: 'on' },
  'sensor.g_monitor_freezer_p110m_current_consumption': { s: '113.8' },
  'sensor.g_monitor_freezer_p110m_voltage': { s: '232.5' },
  'sensor.g_monitor_freezer_p110m_this_month_s_consumption': { s: '14.5' },

  // Guest room
  'switch.g_printer_p100': { s: 'off' },
  'media_player.pogo': { s: 'unavailable' },

  // Backyard
  'binary_sensor.b_contact_sensor_door': { s: 'unavailable' },

  // Security: doors, doorbell, cameras, sirens
  'binary_sensor.f_contact_sensor_door': { s: 'off', ago: 360 },
  'sensor.front_door_last_activity': { s: 'Yesterday 11:22' },
  'sensor.front_door_battery': { s: '20' },
  'switch.front_door_motion_detection': { s: 'on' },
  'camera.front_door_live_view': { s: 'idle' },
  'camera.tapo_c425_north_wall_hd_stream_direct': { s: 'idle' },
  'camera.tapo_c200_stockroom_hd_stream_direct': { s: 'idle' },
  'camera.tapo_c420_south_wall_hd_stream_direct': { s: 'unavailable' },
  'camera.tapo_c420_east_wall_hd_stream_direct': { s: 'unavailable' },
  'sensor.tapo_c425_north_wall_battery': { s: '22' },
  'siren.tapo_c425_north_wall_siren': { s: 'off' },
  'siren.tapo_c200_stockroom_siren': { s: 'off' },
  'siren.tapo_h200': { s: 'off' },

  // Energy
  'sensor.casa_monitored_power': { s: '147.9' },
  'sensor.primo_5_0_1_1_ac_power': { s: 'unavailable' },
  'binary_sensor.casa_solar_online': { s: 'off' },
  'sensor.energy_production_today': { s: '8.8' },
  'sensor.energy_production_today_remaining': { s: '8.9' },
  'sensor.energy_production_tomorrow': { s: '4.8' },
  'sensor.power_highest_peak_time_today': { s: '14:00' },
  'sensor.electricity_maps_co2_intensity': { s: '649' },
  'sensor.electricity_maps_grid_fossil_fuel_percentage': { s: '71' },
  'sensor.powerpal_gateway_powerpal_power': { s: '612' },
  'sensor.powerpal_gateway_powerpal_daily_energy': { s: '9.4' },
  'input_number.gas_bill_mj': { s: '9437' },

  // Bills
  'input_boolean.elec_bill_paid': { s: 'off' },
  'input_number.elec_bill_amount': { s: '284.10' },
  'input_datetime.elec_bill_due': { s: '2026-10-02' },
  'input_boolean.gas_bill_paid': { s: 'off' },
  'input_number.gas_bill_amount': { s: '196.45' },
  'input_datetime.gas_bill_due': { s: '2026-09-23' },
  'input_boolean.water_bill_paid': { s: 'on' },
  'input_number.water_bill_amount': { s: '121.80' },
  'input_datetime.water_bill_due': { s: '2026-09-12' },
  'input_boolean.council_rate_paid': { s: 'off' },
  'input_number.council_rate_amount': { s: '0' },
  'input_datetime.council_rate_due': { s: 'unknown' },
  'input_boolean.rego_paid': { s: 'on' },
  'input_number.rego_amount': { s: '905.00' },
  'input_datetime.rego_due': { s: '2026-08-30' },
  'input_boolean.car_insurance_paid': { s: 'off' },
  'input_number.car_insurance_amount': { s: '1142.00' },
  'input_datetime.car_insurance_due': { s: '2026-11-15' },
  'input_number.bills_paid_ytd': { s: '4318.55' },
  'input_number.bills_saved_ytd': { s: '212.40' },

  // House health and network
  'update.home_assistant_core_update': { s: 'on', a: { installed: '2026.9.1', latest: '2026.9.3' } },
  'update.home_assistant_operating_system_update': { s: 'off', a: { installed: '16.2' } },
  'update.home_assistant_supervisor_update': { s: 'off', a: { installed: '2026.09.0' } },
  'sensor.backup_last_successful_automatic_backup': { s: 'Today 03:14' },
  'binary_sensor.eero_wan_status': { s: 'on' },
  'binary_sensor.matter_zigbee_hub_problem': { s: 'off' },
  'sensor.casa_offline_devices': { s: '41' },
  'sensor.living_room_living_hue_hue_sensor_battery': { s: '88' },
  'sensor.gas_meter_pulse_sensor_battery': { s: '54' },
  'sensor.powerpal_gateway_powerpal_battery': { s: '76' },
};

// Entities that stay readable in the "outage" scenario: helpers live inside
// Home Assistant itself, so a device outage does not take them down.
window.OUTAGE_SURVIVORS = /^(input_|todo\.|person\.|update\.|sensor\.backup_)/;

// ------------------------------------------------------------- scenarios --
// Each scenario is a patch applied over DEMO_STATES.
window.SCENARIOS = {
  evening: {},
  away: {
    'person.raymond_du': { s: 'not_home', ago: 30, a: { zone: 'Away' } },
    'person.vinh_du': { s: 'not_home', ago: 25, a: { zone: 'Away' } },
    'person.ai_q_huang': { s: 'not_home', ago: 95, a: { zone: 'Work' } },
    'light.living_room': { s: 'off', a: { brightness: 0 } },
    'light.dining': { s: 'off', a: { brightness: 0 } },
    'switch.dinning_light_switch_1': { s: 'off' },
    'sensor.house_lights_on': { s: '0' },
    'binary_sensor.k_motion_sensor_motion': { s: 'off', ago: 31 },
    'binary_sensor.bedroom_parents_room_ac_room_occupied': { s: 'off', ago: 40 },
    'media_player.living_room_tv_samsung_q9_series_65': { s: 'off' },
    'fan.living_room_air_purifier': { s: 'off', a: { speed: 'off' } },
    'binary_sensor.b_contact_sensor_door': { s: 'on', ago: 12 },
  },
  outage: '__all_devices_unavailable__',
};
