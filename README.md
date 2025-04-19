# 🚌 Bus Arrival Alert

A custom Home Assistant integration that monitors bus arrivals at your selected stops and alerts you when your bus is approaching!

Built especially for Transport for London (TfL) stops.

---

## ✨ Features

- 🚩 Monitor multiple bus stops simultaneously
- 🚌 Track specific bus lines (optional)
- 🔔 Fire real-time `bus_arrival_alert_arrival` events for automations (e.g., TTS announcements)
- 📊 Provides sensor entities showing upcoming arrival summary for each stop.
- 🛠️ Full configuration via the Home Assistant UI (no YAML required for setup/options)

---

## 📦 Installation

1.  **Using HACS (Recommended):**
    - Go to HACS → Integrations → Explore & Add Repositories.
    - Search for "Bus Arrival Alert" and install it.
    - Restart Home Assistant.
2.  **Manual Installation:**

    - Copy the `custom_components/bus_arrival_alert/` folder into your Home Assistant `/config/custom_components/` directory.
    - Restart Home Assistant.

3.  Go to **Settings → Devices & Services → + Add Integration**.
4.  Search for **Bus Arrival Alert** and configure your stops.

---

## ⚙️ Configuration

The integration uses a UI-based **Config Flow** and **Options Flow**:

- During setup (**Add Integration**):
  - Define the update frequency (scan interval).
  - Add one or more bus stops:
    - **Name:** A friendly name for the stop (e.g., "Home Stop").
    - **Stop ID:** The official TfL StopPoint ID (e.g., `490008660N`).
    - **(Optional) Line Names:** Comma-separated list of bus routes to monitor (e.g., `159, 59`). Leave blank for all lines.
- After setup (**Options** button on the integration card):
  - Change the update frequency.
  - Add, edit, or remove bus stops.

✅ No YAML configuration needed!

---

## 📊 Sensor Entities

For each configured bus stop, a sensor entity is created.

- **State:** Shows the number of upcoming buses (e.g., "2 buses") or "No buses". Will show "Unknown" if data cannot be fetched.
- **Attributes:** Contains a detailed list of upcoming arrivals (`arrivals`).

---

## 🔔 Example Automation

Use the `bus_arrival_alert_arrival` event (fired _per stop_ with arrivals) to trigger TTS announcements or notifications.

```yaml
- alias: "Bus Arrival Notification for Home Stop"
  id: "bus_arrival_notify_home" # Add a unique ID
  trigger:
    - platform: event
      event_type: bus_arrival_alert_arrival # Updated event type
      event_data:
        stop_name: "Home Stop" # Filter for a specific stop using its configured name
  condition:
    # Optional: Only announce if there are actually buses arriving
    - condition: template
      value_template: "{{ trigger.event.data.arrivals | count > 0 }}"
  action:
    - service: tts.speak # Or notify.notify service etc.
      target:
        # Use the tts service created via the UI (e.g., google_translate_say)
        entity_id: tts.google_translate_say
      data:
        cache: true
        media_player_entity_id: media_player.bedroom_speaker # Your media player
        message: >
          {% set stop = trigger.event.data.stop_name %}
          {% set grouped = trigger.event.data.grouped_arrivals %}
          Attention for {{ stop }}:
          {% for arrival in grouped %}
            Bus {{ arrival.line }} towards {{ arrival.destination }} arriving in
            {% set minutes_list = arrival.minutes %}
            {% if minutes_list | count == 1 %}
              {% set minutes = minutes_list[0] %}
              {% if minutes == 0 %} now. {% elif minutes == 1 %} 1 minute. {% else %} {{ minutes }} minutes. {% endif %}
            {% else %}
              {{ minutes_list | join(', ') }} minutes. {# More concise listing #}
            {% endif %}
          {% endfor %}
```

_Note: Adjust `tts.google_translate_say` and `media_player.bedroom_speaker` to match your entity IDs._

---

## 🛠️ Known Limitations

- Supports Transport for London (TfL) API out of the box — requires code changes for other transit systems.
- Does not currently support configuring API keys, which might lead to rate limiting with very frequent updates or many stops.

---

## 🧰 Future Improvements

- Add optional API key configuration.
- Add service to reload stops without HA restart (currently requires config entry reload).
- Add nicer custom icons per stop.
- More robust handling of different API response formats.

---

## 💛 License

This project is licensed under the [MIT License](LICENSE).
