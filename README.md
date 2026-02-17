# 🌙 Custom SleepAsAndroid MQTT Sensors for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Maintainer](https://img.shields.io/badge/MAINTAINER-Roeli1996-blue.svg?style=for-the-badge)](https://github.com/Roeli1996)
[![Version](https://img.shields.io/badge/VERSION-1.4.1-green.svg?style=for-the-badge)](https://github.com/Roeli1996/ha-sleep-mqtt/releases)
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

* **Real-time Tracking:** Calculates sleep phases (Light, Deep, REM, Awake) and durations second-by-second.
* **Dynamic Sound Duration:** Instead of estimates, the integration now measures the exact time spent snoring, talking, etc., by tracking the interval between MQTT events.
* **Self-Calculated Efficiency:** Local calculation of sleep efficiency based on actual sleep time vs. total time in bed.
* **Multi-User Support:** Easily add multiple devices/users with unique MQTT topics and custom names.
* **Sound Event Counters:** Tracks snoring, talking, coughing, laughing, and shouting with a "last seen" timestamp and total duration for each.
* **Delayed Start Support:** Recognizes `sleep_tracking_paused` as a valid start event for those using a start delay in the app.
* **Standardized Translations:** Fully taalonafhankelijk (language independent) through native Home Assistant translation keys.
* **Alarm Integration:** Captures the exact timestamp of your last alarm event and automatically updates the sleep phase to Awake.

---

## Sensors Included

### Sleep Tracking & Phases
| Entity | Description |
| :--- | :--- |
| **Sleep Phase** | The current state (Light, Deep, REM, Awake). Status is fully localized via translations. |
| **Sleep Efficiency** | Real-time percentage of actual sleep vs. total time in bed. |
| **Total Sleep Duration** | Cumulative minutes spent in Light, Deep, and REM sleep combined. |

### Timestamps
| Entity | Description |
| :--- | :--- |
| **Start Time** | Exact time when tracking (or delay) was initiated. |
| **Fell Asleep** | Timestamp of first sleep detection (Light, Deep, REM or Not_Awake). |
| **End Time** | Exact time when tracking was stopped. |
| **Alarm Time** | Timestamp of the last triggered alarm or snooze event. |

### Sound & Event Counters
| Entity | Description |
| :--- | :--- |
| **Event Counts** | Incremental counters for Snoring, Talking, Coughing, Laughing, and Shouting. |
| **Duration Attributes** | Each sound sensor includes a `total_duration_minutes` attribute based on real-time event intervals. |

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

## [1.4.1] - 2026-02-17
### Added
- **Dynamic Sound Duration Tracking:** Replaced static 20s estimates with real-time interval measurements for sound events.
- **Enhanced "Fell Asleep" Logic:** Now supports `not_awake` and various sleep phases as primary triggers for falling asleep.
- **Start Delay Support:** Added handling for `sleep_tracking_paused` to ensure sensors initialize correctly when using a start timer.
- **Full Translation Engine:** Migration to a 100% translation-key-based architecture. Removed all hardcoded strings from Python for professional multi-language support.
- **Alarm-Phase Link:** Triggering an alarm now automatically forces the Sleep Phase sensor to "Awake".

## [1.4.0] - 2026-02-16
### Added
- **Stopwatch Engine:** Complete rewrite of the duration logic. Phases are now timed locally in Home Assistant.
- **Enhanced Sound Tracking:** Added counters for Coughing, Laughing, and Shouting.
- **Automated "Disabled" State:** Phase sensor automatically switches to "Disabled" (localized) when tracking stops.

## [1.3.2] and [1.3.3] - 2026-02-15
### Fixed
- **Multi-user:** Fixed a bug where multiple configurations could interfere with each other.

## [1.0.0] - 2025-02-13
### Added
- **Initial Release:** Basic MQTT sleep tracking functionality.

---
**Developed by [@Roeli1996](https://github.com/Roeli1996)**
