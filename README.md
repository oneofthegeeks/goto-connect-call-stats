# GoTo Connect Call Stats

A Home Assistant integration that provides call statistics from GoTo Connect. This integration displays various call metrics including total calls, incoming/outgoing calls, missed calls, call duration, and more.

## Features

- **Real-time Call Statistics**: Get up-to-date call statistics from your GoTo Connect account
- **Multiple Time Periods**: View statistics for today, this week, and this month
- **Detailed Metrics**: Track incoming, outgoing, and missed calls
- **Call Duration Analysis**: Monitor total and average call durations
- **OAuth2 Authentication**: Secure authentication using GoTo Connect's OAuth2 flow
- **Automatic Updates**: Data refreshes every 5 minutes

## Sensors

The integration provides the following sensors:

- **Total Calls Today**: Number of total calls made today
- **Incoming Calls Today**: Number of incoming calls received today
- **Outgoing Calls Today**: Number of outgoing calls made today
- **Missed Calls Today**: Number of missed calls today
- **Total Call Duration Today**: Total duration of all calls today (in seconds)
- **Average Call Duration Today**: Average duration of calls today (in seconds)
- **Today's Call Statistics**: Summary of today's call activity
- **This Week's Call Statistics**: Summary of this week's call activity
- **This Month's Call Statistics**: Summary of this month's call activity

## Installation

### Option 1: HACS (Recommended)

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. In HACS, go to **Integrations**
3. Click the **+** button in the bottom right
4. Add this repository: `https://github.com/oneofthegeeks/goto-connect-call-stats`
5. Search for "GoTo Connect Call Stats" in the HACS store
6. Click "Download" and restart Home Assistant

### Option 2: Manual Installation

1. Download the `custom_components/goto_connect_call_stats` folder
2. Copy it to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

### Prerequisites

1. **GoTo Connect Developer Account**: You need a GoTo Connect developer account
2. **API Credentials**: Create an application in the GoTo Connect Developer Portal

### Setting up API Credentials

1. Go to the [GoTo Connect Developer Portal](https://developer.goto.com/)
2. Create a new application or use an existing one
3. Note your **Client ID** and **Client Secret**
4. Set the redirect URI to `https://home-assistant.io/auth/callback`
5. Ensure your application has the required scopes:
   - `call-events.v1.events.read`
   - `users.v1.read`
   - `presence.v1.read`

### Adding the Integration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "GoTo Connect Call Stats"
4. Enter your Client ID and Client Secret
5. Complete the OAuth authentication process
6. The integration will be added and sensors will appear

## Dashboard Example

Here's an example dashboard configuration to display your call statistics:

```yaml
# Example dashboard configuration
views:
  - title: "Call Statistics"
    path: call-stats
    badges: []
    cards:
      - type: vertical-stack
        cards:
          - type: entities
            title: "Today's Call Activity"
            entities:
              - entity: sensor.total_calls_today
              - entity: sensor.incoming_calls_today
              - entity: sensor.outgoing_calls_today
              - entity: sensor.missed_calls_today
          
          - type: entities
            title: "Call Duration"
            entities:
              - entity: sensor.total_call_duration_today
              - entity: sensor.average_call_duration_today
          
          - type: entities
            title: "Period Statistics"
            entities:
              - entity: sensor.todays_call_statistics
              - entity: sensor.this_weeks_call_statistics
              - entity: sensor.this_months_call_statistics
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your Client ID and Client Secret are correct
   - Ensure your redirect URI matches exactly: `https://home-assistant.io/auth/callback`
   - Check that your GoTo Connect application has the required scopes

2. **No Data Available**
   - The integration only shows data for calls that occurred after installation
   - Historical data may not be immediately available
   - Check your GoTo Connect account has recent call activity

3. **Sensors Not Updating**
   - The integration updates every 5 minutes
   - Check the integration status in **Settings** → **Devices & Services**
   - Restart the integration if needed

### Debugging

To enable debug logging, add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.goto_connect_call_stats: debug
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 **Documentation**: Check this README for setup instructions
- 🐛 **Issues**: Open an issue on [GitHub](https://github.com/oneofthegeeks/goto-connect-call-stats/issues)
- 💬 **Discussions**: Start a discussion for questions and ideas

## Acknowledgments

- GoTo Connect for providing the API
- The Home Assistant community for excellent integration patterns
- Contributors and users of this integration 