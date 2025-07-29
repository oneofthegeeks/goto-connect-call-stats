"""Constants for the GoTo Connect Call Stats integration."""

DOMAIN = "goto_connect_call_stats"
DEFAULT_NAME = "GoTo Connect Call Stats"

# OAuth2 Configuration (reused from ha-goto)
OAUTH2_AUTHORIZE_URL = "https://authentication.logmeininc.com/oauth/authorize"
OAUTH2_TOKEN_URL = "https://authentication.logmeininc.com/oauth/token"
OAUTH2_SCOPE = "call-events.v1.events.read users.v1.read presence.v1.read"

# GoTo Connect API Endpoints
GOTO_API_BASE_URL = "https://api.goto.com"
CALLS_API_URL = "/rest/calls/v1/calls"
USERS_API_URL = "/rest/users/v1/users/me"
ACCOUNTS_API_URL = "/rest/accounts/v1/accounts"

# Configuration keys
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_ACCESS_TOKEN = "access_token"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_TOKEN_EXPIRES_AT = "token_expires_at"

# Sensor names
SENSOR_TOTAL_CALLS = "total_calls"
SENSOR_INCOMING_CALLS = "incoming_calls"
SENSOR_OUTGOING_CALLS = "outgoing_calls"
SENSOR_MISSED_CALLS = "missed_calls"
SENSOR_CALL_DURATION = "call_duration"
SENSOR_AVERAGE_CALL_DURATION = "average_call_duration"
SENSOR_TODAY_CALLS = "today_calls"
SENSOR_WEEK_CALLS = "week_calls"
SENSOR_MONTH_CALLS = "month_calls"

# Update interval (5 minutes)
UPDATE_INTERVAL = 300

# Platforms
PLATFORMS = ["sensor"] 