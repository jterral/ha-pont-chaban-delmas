# Pont Chaban-Delmas HA

Home Assistant Integration for Pont Chaban-Delmas 🌉🚢.

[![GitHub Release](https://img.shields.io/github/release/jterral/ha-pont-chaban-delmas.svg)](https://github.com/jterral/ha-pont-chaban-delmas/releases)
[![License](https://img.shields.io/github/license/jterral/ha-pont-chaban-delmas.svg)](LICENSE)
[![hacs](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz/)

## 📋 Overview

This Home Assistant integration provides real-time information about the Pont Chaban-Delmas bridge in Bordeaux, France. Monitor upcoming bridge closures to plan your routes and activities around this iconic landmark. 🚗⛵

## ✨ Features

- 🕒 **Real-time bridge closure schedule** - Know when the bridge will be raised
- 📅 **Upcoming closures list** - See all planned closures in advance
- 🚢 **Boat information** - Know which boat is causing the closure
- ⏱️ **Closure duration** - See how long the bridge will be closed
- 🔴 **Total vs Partial closures** - Understand the type of closure
- 🔄 **Automatic updates** - Data refreshed every 15 minutes

## 💾 Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the 3 dots in the top right corner and select "Custom repositories"
4. Add `https://github.com/jterral/ha-pont-chaban-delmas` as a custom repository
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/pont_chaban_delmas` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## ⚙️ Configuration

### Via UI (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Pont Chaban-Delmas**
4. Click on it to set up

### Via YAML (Legacy)

Add to your `configuration.yaml`:

```yaml
sensor:
  - platform: pont_chaban_delmas
```

Then restart Home Assistant.

## 📈 Sensors

The integration provides two sensors:

### Next Closure

- **Entity ID**: `sensor.pont_chaban_delmas_next_closure`
- **State**: Timestamp of the next closure start time
- **Attributes**:
  - `start`: Closure start time
  - `end`: Closure end time
  - `boat`: Boat name
  - `duration_minutes`: Duration in minutes
  - `type`: Type of closure
  - `is_total`: Whether it's a total closure

### Upcoming Closures

- **Entity ID**: `sensor.pont_chaban_delmas_upcoming_closures`
- **State**: Timestamp of the next closure start time
- **Attributes**:
  - `count`: Total number of upcoming closures
  - `closures`: List of up to 10 upcoming closures with full details

## 🔔 Automation Examples

### Notify when bridge closure is approaching

```yaml
automation:
  - alias: "Notify Bridge Closure"
    trigger:
      - platform: time_pattern
        minutes: "/30"
    condition:
      - condition: template
        value_template: >
          {% set next_closure = state_attr('sensor.pont_chaban_delmas_next_closure', 'start') %}
          {{ next_closure != None and (as_timestamp(next_closure) - as_timestamp(now())) < 3600 }}
    action:
      - service: notify.mobile_app
        data:
          title: "Pont Chaban-Delmas Closure Alert"
          message: >
            The bridge will close in less than 1 hour for {{ state_attr('sensor.pont_chaban_delmas_next_closure', 'boat') }}.
```

## 🛠️ Development

### Setup

```bash
# Create virtual environment
make python-venv

# Activate virtual environment
source .venv/bin/activate

# Run tests
make python-test

# Run linter
make python-lint

# Format code
make python-format
```

### Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=custom_components/pont_chaban_delmas --cov-report=html
```

## 📊 Data Source

Data is provided by [Bordeaux Métropole Open Data](https://datahub.bordeaux-metropole.fr/).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Support

If you find this integration useful, please consider giving it a star on GitHub!
