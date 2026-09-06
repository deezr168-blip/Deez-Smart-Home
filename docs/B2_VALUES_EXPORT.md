# B2 — the targeted values export

**One copy-and-paste, about forty entities.** Where `B1` proved what *exists*,
this reports what those entities currently *say*. It is the fastest way to
close every open question in `LIVE_VERIFICATION_QUEUE.md` — faster than
repairing the live connector.

---

## Why a second export

`docs/live/states_export_2026-09-05.txt` deliberately carries **no state
values**. That was the right call: it keeps addresses, coordinates and
readings out of the repository. But it means several defects can be described
and not resolved:

| Question | What a value settles |
|---|---|
| `CR-202` `CR-203` `CR-204` | Whether "5 bills overdue" is five real bills or five helpers nobody filled in, and why the two bill sensors disagree with them |
| `CR-212` | Where "Not yet available" comes from. If a `bill_status` sensor literally says it, the fix is in Home Assistant's template, not this repository |
| `CR-213` | Whether `house_status`, `active_rooms_count` and `house_lights_on` mean what their names suggest. `casa_offline_devices` did not |
| `CR-190` | Which of the three Parents Room TV entities is the live one |
| `CR-183` | What the Family Location selector is for, and what its options are |

## What this deliberately does NOT ask for

**No account numbers, policy numbers, registration numbers or provider
logins.** `input_text.elec_account_number` and its siblings are excluded by
name. Nothing here reveals a token, a password or a URL.

Bill *amounts* are included, because the whole point is to find out whether
they are real figures or unconfigured zeros.

---

## The procedure

1. Home Assistant → **Developer tools** → the **Template** tab.
2. Clear the left-hand editor.
3. Paste the block below in exactly.
4. Copy everything from the right-hand result pane.
5. Paste it back to Claude **in chat**. Do not commit it.

```jinja
{%- set ids = [
'input_number.elec_bill_amount','input_datetime.elec_bill_due','input_boolean.elec_bill_paid',
'input_number.gas_bill_amount','input_datetime.gas_bill_due','input_boolean.gas_bill_paid',
'input_number.water_bill_amount','input_datetime.water_bill_due','input_boolean.water_bill_paid',
'input_number.council_rate_amount','input_datetime.council_rate_due','input_boolean.council_rate_paid',
'input_number.car_insurance_amount','input_datetime.car_insurance_due','input_boolean.car_insurance_paid',
'input_number.rego_amount','input_datetime.rego_due','input_boolean.rego_paid',
'sensor.bills_outstanding_total','sensor.bills_unpaid_count',
'input_number.bills_paid_ytd','input_number.bills_saved_ytd','input_number.bills_original_ytd',
'sensor.electricity_bill_status','sensor.gas_bill_status',
'sensor.electricity_bill_estimate','sensor.gas_bill_estimate','sensor.electricity_billing_cycle',
'sensor.house_status','sensor.casa_offline_devices','sensor.active_rooms_count',
'sensor.house_lights_on','sensor.open_doors_count','sensor.casa_doors_open',
'media_player.55_qled_4k_ai','media_player.55_qled_4k_ai_qa55q7faawxxy',
'media_player.master_bedroom_55_qled_4k_ai','media_player.q70f8036',
'input_select.input_select_family_location_selected',
'sensor.powerpal_gateway_powerpal_power','sensor.powerpal_gateway_powerpal_daily_energy',
'sensor.primo_5_0_1_1_ac_power','sensor.primo_5_0_1_1_energy_day',
'sensor.energy_production_today','sensor.energy_production_today_remaining',
'sensor.power_production_now','sensor.casa_solar_expected_today',
'sensor.master_bedroom_sensibo_sky_plus_air_conditioner_mode','climate.bedroom_parents_room_ac',
'sensor.living_room_living_hue_hue_sensor_temperature','sensor.bedroom_motion_sensor_temperature',
'sensor.living_room_living_room_temperature'
] -%}
{%- for e in ids -%}
{{ e }}|{{ states(e) }}|{{ state_attr(e,'unit_of_measurement') or '' }}|{{ (state_attr(e,'options') or state_attr(e,'hvac_modes') or '') | join(',') if (state_attr(e,'options') or state_attr(e,'hvac_modes')) else '' }}
{% endfor -%}
```

Each line is `entity_id | state | unit | options`. The fourth column is only
filled for the selector and the thermostat, where the list of choices is the
answer.

---

## After you paste it back

Claude reconciles it against the queue and fixes what it settles. Anything the
export shows to be a Home Assistant template problem rather than a dashboard
one — the two bill sensors are the likely case — is reported rather than
edited: those templates live in `/config`, not in this repository.
