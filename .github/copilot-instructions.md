---
description: "Global instructions for GitHub Copilot."
applyTo: "*"
---

## Project Context

Home Assistant integration for **Pont Chaban-Delmas** bridge in Bordeaux, France. Monitors real-time bridge closure data via public API and exposes it through HA sensors.

## Architecture (DDD Pattern)

This integration follows **Domain-Driven Design** principles with clear separation of concerns:

### Layer Structure

- **Domain Layer** ([domain.py](../custom_components/pont_chaban_delmas/domain.py)): `BridgeClosure` value object — pure business logic, no dependencies
- **Infrastructure Layer** ([pont_chaban.py](../custom_components/pont_chaban_delmas/pont_chaban.py)): `PontChabanRepository` — API client with DTOs (`ApiBridgeResponse`, `ApiResponse`)
- **Application Layer** ([coordinator.py](../custom_components/pont_chaban_delmas/coordinator.py)): `PontChabanCoordinator` — orchestrates data fetching, inherits HA's `DataUpdateCoordinator`
- **Presentation Layer** ([sensor.py](../custom_components/pont_chaban_delmas/sensor.py)): Sensor entities — display data to users

### Key Flow

1. Repository fetches raw data from `datahub.bordeaux-metropole.fr` API → returns DTOs
2. Repository converts DTOs to domain objects (`BridgeClosure`)
3. Coordinator filters/processes domain objects → stores in `self.data`
4. Sensors read from `coordinator.data` → expose as HA entities with attributes

## Critical Patterns

### Date/Time Handling

- **Always use UTC**: `dt_util.utcnow()` and `dt_util.UTC` from `homeassistant.util`
- **Midnight crossing**: If end time < start time, increment day (see `_to_domain()` in [pont_chaban.py](../custom_components/pont_chaban_delmas/pont_chaban.py#L183))
- Sensors use `SensorDeviceClass.TIMESTAMP` for native datetime values

### Async Context Management

Repository implements context manager protocol:

```python
async with repository:
    data = await repository.get_upcoming_closures()
```

Always close in `__aexit__` and coordinator's `async_shutdown()`

### Dual Setup Support

Integration supports both:

- **Config Entry** (modern): UI-based setup via config flow
- **YAML Platform** (legacy): `sensor.async_setup_platform()` for backward compatibility

## Development Workflow

### Essential Commands (Makefile)

```bash
make python-venv        # Setup venv + install dev deps
make python-test        # Run pytest
make python-test-coverage  # Coverage report (HTML in htmlcov/)
make python-lint        # Ruff linting
make python-format      # Auto-format with ruff
```

### Testing Strategy

- **Unit tests**: Mock repository, test domain logic ([tests/unit/](../tests/unit/))
- **API tests**: Test real API integration ([tests/api/](../tests/api/))
- Use `pytest-asyncio` for async test functions

### Version Management

- Version defined in both [pyproject.toml](../pyproject.toml) (`project.version`) and [manifest.json](../custom_components/pont_chaban_delmas/manifest.json) (`version`)
- **Keep synchronized** — use calendar versioning (e.g., `2025.12.0`)

## File-Specific Conventions

### manifest.json

- `requirements` must match `dependencies` in pyproject.toml (e.g., `aiohttp>=3.9.0`)
- Use `domain` value consistently: `pont_chaban_delmas`

### const.py

- Minimal file with just `DOMAIN`, `LOGGER`, `ATTRIBUTION`
- Never import from other integration modules (to avoid circular imports)

### coordinator.py

- Update interval: 15 minutes (`timedelta(minutes=15)`)
- `_async_update_data()` returns dict with keys: `closures`, `next_closure`, `last_update`
- Filter data to future only: `c.is_upcoming(now)`

### sensor.py

- Two sensors: `NextClosureSensor` (single upcoming) and `AllClosuresSensor` (list of up to 10)
- Use `CoordinatorEntity` base class for automatic updates
- Attributes contain rich data (boat name, duration, closure type)

## Common Pitfalls

1. **Don't use blocking I/O**: All network calls must be async (aiohttp)
2. **Logging**: Use `LOGGER` from [const.py](../custom_components/pont_chaban_delmas/const.py), not `logging.getLogger(__name__)`
3. **Type hints**: Required on all functions/methods — checked by ruff
4. **Coordinator cleanup**: Must call `await coordinator.async_shutdown()` in `async_unload_entry()`
5. **API errors**: Repository raises `aiohttp.ClientError` and `ValueError` — handle in coordinator with `UpdateFailed`
