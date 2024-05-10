This script sets up a Discord bot that can track the spawn times of bosses in a game and send reminders to a designated channel and role before each boss spawns. The bot can also provide information about the next boss spawns upon request.

## Requirements:
- discord.py and python-dotenv must be installed

To use this script, you need to set up a Discord bot and obtain its token, as well as the IDs for the selected Discord server, channel, and role you want to use. You also need to use the .env file with the following variables:
- BOT_TOKEN: the token for your Discord bot
- GUILD_ID: the ID of the Discord server you want to use
- CHANNEL_ID: the ID of the Discord channel you want the bot to send messages in
- PING_ROLE_ID: the ID of the Discord role you want to ping before each boss spawns
- PERMISSION_ROLE_ID: the ID of the Discord role you want to be able to control the bot. requires REQUIRE_PERMISSION to be true
- AERO_ID: the ID of the user who has permission to execute the bot commands
- REQUIRE_PERMISSION: whether the PERMISSION_ROLE_ID is required to control the bot

## Commands
/boss-warn: starts timers for new server
- round_length: the length of the current game round in seconds
- remind: a boolean value indicating whether to set up reminders for the next boss spawns

/show-boss-spawns: displays the current timers (exact same as the one from boss-warn)

/cancel-reminder: cancels all REMINDERS (not timers)

