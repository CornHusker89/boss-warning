This script sets up a Discord bot that can track the spawn times of bosses in a game and send reminders to a designated channel and role before each boss spawns. The bot can also provide information about the next boss spawns upon request.

Requirements:
- discord.py and python-dotenv must be installed

To use this script, you need to set up a Discord bot and obtain its token, as well as the IDs for the selected Discord server, channel, and role you want to use. You also need to use the .env file with the following variables:
- BOT_TOKEN: the token for your Discord bot
- GUILD_ID: the ID of the Discord server you want to use
- CHANNEL_ID: the ID of the Discord channel you want the bot to send messages in
- PING_ROLE_ID: the ID of the Discord role you want to ping before each boss spawns
- AERO_ID: the ID of the user who has permission to execute the bot commands

To request information about the next boss spawns, you can use the "/boss-warn" command in the designated Discord channel. This command takes two arguments:
- round_length: the length of the current game round in seconds
- remind: a boolean value indicating whether to set up reminders for the next boss spawns

If you set remind to True, the bot will automatically send reminders to the designated channel and ping the designated role before each boss spawns.


