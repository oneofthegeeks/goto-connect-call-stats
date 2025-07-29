# Quick Installation Guide

## Prerequisites

1. **Home Assistant**: Version 2023.8.0 or higher
2. **GoTo Connect Developer Account**: You need API credentials
3. **HACS** (optional but recommended): For easy installation

## Installation Steps

### Step 1: Get GoTo Connect API Credentials

1. Go to [GoTo Connect Developer Portal](https://developer.goto.com/)
2. Create a new application or use an existing one
3. Note your **Client ID** and **Client Secret**
4. Set the redirect URI to: `https://home-assistant.io/auth/callback`
5. Ensure your application has these scopes:
   - `call-events.v1.events.read`
   - `users.v1.read`
   - `presence.v1.read`

### Step 2: Install the Integration

#### Option A: HACS Installation (Recommended)

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. In HACS, go to **Integrations**
3. Click the **+** button in the bottom right
4. Search for this repository URL and add it
5. Find "GoTo Connect Call Stats" in the HACS store
6. Click **Download**
7. Restart Home Assistant

#### Option B: Manual Installation

1. Download the `custom_components/goto_connect_call_stats` folder
2. Copy it to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

### Step 3: Configure the Integration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "GoTo Connect Call Stats"
4. Enter your Client ID and Client Secret
5. Complete the OAuth authentication process:
   - Click the authorization URL
   - Log in to your GoTo Connect account
   - Authorize the application
   - Copy the callback URL and paste it back
6. The integration will be added and sensors will appear

### Step 4: Verify Installation

1. Check that sensors appear in **Settings** → **Devices & Services**
2. Look for sensors like:
   - `sensor.total_calls_today`
   - `sensor.incoming_calls_today`
   - `sensor.outgoing_calls_today`
   - `sensor.missed_calls_today`
   - `sensor.total_call_duration_today`
   - `sensor.average_call_duration_today`

## Troubleshooting

### Common Issues

1. **"Failed to connect" error**
   - Verify your Client ID and Client Secret are correct
   - Check your internet connection
   - Ensure your GoTo Connect application is properly configured

2. **"Invalid authentication" error**
   - Double-check your credentials
   - Make sure the redirect URI matches exactly
   - Verify your application has the required scopes

3. **No sensors appear**
   - Restart Home Assistant after installation
   - Check the integration status in **Devices & Services**
   - Look for any error messages in the logs

4. **Sensors show "unavailable"**
   - The integration updates every 5 minutes
   - Check if you have recent call activity in GoTo Connect
   - Try restarting the integration

### Debug Logging

To enable debug logging, add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.goto_connect_call_stats: debug
```

## Next Steps

1. **Create a Dashboard**: Use the example in `dashboard_example.yaml`
2. **Set up Automations**: Create automations based on call statistics
3. **Monitor Usage**: Check the integration status regularly

## Support

- 📖 **Documentation**: See the main [README.md](README.md)
- 🐛 **Issues**: Open an issue on GitHub
- 💬 **Questions**: Start a discussion for help 