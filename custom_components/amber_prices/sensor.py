# shortened version
from __future__ import annotations
from dataclasses import dataclass
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .coordinator import AmberCoordinator
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required("postcode"): cv.string,
    vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    postcode = config["postcode"]
    scan_interval = config["scan_interval"]
    coordinator = await AmberCoordinator.create(hass, postcode, scan_interval)
    async_add_entities([AmberSensor(coordinator, desc) for desc in SENSORS])

@dataclass
class AmberDesc(SensorEntityDescription):
    key_in_data: str | None = None
    unit: str | None = None
    icon_override: str | None = None

SENSORS = [
    AmberDesc(key="price_now", name="Amber Price Now", key_in_data="price_now", unit="c/kWh", icon_override="mdi:flash"),
    AmberDesc(key="feed_in_now", name="Amber Feed-In Now", key_in_data="feed_in_now", unit="c/kWh", icon_override="mdi:transmission-tower-export"),
    AmberDesc(key="renewables_now", name="Amber Renewables Now", key_in_data="renewables_now", unit="%", icon_override="mdi:leaf"),
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: AmberCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AmberSensor(coordinator, desc) for desc in SENSORS])


class AmberSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: AmberCoordinator, desc: AmberDesc):
        super().__init__(coordinator)
        self.entity_description = desc
        self._attr_unique_id = f"{coordinator.postcode}_{desc.key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, coordinator.postcode)}, name=f"Amber ({coordinator.postcode})", manufacturer="Amber")
        self._attr_native_unit_of_measurement = desc.unit
        self._attr_icon = desc.icon_override

    @property
    def native_value(self):
        return self.coordinator.data.get(self.entity_description.key_in_data)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        return {"nem_time": data.get("nem_time"), "descriptor": data.get("descriptor")}
