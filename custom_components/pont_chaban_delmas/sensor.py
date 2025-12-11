"""Sensor for upcoming Pont Chaban-Delmas bridge closures."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import ATTRIBUTION, DOMAIN, LOGGER
from .coordinator import PontChabanCoordinator
from .domain import BridgeClosure


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Pont Chaban sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        PontChabanNextClosureSensor(coordinator),
        PontChabanAllClosuresSensor(coordinator),
    ]

    async_add_entities(sensors)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Pont Chaban-Delmas sensor platform (legacy YAML)."""
    LOGGER.info("Setting up Pont Chaban-Delmas sensor platform via YAML")
    coordinator = PontChabanCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    sensors = [
        PontChabanNextClosureSensor(coordinator),
        PontChabanAllClosuresSensor(coordinator),
    ]

    async_add_entities(sensors)


class PontChabanNextClosureSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing the next bridge closure.

    Displays the timestamp of the next bridge closure as the native value,
    with detailed attributes including boat info, duration, and closure type.
    """

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:bridge"
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: PontChabanCoordinator) -> None:
        """Initialize the sensor.

        Parameters:
            coordinator: The data update coordinator.
        """
        super().__init__(coordinator)
        self._attr_name = "Next Closure"
        self._attr_unique_id = f"{DOMAIN}_next_closure"

    @property
    def native_value(self) -> datetime | None:
        """Return the start time of the next closure.

        Returns:
            Datetime of next closure start, or None if no closure scheduled.
        """
        if self.coordinator.data and self.coordinator.data.get("next_closure"):
            closure: BridgeClosure = self.coordinator.data["next_closure"]
            return closure.start_utc
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes with next closure details.

        Returns:
            Dictionary with closure timing, boat, duration, and closure type.
        """
        if not self.coordinator.data or not self.coordinator.data.get("next_closure"):
            return {}

        closure: BridgeClosure = self.coordinator.data["next_closure"]
        now = dt_util.utcnow()

        return {
            "start": closure.start_utc.isoformat(),
            "end": closure.end_utc.isoformat(),
            "boat": closure.boat,
            "duration_minutes": int(closure.duration().total_seconds() / 60),
            "type": closure.closure_type,
            "is_total": closure.is_total,
            "is_active": closure.is_active(now),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class PontChabanAllClosuresSensor(CoordinatorEntity, SensorEntity):
    """Sensor listing all upcoming bridge closures.

    Displays the timestamp of the next closure as the native value,
    with a list of up to 10 upcoming closures in attributes.
    """

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:bridge"
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: PontChabanCoordinator) -> None:
        """Initialize the sensor.

        Parameters:
            coordinator: The data update coordinator.
        """
        super().__init__(coordinator)
        self._attr_name = "Upcoming Closures"
        self._attr_unique_id = f"{DOMAIN}_upcoming_closures"

    @property
    def native_value(self) -> datetime | None:
        """Return the start time of the next closure.

        Returns:
            Datetime of next closure start, or None if no closures scheduled.
        """
        if self.coordinator.data and self.coordinator.data.get("closures"):
            closures: list[BridgeClosure] = self.coordinator.data["closures"]
            if closures:
                return closures[0].start_utc
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes with all upcoming closures.

        Returns:
            Dictionary with total count and list of upcoming closures (up to 10).
        """
        if not self.coordinator.data or not self.coordinator.data.get("closures"):
            return {"closures": [], "count": 0}

        closures: list[BridgeClosure] = self.coordinator.data["closures"]
        limited_closures = closures[:10]  # Limit to 10 for attributes

        return {
            "count": len(closures),
            "closures": [
                {
                    "start": c.start_utc.isoformat(),
                    "end": c.end_utc.isoformat(),
                    "boat": c.boat,
                    "duration_minutes": int(c.duration().total_seconds() / 60),
                    "type": c.closure_type,
                    "is_total": c.is_total,
                }
                for c in limited_closures
            ],
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
