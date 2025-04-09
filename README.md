# 🚌 Bus Arrival Alert

A custom Home Assistant integration that monitors bus arrivals at your selected stops and alerts you when your bus is approaching!

Built especially for Transport for London (TfL) stops, but easily adaptable to any similar real-time API.

---

## ✨ Features

- 🚩 Monitor multiple bus stops simultaneously
- 🚌 Track specific bus lines (optional)
- 🕒 Configure monitoring windows (start and end time)
- 🗕️ Choose active days of the week (e.g., only Monday and Thursday)
- 🔔 Fire real-time `bus_arrival_alert` events
- 🎤 Use TTS (Text-to-Speech) to announce upcoming buses naturally
- 🛠️ Full configuration via the Home Assistant UI (no YAML required)

---

## 📦 Installation

1. Copy the `custom_components/bus_arrival_alert/` folder into your Home Assistant `/config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → + Add Integration**.
4. Search for **Bus Arrival Alert** and configure your stops.

---

## ⚙️ Configuration

The integration uses a UI-based **Config Flow** and **Options Flow**:

- During setup, provide:
  - Custom name
  - Bus stop ID (TfL stop ID)
  - (Optional) Bus line names to filter (comma-separated)
  - Start and end time
  - (Optional) Days of the week (multi-select)
- After setup, you can edit any of these fields via the **Options** menu.

✅ No YAML configuration needed!

---

## 🔔 Example Automation

Use the `bus_arrival_alert` event to trigger TTS announcements or notifications.

```yaml
- alias: "Bus Arrival Notification"
  trigger:
    - platform: event
      event_type: bus_arrival_alert
  action:
    - service: tts.speak
      target:
        entity_id: tts.google_translate_en_com
      data:
        cache: true
        media_player_entity_id: media_player.bedroom_pair
        message: >
          {%- for line, arrivals in trigger.event.data.arrivals.items() %}
            {% if arrivals | length == 1 %}
              {% set minutes = arrivals[0] %}
              {% if minutes == 0 %}
                Bus {{ line }} is arriving now.
              {% elif minutes == 1 %}
                Bus {{ line }} arriving in 1 minute.
              {% else %}
                Bus {{ line }} arriving in {{ minutes }} minutes.
              {% endif %}
            {% else %}
              Bus {{ line }} arriving in
              {%- for minute in arrivals %}
                {%- if not loop.first %} and {% endif -%}
                {{ minute }} minutes
              {%- endfor -%}.
            {% endif %}
          {%- endfor %}
```

✅ This TTS message dynamically adapts based on how many buses are arriving and when.

---

## 🛠️ Known Limitations

- No `sensor` entities created (pure event-based integration).
- Supports Transport for London (TfL) API out of the box — may require adaptation for other transit systems.
- Requires Home Assistant 2023.5 or newer (for full Config Flow/Options Flow support).

---

## 🧰 Future Improvements

- Add optional sensor creation (show next bus arrival as entity)
- Add service to reload stops without HA restart
- Add nicer custom icons per stop
- Publish to HACS for one-click install

---

## 💛 License

This project is licensed under the [MIT License](LICENSE).
