"""The Seatsurfing integration."""

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant

from .api import SeatsurfingApi
from .types import SeatsurfingConfigEntry

# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: SeatsurfingConfigEntry) -> bool:
    """Set up Seatsurfing from a config entry."""

    entry.runtime_data = SeatsurfingApi(
        entry.data[CONF_HOST], entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
    )

    # component = ExampleSensor()
    # await component.async_add_entities()

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: SeatsurfingConfigEntry
) -> bool:
    """Unload a config entry."""
    # return True
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
