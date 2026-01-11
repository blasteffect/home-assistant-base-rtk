from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_NAME

@dataclass(frozen=True, kw_only=True)
class BaseRtkSensorDescription(SensorEntityDescription):
    json_key: str

SENSORS_BASE: tuple[BaseRtkSensorDescription, ...] = (
    BaseRtkSensorDescription(key="rtcm", name="RTCM sent", json_key="rtcmSent", native_unit_of_measurement="paquets"),
    BaseRtkSensorDescription(key="crc", name="CRC errors", json_key="crcErrors", native_unit_of_measurement="erreurs"),
    BaseRtkSensorDescription(key="heap", name="Heap", json_key="heap", native_unit_of_measurement="o"),
    BaseRtkSensorDescription(key="boot", name="Boot time", json_key="bootTime"),
    BaseRtkSensorDescription(key="reset", name="Reset reason", json_key="resetReason"),
)

SENSORS_ROBOT: tuple[BaseRtkSensorDescription, ...] = (
    BaseRtkSensorDescription(key="robot_battery", name="Robot battery", json_key="batteryPercent", native_unit_of_measurement="%"),
    BaseRtkSensorDescription(key="robot_mode", name="Robot mode", json_key="mode"),
    BaseRtkSensorDescription(key="robot_fix", name="Robot GNSS fix", json_key="fix"),
    BaseRtkSensorDescription(key="robot_lat", name="Robot latitude", json_key="lat"),
    BaseRtkSensorDescription(key="robot_lon", name="Robot longitude", json_key="lon"),
    BaseRtkSensorDescription(key="robot_sats", name="Robot satellites", json_key="sats", native_unit_of_measurement="sat"),
    BaseRtkSensorDescription(key="robot_last_seen", name="Robot last seen", json_key="lastSeenSec", native_unit_of_measurement="s"),
)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []
    entities += [BaseRtkSensor(coordinator, entry, desc) for desc in SENSORS_BASE]
    entities += [BaseRtkRobotSensor(coordinator, entry, desc) for desc in SENSORS_ROBOT]

    async_add_entities(entities)

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
        if not self.coordinator.last_update_success:
            return None
        base = (self.coordinator.data or {}).get("base") or {}
        return base.get(self.entity_description.json_key)

class BaseRtkRobotSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

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
        if not self.coordinator.last_update_success:
            return None
        robot = (self.coordinator.data or {}).get("robot") or {}
        # si /robot/status pas encore dispo => unknown
        return robot.get(self.entity_description.json_key)
