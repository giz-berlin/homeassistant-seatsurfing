"""Platform for sensor integration."""

import datetime
import urllib

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import SeatsurfingApi
from .const import DOMAIN
from .types import SeatsurfingConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SeatsurfingConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Setup sensor platform for the ui."""

    api: SeatsurfingApi = entry.runtime_data

    entities = []

    for location in await api.get_locations():
        for space in await api.get_spaces_for_location(location["id"]):
            entities.append(
                SeatsurfingOccupancySensor(entry.runtime_data, location, space)
            )

    async_add_entities(
        entities,
        True,
    )


class SeatsurfingOccupancySensor(BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY
    _attr_icon = "mdi:"

    def __init__(self, api: SeatsurfingApi, location, space) -> None:
        super().__init__()
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{api.host}")},
            name=urllib.parse.urlparse(api.host).netloc,
            entry_type=DeviceEntryType.SERVICE,
        )
        self._attr_name = f"{location['name']}: {space['name']}"
        self._const_value = False
        self._location_id = location["id"]
        self._location_name = location["name"]
        self._space_id = space["id"]
        self._space_name = space["name"]
        self._attr_unique_id = (
            f"{DOMAIN}_{api.host}_{self._location_id}_{self._space_id}"
        )
        self._api = api

        self._current_user = None
        self._current_booking_end = None
        self._current_subject = None
        self._next_booking_start_date = None
        self._next_user = None
        self._next_subject = None

    @property
    def should_poll(self) -> bool:
        return True

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        availability = await self._api.get_space_availability(
            self._location_id, self._space_id
        )
        currently_booked = False
        current_user = None
        current_booking_end = None
        current_subject = None
        next_booking_start_date = None
        next_user = None
        next_subject = None
        now = datetime.datetime.now(datetime.UTC)
        for booking in availability["bookings"]:
            start_date = datetime.datetime.fromisoformat(booking["enter"])
            end_date = datetime.datetime.fromisoformat(booking["leave"])
            if start_date <= now <= end_date:
                currently_booked = True
                current_user = booking["userEmail"]
                current_subject = booking["subject"]
                current_booking_end = end_date
            if start_date > now and (
                not next_booking_start_date or start_date < next_booking_start_date
            ):
                next_booking_start_date = start_date
                next_user = booking["userEmail"]
                next_subject = booking["subject"]

        self._current_user = current_user
        self._current_booking_end = current_booking_end
        self._current_subject = current_subject
        self._next_booking_start_date = next_booking_start_date
        self._next_user = next_user
        self._next_subject = next_subject

        self._attr_is_on = currently_booked

    @property
    def state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes.

        Implemented by component base class, should not be extended by integrations.
        Convention for attribute names is lowercase snake_case.
        """
        attributes = {
            'location_name': self._location_name,
            'space_name': self._space_name,
        }
        if self._current_user:
            attributes["current_user"] = self._current_user
        if self._current_subject:
            attributes["current_subject"] = self._current_subject
        if self._current_booking_end:
            attributes["current_booking_end"] = self._current_booking_end.isoformat()
        if self._next_booking_start_date:
            attributes["next_booking_start_date"] = (
                self._next_booking_start_date.isoformat()
            )
        if self._next_user:
            attributes["next_user"] = self._next_user
        if self._next_subject:
            attributes["next_subject"] = self._next_subject
        return attributes

    @property
    def icon(self) -> str | None:
        if self.is_on:
            return "mdi:account-circle"
        return "mdi:account-circle-outline"
