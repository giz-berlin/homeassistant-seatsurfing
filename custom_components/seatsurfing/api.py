import datetime
import urllib.parse

from aiohttp import BasicAuth
import aiohttp

from homeassistant.exceptions import HomeAssistantError


class SeatsurfingApi:
    """Seatsurfing API wrapper."""

    def __init__(self, host: str, username: str, password: str) -> None:
        """Initialize."""
        self.host = host
        self.username = username
        self.password = password

    async def test_authenticate(self):
        """Test if we can authenticate with the host."""
        await self.get_locations()

    async def get_remote(self, url):
        basic = BasicAuth(self.username, self.password)
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(url, auth=basic) as resp,
            ):
                if resp.status > 400 and resp.status < 500:
                    raise InvalidAuth
                return await resp.json()
        except aiohttp.ClientResponseError as exc:
            raise InvalidRequest from exc
        except aiohttp.ClientError as exc:
            raise CannotConnect from exc

    async def get_locations(self):
        return await self.get_remote(f"{self.host}/location/")

    async def get_spaces_for_location(self, location_id: str):
        if "/" in location_id:
            raise ValueError("Invalid {location_id}")
        return await self.get_remote(f"{self.host}/location/{location_id}/space/")

    async def get_space_availability(self, location_id: str, space_id: str):
        if "/" in location_id:
            raise ValueError("Invalid {location_id}")
        if "/" in space_id:
            raise ValueError("Invalid {space_id}")
        # Fix time zone issues, see https://github.com/seatsurfing/seatsurfing/issues/1622
        one_day_ago = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=24)
        one_day_ago_param = urllib.parse.quote_plus(one_day_ago.isoformat())
        one_day_future = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
        one_day_future_param = urllib.parse.quote_plus(one_day_future.isoformat())
        data = await self.get_remote(
            f"{self.host}/location/{location_id}/space/{space_id}/availability?enter={one_day_ago_param}&leave={one_day_future_param}"
        )
        return data[0]


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class InvalidRequest(HomeAssistantError):
    """Error to indicate there is an invalid request."""
