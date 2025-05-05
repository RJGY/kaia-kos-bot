# Kaia KOS Bot

A Discord bot for tracking Minecraft players and their activity status. This bot helps manage a "Kill On Sight" (KOS) list by monitoring player activity, online status, and last login times.

## Features

- Track multiple Minecraft players simultaneously
- Monitor player online status
- View last login times
- Track time since last Pit action
- Add/remove players from the tracking list
- Automatic API status checking
- Discord slash command support

## Setup

1. Clone the repository
2. Install required dependencies:
   ```bash
   pip install discord.py python-dotenv requests
   ```
3. Create a `.env` file with the following variables:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   HYPIXEL_API_KEY=your_hypixel_api_key
   SYMBOL=your_bot_prefix
   ```

## Commands

- `/list` - Display the current KOS list with player status
- `/add <username>` - Add a player to the tracking list
- `/remove <username>` - Remove a player from the tracking list
- `/sync` - Sync bot commands with Discord
- `/test` - Test command to verify bot functionality

## Requirements

- Python 3.8+
- Discord Bot Token
- Hypixel API Key
- Minecraft API access

## File Structure

- `main.py` - Bot entry point
- `bot.py` - Core bot functionality
- `cogs/api_commands.py` - API and command implementations
- `player_list.txt` - Storage for tracked player UUIDs

## Contributing

Feel free to submit issues and enhancement requests!