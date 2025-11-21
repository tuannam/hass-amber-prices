from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN, PLATFORMS
from .coordinator import AmberCoordinator

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    from .const import CONF_POSTCODE, DEFAULT_SCAN_INTERVAL
    postcode = entry.data[CONF_POSTCODE]
    # Prefer options, then data, then default
    scan_interval = (
        entry.options.get("scan_interval")
        if hasattr(entry, "options") and "scan_interval" in entry.options
        else entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    )
    import logging
    _LOGGER = logging.getLogger(__name__)
    _LOGGER.info("Config entry data: %s", entry.data)
    _LOGGER.info("Config entry options: %s", entry.options)
    _LOGGER.info("Using scan_interval=%s for postcode=%s", scan_interval, postcode)
    coordinator = await AmberCoordinator.create(hass, postcode, scan_interval)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
