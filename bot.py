

import traceback

try:
    import discord
    import os
    import asyncio
    import datetime
    from datetime import timedelta
    import json




    from dotenv import load_dotenv
    load_dotenv()


    # set to false if you want everyone to be able to use the commands
    require_command_permission = True

    

    # you could also just replace os.getenv('BOT_TOKEN') with the actual token if you dont want to use a .env file
    bot_token = os.getenv('BOT_TOKEN')
    # discord server id, same goes as for the above (guilds are just servers)
    guild_id = os.getenv('GUILD_ID')
    # channel id for the channel you want the bot to send messages in
    channel_id = os.getenv('CHANNEL_ID')
    # channel id for the channel you want the bot to persistent messages in
    persistent_message_channel_id = os.getenv('PERSISTENT_MESSAGE_CHANNEL_ID')
    # role id for the role you want to ping when a boss spawns
    ping_role_id = os.getenv('PING_ROLE_ID')
    # role id for the role you want to have permission to use commands
    permission_role_id = os.getenv('PERMISSION_ROLE_ID')
    # aero's user id (for the perms)
    aero_id = os.getenv('AERO_ID')


    # get the react for roles message from the json file
    with open('react_message_id.json') as file:
        file_json: dict = json.load(file)
        react_message_id = file_json['react_message_id']
        persistent_react_message_id = file_json.get('persistent_react_message_id', None)
        react_message_channel_id = file_json.get('react_message_channel_id', None)

        # ensure that if the persistent_react_message_id is nonexistent, it will be added to the json file
        if persistent_react_message_id == None:
            persistent_react_message_id = 1

        
        # ensure that if the react_message_channel_id is nonexistent, it will be added to the json file
        if react_message_channel_id == None:
            react_message_channel_id = 1

    # ensure that the json file is up to date
    with open('react_message_id.json', 'w') as file:
        json.dump({"react_message_id": react_message_id, "persistent_react_message_id": persistent_react_message_id, "react_message_channel_id": react_message_channel_id }, file)


    # These are high-level perms for the bot. I put in the ones i assumed you would need, remove any you don't need.
    # You can also use bot_intents.all() to enable all perms, but that might be scary for others who dont trust you.
    bot_intents = discord.Intents.default()

    bot_intents.members = True
    bot_intents.messages = True
    bot_intents.message_content = True
    bot_intents.guilds = True
    bot_intents.reactions = True


    bot = discord.Client(intents=bot_intents)
    command_tree = discord.app_commands.CommandTree(bot)

    guild_discord_object = discord.Object(id=int(guild_id))
    guild: discord.Guild = None
    
    channel: discord.TextChannel = None
    persistent_message_channel: discord.TextChannel = None
    react_message_channel: discord.TextChannel = None
    ping_role: discord.Role = None
    react_message: discord.Message = None
    persistent_react_message: discord.Message = None

    pun_spawn_time = -1
    deci_spawn_time = -1
    galle_spawn_time = -1
    kodi_spawn_time = -1

    remind_users_id_list = []



    async def next_boss_spawns_message(interaction: discord.Interaction = None):
        """
        Sends a message with the next boss spawns that are still being tracked
        """
        # calculate seconds until each boss spawns

        # get the current time
        local_time = datetime.datetime.now()

        embed = discord.Embed(title="Boss Warning")


        # assemble a string with the next 4 boss spawns
        if pun_spawn_time > 0:
            pun_time = local_time + timedelta(seconds=pun_spawn_time)
            embed.add_field(name="Punisher", value=f"{pun_time.strftime('%H:%M')} (In {round(pun_spawn_time / 60)} Minutes)")

        if deci_spawn_time > 0:
            deci_time = local_time + timedelta(seconds=deci_spawn_time)
            embed.add_field(name="X-0/Decimator", value=f"{deci_time.strftime('%H:%M')} (In {round(deci_spawn_time / 60)} Minutes)")

        if galle_spawn_time > 0:
            galle_time = local_time + timedelta(seconds=galle_spawn_time)
            embed.add_field(name="Galleon", value=f"{galle_time.strftime('%H:%M')} (In {round(galle_spawn_time / 60)} Minutes)")

        if kodi_spawn_time > 0:
            kodi_time = local_time + timedelta(seconds=kodi_spawn_time)
            embed.add_field(name="Kodiak", value=f"{kodi_time.strftime('%H:%M')} (In {round(kodi_spawn_time / 60)} Minutes)")


        # if there was a passed interaction, send the message as a followup. otherwise, send standalone message
        if interaction != None:
            await interaction.followup.send(embed=embed)
        else:
            await channel.send(embed=embed)


    async def warn_boss_spawn(time_until_ping: int, boss_name: str):
        """
        Set up a timer to ping users before boss spawn
        """
        wait_time = time_until_ping - 180
        if wait_time < 0:
            wait_time = 0
        await asyncio.sleep(wait_time)
        
        # send the message
        await channel.send(f"{ping_role.mention}\n{boss_name} is spawning in 3 minutes")

        # make sure that we dont send the boss spawn message twice
        if wait_time > 0:
            await next_boss_spawns_message()


    def test_user_perms(user: discord.User):
        """
        Test if a user has permission to execute commands
        """
        if user.id == int(aero_id) or not require_command_permission:
            return True
        else:
            for role in user.roles:
                if role.id == int(permission_role_id):
                    return True
            return False


    @command_tree.command(name = "boss-warn", description = "Gives info about next boss spawn, can ping just before spawn", guild=guild_discord_object) 
    async def boss_warn(interaction: discord.Interaction, round_length: int, remind: bool):
        # tell discord that the bot recieved the command but is "thinking"
        await interaction.response.defer()

        if test_user_perms(interaction.user):
            try:

                round_length *= 60 # convert seconds to minutes

                # calculate seconds until each boss spawns
                global pun_spawn_time, deci_spawn_time, galle_spawn_time, kodi_spawn_time
                pun_spawn_time = 1698 - (round_length % 1698)
                deci_spawn_time = 3600 - (round_length % 3600)
                galle_spawn_time = 4200 - (round_length % 4200)
                kodi_spawn_time = 7200 - (round_length % 7200)


                # send a message with the next boss spawns. pass the interaction so that the message is sent as a followup
                await next_boss_spawns_message(interaction = interaction)


                # start timers to ping users before each boss spawns, if remind is true
                if remind:
                    asyncio.ensure_future(warn_boss_spawn(time_until_ping=pun_spawn_time, boss_name="Punisher"))
                    asyncio.ensure_future(warn_boss_spawn(time_until_ping=deci_spawn_time, boss_name=r"X-0, 45% chance of Decimator"))
                    asyncio.ensure_future(warn_boss_spawn(time_until_ping=galle_spawn_time, boss_name="Galleon"))
                    asyncio.ensure_future(warn_boss_spawn(time_until_ping=kodi_spawn_time, boss_name="Kodiak"))



                # see if we need to resend any react messages

                if remind:

                    global react_message, react_message_id, react_message_channel_id, react_message_channel

                    if interaction.channel_id == int(channel_id) or (interaction.channel_id != int(persistent_message_channel_id) and interaction.channel_id != int(react_message_channel_id)):


                        # attempt to retrieve the react for roles message from the channel
                        try:
                            react_message = await channel.fetch_message(int(react_message_id))

                            # remove the react roles from those who reacted to the message
                            for reaction_type in react_message.reactions:
                                async for user in reaction_type.users():
                                    await user.remove_roles(ping_role)

                            await react_message.delete()

                        except:
                            try:
                                react_message = await react_message_channel.fetch_message(int(react_message_id))

                                # remove the react roles from those who reacted to the message
                                for reaction_type in react_message.reactions:
                                    async for user in reaction_type.users():
                                        await user.remove_roles(ping_role)

                                await react_message.delete()
                            except:
                                pass


                        # make a new react for roles message
                        embed = discord.Embed(title="React for Roles", description="React to this message to enable pinging you before a boss spawns")
                        current_channel = bot.get_channel(interaction.channel_id)
                        react_message = await current_channel.send(embed=embed)
                        react_message_id = react_message.id

                        react_message_channel_id = interaction.channel_id
                        react_message_channel = bot.get_channel(int(react_message_channel_id))

                        # write the message id to the json file
                        with open('react_message_id.json', 'w') as file:
                            json.dump({"react_message_id": react_message_id, "persistent_react_message_id": persistent_react_message_id, "react_message_channel_id": react_message_channel_id }, file)


            except Exception as e:
                print(e)
                await interaction.followup.send("`An error occurred`", ephemeral=True)


        # if they didnt pass the permission check to execute the command  
        else:
            await interaction.followup.send("You do not have permission to execute this command", ephemeral=True)   



    @command_tree.command(name = "resend-message", description = "Resends the react-for-role message, deletes old one", guild=guild_discord_object) 
    async def resend_react_message(interaction: discord.Interaction):

        # tell discord that the bot recieved the command but is "thinking"
        await interaction.response.defer()

        if test_user_perms(interaction.user):
            try:

                global react_message, react_message_id, react_message_channel_id, react_message_channel

                # attempt to retrieve the react for roles message from the channel
                try:
                    react_message = await channel.fetch_message(int(react_message_id))
                    await react_message.delete()
                except:
                    try:
                        react_message = await react_message_channel.fetch_message(int(react_message_id))
                        await react_message.delete()
                    except:
                        pass


                # make a new react for roles message
                embed = discord.Embed(title="React for Roles", description="React to this message to enable pinging you before a boss spawns")
                current_channel = bot.get_channel(interaction.channel_id)
                react_message = await current_channel.send(embed=embed)
                react_message_id = react_message.id

                react_message_channel_id = interaction.channel_id
                react_message_channel = bot.get_channel(int(react_message_channel_id))

                # write the message id to the json file
                with open('react_message_id.json', 'w') as file:
                    json.dump({"react_message_id": react_message_id, "persistent_react_message_id": persistent_react_message_id, "react_message_channel_id": react_message_channel_id }, file)

                await interaction.followup.send("Message re-sent")


            except Exception as e:
                print(e)
                await interaction.followup.send("`An error occurred`", ephemeral=True)


        # if they didnt pass the permission check to execute the command  
        else:
            await interaction.followup.send("You do not have permission to execute this command", ephemeral=True)



    async def start_timer():
        """
        Start the timer that decrements the time until each boss spawns
        """
        timecount = 0
        while True:
            await asyncio.sleep(0.997) # attempt to account for the time it takes to run the code
            # decrement the time until each boss spawns by 1 every second
            global pun_spawn_time, deci_spawn_time, galle_spawn_time, kodi_spawn_time, remind_users_id_list, react_message, react_message_id, persistent_react_message, persistent_react_message_id, react_message_channel_id, react_message_channel

            pun_spawn_time = pun_spawn_time - 1
            deci_spawn_time = deci_spawn_time - 1
            galle_spawn_time = galle_spawn_time - 1
            kodi_spawn_time = kodi_spawn_time - 1

            timecount = timecount + 1
            if timecount > 15:
                timecount = 0



                # attempt to retrieve the react for roles message from the channel
                try:
                    react_message = await channel.fetch_message(int(react_message_id))
                except:
                    try:
                        react_message = await react_message_channel.fetch_message(int(react_message_id))
                    except:
                        print("Could not find react-for-roles message, making a new one")

                        # make a new react for roles message
                        embed = discord.Embed(title="React for Roles", description="React to this message to enable pinging you before a boss spawns")
                        react_message = await react_message_channel.send(embed=embed)
                        react_message_id = react_message.id

                        react_message_channel = bot.get_channel(int(react_message_channel_id))

                        # write the message id to the json file
                        with open('react_message_id.json', 'w') as file:
                            json.dump({"react_message_id": react_message_id, "persistent_react_message_id": persistent_react_message_id, "react_message_channel_id": react_message_channel_id }, file)



                # refresh the user list every 20 seconds
                found_users_ids = []

                for reaction_type in react_message.reactions:
                    async for user in reaction_type.users():
                        found_users_ids.append(user.id)

                for reaction_type in persistent_react_message.reactions:
                    async for user in reaction_type.users():
                        found_users_ids.append(user.id)

                for user_id in found_users_ids:
                    if user_id not in remind_users_id_list:
                        # give the user the role
                        user = guild.get_member(user_id)
                        await user.add_roles(ping_role)
                        print(f"Added role to {user.name}")

                for user_id in remind_users_id_list:
                    if user_id not in found_users_ids:
                        # remove the role from the user
                        user = guild.get_member(user_id)
                        await user.remove_roles(ping_role)
                        print(f"Removed role from {user.name}")

                remind_users_id_list = found_users_ids




    # do this when the bot is connected
    @bot.event
    async def on_ready():

        global guild, channel, ping_role, react_message, react_message_id, persistent_react_message, persistent_react_message_id, persistent_message_channel_id, react_message_channel_id, react_message_channel
        guild = bot.get_guild(int(guild_id))
        channel = bot.get_channel(int(channel_id))
        persistent_message_channel = bot.get_channel(int(persistent_message_channel_id))
        react_message_channel = bot.get_channel(int(react_message_channel_id))
        ping_role = guild.get_role(int(ping_role_id))
        
        commands = await command_tree.sync(guild=guild_discord_object)
        print(commands)
        print("Bot is ready")


        # attempt to retrieve the react for roles message from the channel
        try:
            react_message = await channel.fetch_message(int(react_message_id))
        except:
            try:
                react_message = await react_message_channel.fetch_message(int(react_message_id))
            except:
                print("Could not find react-for-roles message, making a new one")

                embed = discord.Embed(title="React for Roles", description="React to this message to enable pinging you before a boss spawns")
                react_message = await react_message_channel.send(embed=embed)
                react_message_id = react_message.id

                # write the message id to the json file
                with open('react_message_id.json', 'w') as file:
                    json.dump({"react_message_id": react_message_id, "persistent_react_message_id": persistent_react_message_id, "react_message_channel_id": react_message_channel_id }, file)

        # do the same, but with the persistent message
        try:
            persistent_react_message = await persistent_message_channel.fetch_message(int(persistent_react_message_id))
        except:
            print("Could not find the persistent react-for-roles message, making a new one")

            embed = discord.Embed(title="React for Roles (Persistent)", description="React to this message to enable pinging you before a boss spawns")
            persistent_react_message = await persistent_message_channel.send(embed=embed)
            persistent_react_message_id = persistent_react_message.id

            # write the message id to the json file
            with open('react_message_id.json', 'w') as file:
                json.dump({"react_message_id": react_message_id, "persistent_react_message_id": persistent_react_message_id, "react_message_channel_id": react_message_channel_id }, file)

        asyncio.ensure_future(start_timer())


    bot.run(bot_token)

except Exception as e:
    print(e)
    traceback.print_exc()
    input("Press enter to exit")






