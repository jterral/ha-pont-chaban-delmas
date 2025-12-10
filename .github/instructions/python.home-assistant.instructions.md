# Python Home Assistant Integration Development Instructions

This document provides strict guidelines and best practices for developing a **custom Home Assistant integration** in Python. It consolidates and adapts conventions from general Python coding standards 【filecite】turn0file0】 into Home Assistant–specific requirements.

---

## 1. Project Structure

Follow the canonical Home Assistant integration layout:

```
custom_components/
└── your_integration/
    ├── __init__.py
    ├── manifest.json
    ├── config_flow.py
    ├── const.py
    ├── coordinator.py
    ├── sensor.py (and/or switch.py, binary_sensor.py…)
    ├── services.yaml (optional)
    └── translations/
        └── en.json
```

**Rules:**

- Never add Python code outside the integration folder.
- Keep constants in `const.py` only.
- Place all API I/O and update logic inside a coordinator inheriting from `DataUpdateCoordinator`.

---

## 2. Python Code Requirements

### 2.1 Type hints and PEP conventions

- All functions and methods must include type hints.
- Add docstrings to all functions and classes.
- Follow PEP 8 and PEP 257.

### 2.2 Structure and clarity

- Code must always prefer readability over cleverness.
- Split complex logic across small functions.
- Include comments explaining _why_ a choice is made, not _what_ it does.

### 2.3 No blocking I/O

- Never use synchronous network or file system calls inside Home Assistant.
- Use `async` / `await` everywhere.
- For third-party libraries that are blocking, wrap calls with:

  ```python
  await hass.async_add_executor_job(func)
  ```

### 2.4 Logging

- Use Home Assistant logging:

  ```python
  from homeassistant.core import HomeAssistant
  import logging

  LOGGER = logging.getLogger(__name__)
  LOGGER.debug("Message")
  ```

- Do not log sensitive data.
- Do not log JSON payloads directly unless sanitized.

---

## 3. Manifest Rules

The `manifest.json` must:

- Include `domain`, `name`, `version`, and `requirements`.
- Pin dependencies to exact versions.
- Use a valid `iot_class` (e.g. `cloud_polling`, `local_push`).
- Never expose private URLs.

Example:

```json
{
  "domain": "your_integration",
  "name": "Your Integration",
  "version": "1.0.0",
  "codeowners": ["@yourgithub"],
  "documentation": "https://github.com/...",
  "requirements": ["yourapi==0.4.2"],
  "iot_class": "cloud_polling"
}
```

---

## 4. Config Flow Standards

All new integrations must support UI configuration:

- Implement `config_flow.py` using `ConfigFlow` and `OptionsFlow`.
- Validate user input early with descriptive errors.
- Use translation keys for all strings.
- Never access the network inside schema definitions.

---

## 5. Coordinators and Data Handling

### 5.1 Use DataUpdateCoordinator

All periodic data retrieval must go through a coordinator:

```python
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
```

### 5.2 Rules

- Respect Home Assistant's central update interval.
- Never perform device I/O inside entities.
- Store raw API responses in the coordinator.
- Parse API responses before exposing them to entities.

---

## 6. Entities

### 6.1 Naming

- Set `unique_id` for every entity.
- Use clear and stable naming conventions.

### 6.2 Entity properties

Entities must implement:

- `device_info` where applicable
- `available`
- `native_value` or entity-specific value accessors

### 6.3 No Blocking Logic

Entities must never:

- Call the API directly
- Perform heavy computations
- Depend on I/O

All data comes from the coordinator.

---

## 7. Services

If the integration exposes services:

- Define them in `services.yaml`.
- Document parameters.
- Validate input.
- Never allow arbitrary Python execution.
- Implement services in `__init__.py` or component-level handlers.

---

## 8. Translations

- All user-facing strings must live in `translations/*.json`.
- Do not hardcode text.

---

## 9. Testing

### 9.1 Unit tests

- Cover API client logic and coordinator logic.
- Use pytest.
- Mock HTTP calls.

### 9.2 Home Assistant test harness

Use:

```python
from homeassistant.core import HomeAssistant
```

Tests must verify:

- Config flow validation
- Entity creation
- Coordinator refresh

---

## 10. Edge Cases and Reliability

- Handle empty or malformed API responses.
- Gracefully handle timeouts.
- Implement exponential backoff if needed.
- Retry only inside the coordinator.
- Ensure integration loads even without network connectivity.

---

## 11. Documentation

Every integration must include:

- Clear installation steps
- Configuration options
- Entity descriptions
- Service documentation

---

## 12. Example Template

```python
def example_function(value: int) -> int:
    """
    Example function showing proper typing and docstring usage.

    Parameters:
        value: Example integer parameter.

    Returns:
        The incremented value.
    """
    return value + 1
```

---

## 13. Summary of Mandatory Rules

- Fully async integration
- Config flow required
- Coordinator required
- Clear logging without sensitive data
- Full typing and docstrings
- No blocking code
- No untested logic
- No hardcoded strings
- Manifest pinned dependencies

---

This file defines the baseline for building compliant, maintainable, and idiomatic Home Assistant integrations using Python.
