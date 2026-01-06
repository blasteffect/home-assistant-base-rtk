from dataclasses import dataclass
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, DEFAULT_NAME

@dataclass(frozen=True)
class Desc(SensorEntityDescription):
    json_key: str

SENSORS = (
    Desc(key="rtcm", name="RTCM sent", json_key="rtcmSent"),
    Desc(key="crc", name="CRC errors", json_key="crcErrors"),
    Desc(key="heap", name="Heap", json_key="heap"),
    Desc(key="boot", name="Boot time", json_key="bootTime"),
    Desc(key="reset", name="Reset reason", json_key="resetReason"),
)

async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BaseRtkSensor(coord, entry, d) for d in SENSORS])

class BaseRtkSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, desc):
        super().__init__(coordinator)
        self.entity_description = desc
        self._attr_unique_id = f"{entry.entry_id}_{desc.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": DEFAULT_NAME,
            "manufacturer": "DIY",
            "model": "ESP32 RTK Base",
        }

    @property
    def native_value(self):
        if not self.coordinator.last_update_success:
            return None
        return self.coordinator.data.get(self.entity_description.json_key)
