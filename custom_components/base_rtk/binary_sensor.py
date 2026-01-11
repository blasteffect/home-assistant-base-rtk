from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_NAME

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        BaseRtkOnlineBinarySensor(coordinator, entry),
        RobotOnlineBinarySensor(coordinator, entry),
        RobotChargingBinarySensor(coordinator, entry),
        RobotDockedBinarySensor(coordinator, entry),
    ])

class _BaseInfoMixin:
    def _device_info(self, coordinator, entry):
        return {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{DEFAULT_NAME} ({coordinator.host})",
            "manufacturer": "DIY",
            "model": "ESP32 RTK Base",
        }

class BaseRtkOnlineBinarySensor(CoordinatorEntity, BinarySensorEntity, _BaseInfoMixin):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_online"
        self._attr_name = "En ligne"
        self._attr_device_class = "connectivity"
        self._attr_device_info = self._device_info(coordinator, entry)

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.last_update_success)

class RobotOnlineBinarySensor(CoordinatorEntity, BinarySensorEntity, _BaseInfoMixin):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_robot_online"
        self._attr_name = "Robot en ligne"
        self._attr_device_class = "connectivity"
        self._attr_device_info = self._device_info(coordinator, entry)

    @property
    def is_on(self):
        if not self.coordinator.last_update_success:
            return None
        robot = (self.coordinator.data or {}).get("robot") or {}
        val = robot.get("online")
        return None if val is None else bool(val)

class RobotChargingBinarySensor(CoordinatorEntity, BinarySensorEntity, _BaseInfoMixin):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_robot_charging"
        self._attr_name = "Robot en charge"
        self._attr_device_info = self._device_info(coordinator, entry)

    @property
    def is_on(self):
        if not self.coordinator.last_update_success:
            return None
        robot = (self.coordinator.data or {}).get("robot") or {}
        val = robot.get("charging")
        if val is None:
            return None
        return bool(int(val)) if isinstance(val, (int, float, str)) else bool(val)

class RobotDockedBinarySensor(CoordinatorEntity, BinarySensorEntity, _BaseInfoMixin):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_robot_docked"
        self._attr_name = "Robot au dock"
        self._attr_device_info = self._device_info(coordinator, entry)

    @property
    def is_on(self):
        if not self.coordinator.last_update_success:
            return None
        robot = (self.coordinator.data or {}).get("robot") or {}
        val = robot.get("docked")
        if val is None:
            return None
        return bool(int(val)) if isinstance(val, (int, float, str)) else bool(val)
