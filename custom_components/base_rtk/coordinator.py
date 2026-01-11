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
        self.base_url = f"http://{self.host}"

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.host}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _fetch_json(self, session: aiohttp.ClientSession, path: str) -> dict:
        url = f"{self.base_url}{path}"
        async with session.get(url, timeout=DEFAULT_TIMEOUT) as resp:
            if resp.status != 200:
                raise UpdateFailed(f"HTTP {resp.status} on {path}")
            data = await resp.json(content_type=None)
            if not isinstance(data, dict):
                raise UpdateFailed(f"Invalid JSON payload on {path} (not an object)")
            return data

    async def _async_update_data(self) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                base_data = await self._fetch_json(session, "/status")

                # Robot: si tu veux tolérer l'absence de /robot/status au début,
                # on ne fait pas échouer tout l'update : on met {}.
                try:
                    robot_data = await self._fetch_json(session, "/robot/status")
                except Exception as err:
                    _LOGGER.debug("Robot status unavailable: %s", err)
                    robot_data = {}

                return {"base": base_data, "robot": robot_data}

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise UpdateFailed(f"Cannot connect to {self.base_url}: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
