"""OAuth2 token management for GoTo Connect Call Stats integration."""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

import requests
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from requests_oauthlib import OAuth2Session

# Allow HTTP for development (disable SSL verification warnings)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from .const import (
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_REFRESH_TOKEN,
    CONF_TOKEN_EXPIRES_AT,
    DOMAIN,
    OAUTH2_AUTHORIZE_URL,
    OAUTH2_SCOPE,
    OAUTH2_TOKEN_URL,
)

_LOGGER = logging.getLogger(__name__)


class GoToOAuth2Manager:
    """Manages OAuth2 tokens for GoTo Connect API."""

    def __init__(self, hass: HomeAssistant, config_entry: Optional[ConfigEntry] = None):
        """Initialize the OAuth2 manager."""
        self.hass = hass
        self.config_entry = config_entry

        # Handle both config entry and manual credential setting
        if config_entry is not None:
            self.client_id = config_entry.data[CONF_CLIENT_ID]
            self.client_secret = config_entry.data[CONF_CLIENT_SECRET]
        else:
            # For config flow setup, credentials will be set manually
            self.client_id = None
            self.client_secret = None
        
        # Initialize session with client_id (will be set later if None)
        self.session = OAuth2Session(
            self.client_id or "temp",  # Use temp placeholder if None
            redirect_uri="https://home-assistant.io/auth/callback",
            scope=OAUTH2_SCOPE,
        )
        self._tokens = {}

    def load_tokens(self) -> bool:
        """Load tokens from config entry."""
        try:
            if self.config_entry is None:
                _LOGGER.warning("No config entry available for token loading")
                return False

            _LOGGER.info(
                "Loading tokens from config entry. Config entry data: %s",
                self.config_entry.data,
            )

            tokens = self.config_entry.data.get("tokens", {})
            _LOGGER.info("Found tokens in config entry: %s", tokens)

            if not tokens:
                _LOGGER.warning("No tokens found in config entry")
                return False

            self._tokens = tokens
            _LOGGER.info("Tokens loaded into memory: %s", self._tokens)

            if not self._validate_tokens():
                _LOGGER.warning("Invalid or expired tokens found")
                return False

            _LOGGER.info("Tokens loaded successfully")
            return True

        except Exception as e:
            _LOGGER.error("Failed to load tokens: %s", e)
            return False

    def save_tokens(self) -> bool:
        """Save tokens to config entry."""
        try:
            if self.config_entry is None:
                _LOGGER.warning("No config entry available for token saving")
                return False

            # Update the config entry with new tokens
            data = dict(self.config_entry.data)
            data["tokens"] = self._tokens

            # Update the config entry
            self.hass.async_create_task(
                self._update_config_entry_async(data)
            )

            _LOGGER.info("Tokens saved successfully")
            return True

        except Exception as e:
            _LOGGER.error("Failed to save tokens: %s", e)
            return False

    async def _update_config_entry_async(self, data):
        """Update config entry asynchronously."""
        self.hass.config_entries.async_update_entry(self.config_entry, data=data)

    def _validate_tokens(self) -> bool:
        """Validate that tokens exist and are not expired."""
        try:
            if not self._tokens:
                _LOGGER.warning("No tokens to validate")
                return False

            access_token = self._tokens.get(CONF_ACCESS_TOKEN)
            if not access_token:
                _LOGGER.warning("No access token found")
                return False

            # Check if token is expired
            expires_at = self._tokens.get(CONF_TOKEN_EXPIRES_AT)
            if expires_at:
                current_time = datetime.now().timestamp()
                if current_time >= expires_at:
                    _LOGGER.info("Token is expired, attempting refresh")
                    return self.refresh_tokens()

            _LOGGER.info("Tokens are valid")
            return True

        except Exception as e:
            _LOGGER.error("Token validation failed: %s", e)
            return False

    def get_authorization_url(self) -> str:
        """Get the authorization URL for OAuth2 flow."""
        try:
            if not self.client_id:
                raise ValueError("Client ID not set")

            authorization_url, state = self.session.authorization_url(
                OAUTH2_AUTHORIZE_URL,
                access_type="offline",
                prompt="consent"
            )

            _LOGGER.info("Generated authorization URL")
            return authorization_url

        except Exception as e:
            _LOGGER.error("Failed to generate authorization URL: %s", e)
            raise

    def fetch_token(self, authorization_response: str) -> bool:
        """Fetch tokens using the authorization response."""
        try:
            _LOGGER.info("Fetching tokens from authorization response")

            # Extract the authorization code from the response
            if "code=" in authorization_response:
                code = authorization_response.split("code=")[1].split("&")[0]
            else:
                raise ValueError("No authorization code found in response")

            # Exchange authorization code for tokens
            token_data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': "https://home-assistant.io/auth/callback"
            }

            response = requests.post(OAUTH2_TOKEN_URL, data=token_data)
            response.raise_for_status()

            tokens = response.json()
            _LOGGER.info("Successfully fetched tokens")

            # Process and store tokens
            self._tokens = {
                CONF_ACCESS_TOKEN: tokens.get('access_token'),
                CONF_REFRESH_TOKEN: tokens.get('refresh_token'),
                CONF_TOKEN_EXPIRES_AT: datetime.now().timestamp() + tokens.get('expires_in', 3600)
            }

            # Save tokens to config entry
            self.save_tokens()

            return True

        except Exception as e:
            _LOGGER.error("Failed to fetch tokens: %s", e)
            return False

    def refresh_tokens(self) -> bool:
        """Refresh the access token using the refresh token."""
        try:
            refresh_token = self._tokens.get(CONF_REFRESH_TOKEN)
            if not refresh_token:
                _LOGGER.warning("No refresh token available")
                return False

            _LOGGER.info("Refreshing access token")

            token_data = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token
            }

            response = requests.post(OAUTH2_TOKEN_URL, data=token_data)
            response.raise_for_status()

            tokens = response.json()
            _LOGGER.info("Successfully refreshed tokens")

            # Update tokens
            self._tokens.update({
                CONF_ACCESS_TOKEN: tokens.get('access_token'),
                CONF_REFRESH_TOKEN: tokens.get('refresh_token', refresh_token),  # Keep old refresh token if new one not provided
                CONF_TOKEN_EXPIRES_AT: datetime.now().timestamp() + tokens.get('expires_in', 3600)
            })

            # Save updated tokens
            self.save_tokens()

            return True

        except Exception as e:
            _LOGGER.error("Failed to refresh tokens: %s", e)
            return False

    def get_valid_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary."""
        try:
            if not self._validate_tokens():
                _LOGGER.warning("No valid tokens available")
                return None

            return self._tokens.get(CONF_ACCESS_TOKEN)

        except Exception as e:
            _LOGGER.error("Failed to get valid token: %s", e)
            return None

    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        token = self.get_valid_token()
        if not token:
            raise ValueError("No valid access token available")

        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        } 