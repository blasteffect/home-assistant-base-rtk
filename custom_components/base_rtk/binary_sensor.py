from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_NAME

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BaseRtkOnlineBinarySensor(coordinator, entry)])

class BaseRtkOnlineBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_online"
        self._attr_name = "En ligne"
        self._attr_device_class = "connectivity"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{DEFAULT_NAME} ({coordinator.host})",
            "manufacturer": "DIY",
            "model": "ESP32 RTK Base",
        }

    @property
    def is_on(self) -> bool:
        # True si la dernière requête HTTP a réussi
        return bool(self.coordinator.last_update_success)
