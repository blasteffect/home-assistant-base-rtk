from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_NAME

@dataclass(frozen=True, kw_only=True)
class BaseRtkSensorDescription(SensorEntityDescription):
    json_key: str
    unit: str | None = None

SENSORS: tuple[BaseRtkSensorDescription, ...] = (
    BaseRtkSensorDescription(key="rtcm", name="RTCM sent", json_key="rtcmSent", native_unit_of_measurement="paquets"),
    BaseRtkSensorDescription(key="crc", name="CRC errors", json_key="crcErrors", native_unit_of_measurement="erreurs"),
    BaseRtkSensorDescription(key="heap", name="Heap", json_key="heap", native_unit_of_measurement="o"),
    BaseRtkSensorDescription(key="boot", name="Boot time", json_key="bootTime"),
    BaseRtkSensorDescription(key="reset", name="Reset reason", json_key="resetReason"),
)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BaseRtkSensor(coordinator, entry, desc) for desc in SENSORS])

class BaseRtkSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, desc: BaseRtkSensorDescription):
        super().__init__(coordinator)
        self.entity_description = desc
        self._attr_unique_id = f"{entry.entry_id}_{desc.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{DEFAULT_NAME} ({coordinator.host})",
            "manufacturer": "DIY",
            "model": "ESP32 RTK Base",
        }

    @property
    def native_value(self):
        # If the coordinator cannot update, HA will show "unavailable"
        if not self.coordinator.last_update_success:
            return None
        return self.coordinator.data.get(self.entity_description.json_key)
