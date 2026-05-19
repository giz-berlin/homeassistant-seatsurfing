from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry

@dataclass
class SeatsurfingData:
    """Data for AccuWeather integration."""

    host: str
    username: str
    password: str


# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations
type SeatsurfingConfigEntry = ConfigEntry[SeatsurfingData]
