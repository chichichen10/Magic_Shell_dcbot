# Magic Shell Discord Bot aka 神奇海螺

Discord bot with voice greetings, team splitting, OpenAI responses, Fish Audio
TTS, and a Quart dashboard.

## Structure

- `main.py`: process entrypoint
- `bot/app.py`: application composition and lifecycle
- `bot/events/`: Discord event handlers
- `bot/commands/`: text and slash commands
- `services/`: AI, audio, TTS, asset, and team logic
- `repositories/`: Replit DB access
- `web/`: dashboard application

## Required environment variables

- `BOT_TOKEN`
- `OPEN_AI_API_KEY`
- `FISH_AUDIO_API_KEY`

Optional settings include `OPEN_AI_MODEL`, `FISH_REFERENCE_ID`, `PORT`,
`DASHBOARD_HOST`, and `ASSET_ROOT`.

Run the bot with `python main.py`.

This bot is made with Discord.py and may not be copied for commercial use or
distribution.

&copy; 2023 All Rights Reserved.
