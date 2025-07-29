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

from .const import DOMAIN, OAUTH2_SCOPE
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
        """Handle the OAuth2 authorization step."""
        _LOGGER.info("Entering OAuth step, user_input: %s", user_input is not None)
        if user_input is not None:
            # Handle the OAuth2 callback
            try:
                authorization_response = user_input.get("authorization_response")
                if not authorization_response:
                    raise HomeAssistantError("No authorization response received")

                success = await self.hass.async_add_executor_job(
                    self.oauth_manager.fetch_token, authorization_response
                )

                if success:
                    # Create the config entry with tokens
                    config_data = {
                        CONF_CLIENT_ID: self.client_id,
                        CONF_CLIENT_SECRET: self.client_secret,
                        "tokens": self.oauth_manager._tokens,  # Include the tokens
                    }

                    return self.async_create_entry(
                        title="GoTo Connect Call Stats",
                        data=config_data,
                    )
                else:
                    return self.async_show_form(
                        step_id="oauth",
                        errors={"base": "oauth_failed"},
                    )

            except Exception as e:
                _LOGGER.error("OAuth2 flow failed: %s", e)
                return self.async_show_form(
                    step_id="oauth",
                    errors={"base": "oauth_failed"},
                )

        # Get the authorization URL
        try:
            _LOGGER.info("About to generate authorization URL")
            auth_url = self.oauth_manager.get_authorization_url()
            _LOGGER.info("Generated authorization URL: %s", auth_url)
        except Exception as e:
            _LOGGER.error("Failed to generate authorization URL: %s", e)
            # Create a fallback URL manually
            auth_url = (
                f"https://authentication.logmeininc.com/oauth/authorize"
                f"?client_id={self.client_id}"
                f"&redirect_uri=https://home-assistant.io/auth/callback"
                f"&response_type=code&scope={OAUTH2_SCOPE}"
            )
            _LOGGER.info("Using fallback authorization URL: %s", auth_url)

        _LOGGER.info("Showing OAuth form with auth_url: %s", auth_url)
        # Create a simpler form that shows the URL directly
        description = f"""
Please authorize the application by visiting this URL:

**{auth_url}**

After authorization, you'll be redirected to a URL like:
`https://home-assistant.io/auth/callback?code=AUTHORIZATION_CODE`

Copy the entire URL and paste it below.

**Note:** If you only see an authorization code (without the full URL), you can paste just the code.
        """

        return self.async_show_form(
            step_id="oauth",
            description_placeholders={
                "auth_url": auth_url,
                "client_id": self.client_id,
            },
            data_schema=vol.Schema(
                {
                    vol.Required("authorization_response"): str,
                }
            ),
        )




class InvalidCredentials(HomeAssistantError):
    """Error to indicate invalid credentials."""


class OAuth2Error(HomeAssistantError):
    """Error to indicate OAuth2 flow failed.""" 