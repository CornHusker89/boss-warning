


import discord
import os
import asyncio
import datetime
from datetime import timedelta


from dotenv import load_dotenv
load_dotenv()



# you could also just replace os.getenv('BOT_TOKEN') with the actual token if you dont want to use a .env file
bot_token = os.getenv('BOT_TOKEN')
# discord server id, same goes as for the above (guilds are just servers)
guild_id = os.getenv('GUILD_ID')
# channel id for the channel you want the bot to send messages in
channel_id = os.getenv('CHANNEL_ID')
# role id for the role you want to ping when a boss spawns
ping_role_id = os.getenv('PING_ROLE_ID')
# aero's user id (for the perms)
aero_id = os.getenv('AERO_ID')



# These are high-level perms for the bot. I put in the ones i assumed you would need, remove any you don't need.
# You can also use bot_intents.all() to enable all perms, but that might be scary for others who dont trust you.
bot_intents = discord.Intents.default()

bot_intents.members = True
bot_intents.messages = True
bot_intents.message_content = True


bot = discord.Client(intents=bot_intents)
command_tree = discord.app_commands.CommandTree(bot)

guild: discord.Guild = discord.Object(id=guild_id)
channel: discord.TextChannel = bot.get_channel(channel_id)


pun_spawn_time = -1
deci_spawn_time = -1
galle_spawn_time = -1
kodi_spawn_time = -1



async def next_boss_spawns_message():
    """
    Sends a message with the next boss spawns that are still being tracked
    """
    # calculate seconds until each boss spawns

    # get the current time
    local_time = datetime.datetime.now()

    pun_message = ""
    deci_message = ""
    galle_message = ""
    koki_message = ""

    # assemble a string with the next 4 boss spawns
    if pun_spawn_time > 0:
        pun_message = f"{local_time + timedelta(seconds=pun_spawn_time)} ({round(pun_spawn_time / 60)} Minutes)"

    if deci_spawn_time > 0:
        deci_message = f"{local_time + timedelta(seconds=deci_spawn_time)} ({round(deci_spawn_time / 60)} Minutes)"

    if galle_spawn_time > 0:
        galle_message = f"{local_time + timedelta(seconds=galle_spawn_time)} ({round(galle_spawn_time / 60)} Minutes)"

    if kodi_spawn_time > 0:
        koki_message = f"{local_time + timedelta(seconds=kodi_spawn_time)} ({round(kodi_spawn_time / 60)} Minutes)"

    message = f"Next boss spawns: {pun_message}\n{deci_message}\n{galle_message}\n{koki_message}"

    await channel.send(message)



async def warn_boss_spawn(time_until_ping: int, user_ids: list, boss_name: str):
    """
    Set up a timer to ping users before boss spawn
    """
    await asyncio.sleep(time_until_ping)

    # assemble a string to ping all the users
    pings = ""
    for id in user_ids:
        pings = pings + f"<@{id}> "
    
    # send the message
    await channel.send(f"{pings}\n{boss_name} is spawning in 3 minutes")
    await next_boss_spawns_message()




@command_tree.command(name = "boss-warn", description = "Gives info about next boss spawn, can ping just before spawn", guild=guild) 
async def list_temporary_whitelist_command(interaction: discord.Integration, round_length: int, remind: bool = False):
    # tell discord that the bot recieved the command but is "thinking"
    await interaction.response.defer()

    # set to "if True:" to get rid of the permission check
    if interaction.user.id == aero_id:
        try:

            # get all users of the role
            ids = []
            for member in guild.members:
                # test if the member has the ping role, if so, add them to the list
                if member.get_role(ping_role_id) != None:
                    ids.append(member.id)


            # calculate seconds until each boss spawns
            global pun_spawn_time, deci_spawn_time, galle_spawn_time, kodi_spawn_time
            pun_spawn_time = 1698 - (round_length % 1698)
            deci_spawn_time = 3600 - (round_length % 3600)
            galle_spawn_time = 4200 - (round_length % 4200)
            kodi_spawn_time = 7200 - (round_length % 7200)

            # send a message with the next boss spawns
            await next_boss_spawns_message()

            # start timers to ping users before each boss spawns, if remind is true
            if remind:
                asyncio.ensure_future(warn_boss_spawn(time_until_ping=pun_spawn_time, user_ids=ids, boss_name="Punisher"))
                asyncio.ensure_future(warn_boss_spawn(time_until_ping=deci_spawn_time, user_ids=ids, boss_name=r"X-0, 45% chance of Decimator"))
                asyncio.ensure_future(warn_boss_spawn(time_until_ping=galle_spawn_time, user_ids=ids, boss_name="Galleon"))
                asyncio.ensure_future(warn_boss_spawn(time_until_ping=kodi_spawn_time, user_ids=ids, boss_name="Kodiak"))


        except Exception as e:
            print(e)
            await interaction.followup.send("`An error occurred`", ephemeral=True)


    # if they didnt pass the permission check        
    else:
        await interaction.followup.send("You do not have permission to execute this command", ephemeral=True)


async def start_timer():
    while True:
        await asyncio.sleep(1)
        # decrement the time until each boss spawns by 1 every second
        pun_spawn_time = pun_spawn_time - 1
        deci_spawn_time = deci_spawn_time - 1
        galle_spawn_time = galle_spawn_time - 1
        kodi_spawn_time = kodi_spawn_time - 1


@bot.event
async def on_ready():

    await command_tree.sync(guild=guild)
    print("Bot is ready")


bot.run(bot_token)







