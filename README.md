# 🌙 Custom SleepAsAndroid MQTT Sensors for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Maintainer](https://img.shields.io/badge/MAINTAINER-Roeli1996-blue.svg?style=for-the-badge)](https://github.com/Roeli1996)
[![Version](https://img.shields.io/badge/VERSION-1.1.0-green.svg?style=for-the-badge)](https://github.com/Roeli1996/ha-sleep-mqtt/releases)
[![License](https://img.shields.io/badge/LICENSE-MIT-yellow.svg?style=for-the-badge)](LICENSE)

This custom integration brings advanced sleep tracking analytics from the **SleepAsAndroid** app directly into Home Assistant via MQTT. Unlike standard implementations, this version calculates live statistics and features a dedicated **Real-time Hypnogram** sensor for tracking sleep stages as they happen.

---

## ✨ Features

* **📊 Live Hypnogram (New in V2):** Dedicated `Sleep Phase` sensor for tracking stages (Deep, Light, REM, Awake) in real-time.
* **🔄 Real-time Calculations:** Live calculation of sleep duration and phase distribution percentages.
* **📈 Sleep Efficiency:** Automatic tracking of your sleep quality percentage.
* **🔊 Sound Event Counters:** Specifically tracks occurrences of snoring, talking, coughing, laughing, or yawning.
* **⏰ Alarm Tracking:** Records the exact time your alarm starts ringing.
* **👥 Multi-Device Support:** Add multiple people/phones as separate devices without data conflicts.
* **🌍 Multi-language:** Automatically detects your Home Assistant language (Supports English and Dutch natively).

---

## 🚀 Installation

### Step 1: Via HACS (Recommended)
1.  Open **HACS** in your Home Assistant instance.
2.  Click the three dots in the top right corner and select **Custom repositories**.
3.  Paste your GitHub repository URL: `https://github.com/Roeli1996/ha-sleep-mqtt`
4.  Select **Integration** as the category and click **Add**.
5.  Search for **SleepAsAndroid MQTT Custom** and click **Download**.
6.  **Restart** Home Assistant.

### Step 2: Configure SleepAsAndroid App
Configure the app on your Android device to broadcast data:
1.  Go to **Settings > Services > MQTT**.
2.  **Enable MQTT.**
3.  **Host:** Your MQTT broker IP (e.g., your Home Assistant / Mosquitto IP).
4.  **Topic prefix:** Use a unique path, e.g., `SleepAsAndroid/Arne`.
5.  **Client ID:** Choose a unique name for the device.
6.  **Important:** Ensure **Events** is checked in the MQTT settings to enable the Hypnogram feature.

### Step 3: Add the Integration
1.  Go to **Settings > Devices & Services**.
2.  Click **Add Integration** and search for **SleepAsAndroid MQTT Custom**.
3.  Fill in the details:
    * **Device Name:** Name to display in HA (e.g., Arne).
    * **Topic Prefix:** The exact path used in the app (e.g., `SleepAsAndroid/Arne`).

---

## 📈 Available Sensors

| Sensor | Description | Attributes |
| :--- | :--- | :--- |
| **Status** | Current app activity/event | Last event string |
| **Sleep Phase** | Current stage (Deep, REM, Light, Awake) | Time-stamped history |
| **Sleep Duration** | Total time in bed (e.g., 7h 15m) | Decimal hours |
| **Efficiency** | Percentage of time spent actually sleeping | - |
| **Phase Breakdown** | Distribution of Deep, Light, REM, and Awake | Formatted time & seconds |
| **Sound Events** | Counters for snoring, talking, coughing, etc. | Last detected timestamp |
| **Alarm Time** | The time the last alarm was triggered | - |
| **Last Sync** | Timestamp of the last received MQTT message | - |

---
