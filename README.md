# 🌙 SleepAsAndroid MQTT Custom for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Maintainer](https://img.shields.io/badge/MAINTAINER-Roeli1996-blue.svg?style=for-the-badge)](https://github.com/Roeli1996)
[![Version](https://img.shields.io/badge/VERSION-1.4.3-green.svg?style=for-the-badge)](https://github.com/Roeli1996/ha-sleep-mqtt/releases)
[![License](https://img.shields.io/badge/LICENSE-MIT-yellow.svg?style=for-the-badge)](LICENSE)

This custom integration brings advanced sleep tracking analytics from the **SleepAsAndroid** app directly into Home Assistant via MQTT. It features live statistics calculation, a **Real-time Hypnogram**, and full support for Long-Term Statistics.

---

## 📊 Visualisation Examples

### Sleep Analytics Dashboard
The integration provides a comprehensive set of sensors to monitor your rest. Below is an example of how the sensors and the sleep distribution look in a Home Assistant dashboard.

<p align="center">
  <img src="screenshots/sensors_overview.png" width="350" alt="Sensors Overview">
  <img src="screenshots/donut_chart.png" width="350" alt="Sleep Distribution Donut">
</p>

* **Left:** Overview of the numerical and time-based sensors provided by the integration.
* **Right:** A dynamic Donut Chart showing the balance between Deep, Light, REM, and Awake stages.

---

## ✨ Features

* **Real-time Tracking:** Calculates sleep phases (Light, Deep, REM, Awake) and durations second-by-second locally in Home Assistant.
* **Session Integrity Protection:** Prevents mid-night resets. If the app sends a new start event while a session is already active (e.g., due to a connection drop), the integration maintains the current data.
* **Phase Percentage Attributes:** The main Sleep Phase sensor now includes live-calculated attributes for the percentage of Deep, Light, REM, and Awake time relative to total time in bed.
* **Dynamic Sound Duration:** Measures the exact time spent snoring, talking, coughing, laughing, or shouting by tracking intervals between MQTT events.
* **Self-Calculated Efficiency:** Local calculation of sleep efficiency based on actual sleep time vs. total time in bed.
* **Strict Alarm Logic:** Automatically updates the sleep phase to **Awake** and captures the exact timestamp only when the alarm actually starts alerting (`alarm_alert_start`).
* **Multi-User Support:** Add multiple devices/users with unique MQTT topics and custom names in the UI.
* **Fully Localized:** Language-independent architecture using native Home Assistant translation keys (`strings.json` and `nl.json` support).

---

## Sensors Included

### Sleep Tracking & Phases
| Entity | Description |
| :--- | :--- |
| **Sleep Phase** | The current state (Light, Deep, REM, Awake). Status is fully localized via translations. Includes attributes: `deep_sleep_percentage`, `light_sleep_percentage`, `rem_sleep_percentage`, `awake_percentage`. |
| **Sleep Efficiency** | Real-time percentage of actual sleep vs. total time in bed. |
| **Total Sleep Duration** | Cumulative minutes spent in Light, Deep, and REM sleep combined. |
| **Phase Durations** | Individual sensors for Light, Deep, REM, and Awake duration in minutes. |

### Timestamps
| Entity | Description |
| :--- | :--- |
| **Start Time** | Exact time when tracking (or delay) was initiated. |
| **Fell Asleep** | Timestamp of first sleep detection (Light, Deep, REM, or Not_Awake). |
| **End Time** | Exact time when tracking was stopped. |
| **Alarm Time** | Timestamp of the last **actual** alarm alert (`alarm_alert_start`). |

### Sound & Event Counters
| Entity | Description |
| :--- | :--- |
| **Event Counters** | Individual sensors for Snoring, Talking, Coughing, Laughing, and Shouting. |
| **Sound Attributes** | Each sound sensor includes `total_duration_minutes` and `last_seen` timestamp. |

### Diagnostics
| Entity | Description |
| :--- | :--- |
| **Last MQTT Message** | Raw payload of the last received MQTT message for debugging purposes. |

---

## 🚀 Installation

### Step 1: Via HACS (Recommended)
1. Open **HACS** > Click the three dots (top right) > **Custom repositories**.
2. Paste: `https://github.com/Roeli1996/ha-sleep-mqtt`
3. Select **Integration** as the category and click **Add**.
4. Search for **SleepAsAndroid MQTT Custom** and download.
5. **Restart** Home Assistant.

### Step 2: Configure SleepAsAndroid App
1. Open the app on your Android device.
2. Go to **Settings > Services > MQTT**.
3. **Enable MQTT** and set your Host/IP.
4. **Topic prefix:** e.g., `SleepAsAndroid/Roeli`.
5. **Important:** Ensure **Events** is checked in the MQTT settings.

---

# Changelog

## [1.4.3] - 2026-02-18
### Added
- **Session Protection:** Implemented logic to ignore redundant `sleep_tracking_started` events if a session is already active, preventing data loss during reconnects.
- **Percentage Analytics:** Added `deep_sleep_percentage`, `light_sleep_percentage`, `rem_sleep_percentage`, and `awake_percentage` as attributes to the Phase sensor.
- **Strict Alarm Trigger:** Refined alarm logic to only trigger on `alarm_alert_start`, ignoring `before_alarm` events for more accurate timestamps.
- **Updated Translations:** Expanded `strings.json` and `nl.json` to include all new sensors and states in English and Dutch.

## [1.4.2] - 2026-02-17
### Fixed
- **Start time logic:** Fixed a bug where the start time was not always correctly captured during specific MQTT sequences.

## [1.4.1] - 2026-02-17
### Added
- **Dynamic Sound Duration Tracking:** Replaced static 20s estimates with real-time interval measurements for sound events.
- **Enhanced "Fell Asleep" Logic:** Now supports `not_awake` and various sleep phases as primary triggers for falling asleep.
- **Start Delay Support:** Added handling for `sleep_tracking_paused` to ensure sensors initialize correctly when using a start timer in the app.
- **Full Translation Engine:** Migration to a 100% translation-key-based architecture. Removed all hardcoded strings from Python.

## [1.4.0] - 2026-02-16
### Added
- **Stopwatch Engine:** Complete rewrite of the duration logic. Phases are now timed locally in Home Assistant instead of relying on external calculations.
- **Enhanced Sound Tracking:** Added sensors and counters for Coughing, Laughing, and Shouting.
- **Automated "Disabled" State:** Phase sensor automatically switches to "Disabled" when tracking stops.

## [1.3.2] & [1.3.3] - 2026-02-15
### Fixed
- **Multi-user Support:** Fixed a critical bug where multiple device configurations could interfere with each other's data.

## [1.0.0] - 2025-02-13
### Added
- **Initial Release:** Basic MQTT sleep tracking functionality, supporting core sleep phases and efficiency.

---
**Developed by [@Roeli1996](https://github.com/Roeli1996)**
