from datetime import timedelta
import aiohttp, asyncio, logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DEFAULT_SCAN_INTERVAL, DEFAULT_TIMEOUT, DOMAIN

class BaseRtkCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.host = entry.data["host"]
        self.url = f"http://{self.host}/status"
        super().__init__(hass, logging.getLogger(__name__), name=DOMAIN,
                         update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL))

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, timeout=DEFAULT_TIMEOUT) as r:
                    if r.status != 200:
                        raise UpdateFailed(r.status)
                    return await r.json()
        except Exception as e:
            raise UpdateFailed(e)
