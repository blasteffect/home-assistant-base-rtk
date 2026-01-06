from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOST, DEFAULT_SCAN_INTERVAL, DEFAULT_TIMEOUT, DOMAIN

_LOGGER = logging.getLogger(__name__)

class BaseRtkCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass, entry):
        self.entry = entry
        self.host = entry.data[CONF_HOST].strip()
        self.url = f"http://{self.host}/status"

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.host}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, timeout=DEFAULT_TIMEOUT) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"HTTP {resp.status}")
                    data = await resp.json(content_type=None)
                    if not isinstance(data, dict):
                        raise UpdateFailed("Invalid JSON payload (not an object)")
                    return data
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise UpdateFailed(f"Cannot connect to {self.url}: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
