# 🌙 Custom SleepAsAndroid MQTT Sensors for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Maintainer](https://img.shields.io/badge/MAINTAINER-Roeli1996-blue.svg?style=for-the-badge)](https://github.com/Roeli1996)
[![Version](https://img.shields.io/badge/VERSION-1.3.1-green.svg?style=for-the-badge)](https://github.com/Roeli1996/ha-sleep-mqtt/releases)
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

* **📊 Live Hypnogram (Numerical):** `Sleep Phase` sensor using integers (0-3) for instant compatibility with **ApexCharts**.
* **💤 Fell Asleep Tracking:** Records the exact timestamp when you actually transition from "Awake" into sleep.
* **🔄 Precise Calculations:** Real-time sleep duration and phase percentages using decimal values for accurate graphing.
* **📈 Long-term Statistics:** Full support for HA Long-Term Statistics (LTS) with `measurement` state classes.
* **🔊 Sound Event Counters:** Tracks snoring, talking, coughing, laughing, and yawning.
* **⏰ Smart Start & Pause:** Correctly handles "Delayed Start" and "Paused" states to ensure your tracking starts the moment you hit the bed.
* **🌍 Official Translations:** Native support for English and Dutch via Home Assistant translation files.

---

## Sensors Included
| Sensor | Description |
| :--- | :--- |
| **Sleep Phase** | Current status (Light, Deep, REM, Awake) + Sound events. |
| **Total Sleep** | Total duration of the current/last sleep session. |
| **Deep Sleep Duration** | Cumulative minutes of deep sleep. |
| **Light Sleep Duration** | Cumulative minutes of light sleep. |
| **REM Sleep Duration** | Cumulative minutes of REM sleep. |
| **Awake Duration** | Time spent awake during the session. |
| **Snoring Duration** | Total time snoring was detected. |
| **Talking Duration** | Total time talking was detected. |

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
3. **Enable MQTT** and set your Host/IP (your Home Assistant MQTT broker).
4. **Topic prefix:** e.g., `SleepAsAndroid/Arne`.
5. **Important:** Ensure **Events** is checked in the MQTT settings to enable real-time updates.

---

## 💡 Dashboard Tip: Donut Chart
To recreate the donut chart shown above, install **ApexCharts** via HACS and use this configuration (replace `arne` with your device name):

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Sleep Distribution
  show_states: true
  colorize_states: true
chart_type: donut
series:
  - entity: sensor.arne_sleep_deep_sleep
    name: Deep
    color: "#1A237E"
  - entity: sensor.arne_sleep_rem_sleep
    name: REM
    color: "#4FC3F7"
  - entity: sensor.arne_sleep_light_sleep
    name: Light
    color: "#90CAF9"
  - entity: sensor.arne_sleep_awake
    name: Awake
    color: "#FFAB91"
```
# Changelog

All notable changes to the **SleepAsAndroid MQTT Custom** integration will be documented in this file.

## [1.3.1] - 2026-02-15
### Added
- **Full REM Sleep Support:** Dedicated tracking for REM sleep stages.
- **Sound Event Tracking:** New sensors for **Snoring** and **Talking** durations (in minutes).
- **Percentage Analysis:** Added `percentage_of_total` attributes to all duration sensors for deeper analysis.
- **Long-Term Statistics:** Support for `total_increasing` state classes, enabling native Home Assistant history graphs and LTS.

### Changed
- **Intelligent Phase Tracking:** The main "Sleep Phase" sensor now features "memory," retaining the current sleep stage during sound events (e.g., `Deep Sleep (Snoring)`).
- **Cleanup:** Removed unused ambient noise detection sensors to prevent entity clutter.
- **Translation Update:** Fully updated Dutch (`nl.json`) and English (`strings.json`) localization.

## [1.3.0] - 2026-02-14
### Added
- **Official HACS Support:** Added `hacs.json` and GitHub Actions for repository validation.
- **GitHub Topics:** Repository categorized with `home-assistant`, `hacs`, and `integration` for better discoverability.
- **Improved Metadata:** Updated `manifest.json` with official documentation and issue tracker links.
- **Hypnogram Visualization:** Added example code for ApexCharts in the README.

## [1.2.0] - 2026-02-13
### Added
- **Official Translation Framework:** Full implementation of `strings.json` and `translations/` folder for EN/NL support.
- **Fell Asleep Sensor:** New dedicated sensor capturing the exact timestamp of the first transition to a sleep stage.
- **Long-Term Statistics:** Added `state_class: measurement` to all numerical sensors to enable native Home Assistant history analysis and energy-style dashboards.

### Changed
- **Numerical-First Architecture:** Sensors now return numerical values (integers/floats) instead of strings for native graphing and recorder support.
- **Smart Pause Handling:** Improved session initialization when using delayed starts (`sleep_tracking_paused`).
- **Auto-Recovery:** The tracker now auto-starts if a phase event is received but a start event was missed.

## [1.1.0] - 2026-02-13
### Added
- **Multi-Device Support:** Initial support for tracking multiple devices simultaneously.
- **Sound Events:** Added tracking for snoring, coughing, talking, laughing, and yawning.

## [1.0.0] - 2025-02-13
### Added
- **Initial Release:** Basic MQTT sleep tracking functionality including start, stop, and phase events.
