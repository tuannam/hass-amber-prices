import asyncio
import logging
import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, API_BASE, HEADERS, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class AmberCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, postcode, scan_interval=DEFAULT_SCAN_INTERVAL):
        self.postcode = postcode
        self.api_url = f"{API_BASE}/postcode/{postcode}/prices?past-hours=1"
        super().__init__(
            hass,
            _LOGGER,
            name=f"Amber Prices {postcode}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.data = {}

    @classmethod
    async def create(cls, hass, postcode, scan_interval=DEFAULT_SCAN_INTERVAL):
        coordinator = cls(hass, postcode, scan_interval)
        await coordinator.async_config_entry_first_refresh()
        return coordinator

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, headers=HEADERS) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"HTTP {resp.status}")
                    data = await resp.json()
                    return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching Amber data: {err}")
