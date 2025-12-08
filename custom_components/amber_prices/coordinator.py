import asyncio
import logging
import aiohttp
import traceback
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, API_BASE, HEADERS, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class AmberCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, postcode, scan_interval=DEFAULT_SCAN_INTERVAL):
        self.postcode = postcode
        self.api_url = f"{API_BASE}/postcode/{postcode}/prices?past-hours=1"
        _LOGGER.info("AmberCoordinator initialized with scan_interval=%s seconds for postcode=%s", scan_interval, postcode)
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
        try:
            await coordinator.async_config_entry_first_refresh()
        except Exception:  # don't fail setup permanently on transient network errors
            _LOGGER.warning(
                "Initial data fetch failed for postcode %s — integration will still be set up and retry: %s",
                postcode,
                traceback.format_exc(),
            )
        return coordinator

    async def _async_update_data(self):
        try:
            session = async_get_clientsession(self.hass)
            try:
                async with session.get(self.api_url, headers=HEADERS, timeout=10) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        _LOGGER.error(
                            "Amber API error: HTTP %s, Postcode: %s, URL: %s, Response: %s",
                            resp.status,
                            self.postcode,
                            self.api_url,
                            text,
                        )
                        raise UpdateFailed(f"HTTP {resp.status}")
                    data = await resp.json()
            except asyncio.TimeoutError:
                _LOGGER.warning("Timeout fetching Amber data for postcode %s", self.postcode)
                raise UpdateFailed("Timeout")
            except aiohttp.ClientError as err:
                _LOGGER.warning("Network error fetching Amber data for postcode %s: %s", self.postcode, err)
                raise UpdateFailed(err)

            # Flatten the latest interval for sensors
            result = {}
            try:
                if data.get("priceData") and data["priceData"][0]["intervals"]:
                    latest_price = data["priceData"][0]["intervals"][-1]
                    result["price_now"] = latest_price.get("perKwh")
                    result["renewables_now"] = latest_price.get("renewables")
                    result["nem_time"] = latest_price.get("nemTime")
                    result["descriptor"] = latest_price.get("descriptor")
                if data.get("feedInPriceData") and data["feedInPriceData"][0]["intervals"]:
                    latest_feed_in = data["feedInPriceData"][0]["intervals"][-1]
                    result["feed_in_now"] = latest_feed_in.get("perKwh")
            except Exception as e:
                _LOGGER.error("Error flattening Amber API data: %s", e, exc_info=True)
            return result
        except UpdateFailed:
            # Already logged above — re-raise to let the coordinator handle backoff
            raise
        except Exception as err:
            _LOGGER.error("Unexpected exception fetching Amber data: %s", err, exc_info=True)
            raise UpdateFailed(f"Error fetching Amber data: {err}")
