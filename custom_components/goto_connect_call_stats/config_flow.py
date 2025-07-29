"""Config flow for GoTo Connect Call Stats integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .oauth import GoToOAuth2Manager

_LOGGER = logging.getLogger(__name__)


class GoToConnectCallStatsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GoTo Connect Call Stats."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.client_id: Optional[str] = None
        self.client_secret: Optional[str] = None
        self.oauth_manager: Optional[GoToOAuth2Manager] = None

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self.client_id = user_input[CONF_CLIENT_ID]
            self.client_secret = user_input[CONF_CLIENT_SECRET]

            try:
                # Initialize OAuth manager
                self.oauth_manager = GoToOAuth2Manager(self.hass)
                self.oauth_manager.client_id = self.client_id
                self.oauth_manager.client_secret = self.client_secret

                # Generate authorization URL
                auth_url = self.oauth_manager.get_authorization_url()

                # Store the OAuth manager for the next step
                self.hass.data.setdefault(DOMAIN, {})
                self.hass.data[DOMAIN]["temp_oauth_manager"] = self.oauth_manager

                return await self.async_step_oauth()

            except Exception as ex:
                _LOGGER.error("Failed to initialize OAuth: %s", ex)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CLIENT_ID): str,
                    vol.Required(CONF_CLIENT_SECRET): str,
                }
            ),
            errors=errors,
        )

    async def async_step_oauth(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the OAuth step."""
        errors = {}

        if user_input is not None:
            authorization_response = user_input.get("authorization_response")

            try:
                # Get the OAuth manager from temporary storage
                oauth_manager = self.hass.data[DOMAIN].get("temp_oauth_manager")
                if not oauth_manager:
                    raise ValueError("OAuth manager not found")

                # Fetch tokens using the authorization response
                if oauth_manager.fetch_token(authorization_response):
                    # Create the config entry
                    return self.async_create_entry(
                        title="GoTo Connect Call Stats",
                        data={
                            CONF_CLIENT_ID: self.client_id,
                            CONF_CLIENT_SECRET: self.client_secret,
                            "tokens": oauth_manager._tokens,
                        },
                    )
                else:
                    errors["base"] = "invalid_auth"

            except Exception as ex:
                _LOGGER.error("Failed to complete OAuth flow: %s", ex)
                errors["base"] = "invalid_auth"

        # Generate authorization URL
        oauth_manager = self.hass.data[DOMAIN].get("temp_oauth_manager")
        if oauth_manager:
            auth_url = oauth_manager.get_authorization_url()
        else:
            auth_url = "https://authentication.logmeininc.com/oauth/authorize"

        return self.async_show_form(
            step_id="oauth",
            data_schema=vol.Schema(
                {
                    vol.Required("authorization_response"): str,
                }
            ),
            description_placeholders={
                "auth_url": auth_url,
            },
            errors=errors,
        )

    async def async_step_import(self, import_info: Dict[str, Any]) -> FlowResult:
        """Handle import from configuration."""
        return await self.async_step_user(import_info)


class InvalidCredentials(HomeAssistantError):
    """Error to indicate invalid credentials."""


class OAuth2Error(HomeAssistantError):
    """Error to indicate OAuth2 flow failed.""" 