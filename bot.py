

import traceback

try:
    import discord
    import os
    import asyncio
    import datetime
    from datetime import datetime, timedelta
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
        react_message_channel_id = file_json.get('react_message_channel_id', None)
        
        # ensure that if the react_message_channel_id is nonexistent, it will be added to the json file
        if react_message_channel_id == None:
            react_message_channel_id = 1

    # ensure that the json file is up to date
    with open('react_message_id.json', 'w') as file:
        json.dump({"react_message_id": react_message_id, "react_message_channel_id": react_message_channel_id }, file)


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
    react_message_channel: discord.TextChannel = None
    ping_role: discord.Role = None
    react_message: discord.Message = None

    message_queue = []

    pun_spawn_time: datetime = None
    deci_spawn_time: datetime = None
    galle_spawn_time: datetime = None
    kodi_spawn_time: datetime = None

    last_used_boss_time: datetime = None

    remind_users_id_list = []

    # dont do any reminders at or under this id number
    cancel_reminder_id = 0

    current_reminder_id = 1



    async def next_boss_spawns_message(interaction: discord.Interaction = None, send_message_channel: discord.TextChannel = None):
        """
        Sends a message with the next boss spawns that are still being tracked
        """
        # calculate seconds until each boss spawns
        current_time = datetime.now()

        embed = discord.Embed(title="Boss Warning")

        double_message_flag = False

        global pun_spawn_time, deci_spawn_time, galle_spawn_time, kodi_spawn_time, last_used_boss_time

        # assemble strings with the next boss spawns
        embed.add_field(name="Punisher", value=f"at {pun_spawn_time.strftime('%H:%M')} (In {round((pun_spawn_time - current_time).total_seconds() / 60)} Minutes)")
        embed.add_field(name="X-0/Decimator", value=f"at {deci_spawn_time.strftime('%H:%M')} (In {round((deci_spawn_time - current_time).total_seconds() / 60)} Minutes)")
        embed.add_field(name="Galleon", value=f"at {galle_spawn_time.strftime('%H:%M')} (In {round((galle_spawn_time - current_time).total_seconds() / 60)} Minutes)")
        embed.add_field(name="Kodiak", value=f"at {kodi_spawn_time.strftime('%H:%M')} (In {round((kodi_spawn_time - current_time).total_seconds() / 60)} Minutes)")

        embed.set_footer(text=f"Times were calcuated at {last_used_boss_time.strftime('%H:%M')} ({round((current_time - last_used_boss_time).total_seconds() / 60)} Minutes ago)")

        # if there was a passed interaction, send the message as a followup. otherwise, send standalone message
        if interaction != None:
            await interaction.followup.send(embed=embed)
        elif channel != None:
            await send_message_channel.send(embed=embed)
        else:
            if not double_message_flag:
                await channel.send(embed=embed)


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


    @command_tree.command(name = "boss-warn", description = "Gives info about next boss spawn, can ping just before spawn (round length in mins)", guild=guild_discord_object) 
    async def boss_warn(interaction: discord.Interaction, round_length: int, remind: bool):
        # tell discord that the bot recieved the command but is "thinking"
        await interaction.response.defer()

        if test_user_perms(interaction.user):
            try:

                round_length *= 60 # convert seconds to minutes

                # calculate seconds until each boss spawns
                global pun_spawn_time, deci_spawn_time, galle_spawn_time, kodi_spawn_time, last_used_boss_time, message_queue

                # reset the message queue
                message_queue = []

                pun_spawn_delta_time = timedelta(seconds=1698 - (round_length % 1698)) 
                deci_spawn_delta_time = timedelta(seconds=3600 - (round_length % 3600))
                galle_spawn_delta_time = timedelta(seconds=4200 - (round_length % 4200))
                kodi_spawn_delta_time = timedelta(seconds=7200 - (round_length % 7200))

                # get the current time
                current_time = datetime.now()

                # make a datetime for when each boss spawns
                pun_spawn_time = current_time + pun_spawn_delta_time
                deci_spawn_time = current_time + deci_spawn_delta_time
                galle_spawn_time = current_time + galle_spawn_delta_time
                kodi_spawn_time = current_time + kodi_spawn_delta_time

                last_used_boss_time = datetime.now()

                # send a message with the next boss spawns. pass the interaction so that the message is sent as a followup
                await next_boss_spawns_message(interaction=interaction)


                # see if we need to resend any react messages
                if remind:

                    global react_message, react_message_id, react_message_channel_id, react_message_channel

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
                        json.dump({"react_message_id": react_message_id, "react_message_channel_id": react_message_channel_id }, file)


                # add remind messages to message queue, if remind is true
                if remind:
                    global current_reminder_id

                    # message object structure: [ping datetime, boss name, reminder_id, channel, boss spawn interval]
                    
                    pun_message_object = [pun_spawn_time, "Punisher", current_reminder_id, interaction.channel, 1698]
                    deci_message_object = [deci_spawn_time, r"Decimator, 45% chance of X-0", current_reminder_id + 1, interaction.channel, 3600]
                    galle_message_object = [galle_spawn_time, "Galleon", current_reminder_id + 2, interaction.channel, 4200]
                    kodi_message_object = [kodi_spawn_time, "Kodiak", current_reminder_id + 3, interaction.channel, 7200]

                    message_queue.append(pun_message_object)
                    message_queue.append(deci_message_object)
                    message_queue.append(galle_message_object)
                    message_queue.append(kodi_message_object)

                    current_reminder_id += 4

            except Exception as e:
                print(e)
                await interaction.followup.send("`An error occurred`", ephemeral=True)


        # if they didnt pass the permission check to execute the command  
        else:
            await interaction.followup.send("You do not have permission to execute this command", ephemeral=True)   



    @command_tree.command(name = "show-boss-spawns", description = "Displays the next boss spawn time", guild=guild_discord_object) 
    async def resend_react_message(interaction: discord.Interaction):

        # tell discord that the bot recieved the command but is "thinking"
        await interaction.response.defer()

        if test_user_perms(interaction.user):
            try:

                global last_used_boss_time
                if last_used_boss_time != None:
                    await next_boss_spawns_message(interaction=interaction)
                else:
                    await interaction.followup.send("Use `/boss-warn` to set the boss spawn times, then use this command again to see the next boss spawns", ephemeral=True)     

            except Exception as e:
                print(e)
                await interaction.followup.send("`An error occurred`", ephemeral=True)

        # if they didnt pass the permission check to execute the command  
        else:
            await interaction.followup.send("You do not have permission to execute this command", ephemeral=True)



    @command_tree.command(name = "cancel-reminder", description = "Cancels all active reminders", guild=guild_discord_object) 
    async def resend_react_message(interaction: discord.Interaction):

        # tell discord that the bot recieved the command but is "thinking"
        await interaction.response.defer()

        if test_user_perms(interaction.user):
            try:

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

                global cancel_reminder_id

                cancel_reminder_id = current_reminder_id - 1
                await interaction.followup.send("All previous reminders have been cancelled.")

            except Exception as e:
                print(e)
                await interaction.followup.send("`An error occurred`", ephemeral=True)

        # if they didnt pass the permission check to execute the command  
        else:
            await interaction.followup.send("You do not have permission to execute this command", ephemeral=True)



    async def start_timer():
        timecount = 0
        while True:
            await asyncio.sleep(1) # make sure that the program doesnt use 100% cpu lmao
            # decrement the time until each boss spawns by 1 every second
            global pun_spawn_time, deci_spawn_time, galle_spawn_time, kodi_spawn_time, remind_users_id_list, react_message, react_message_id, react_message_channel_id, react_message_channel

            # get the current time and add 3 minutes to it, so that we can ping the role 3 minutes before the boss spawns
            current_time = datetime.now() + timedelta(seconds=180)

            # message object structure: [ping datetime, boss name, reminder_id, channel, boss spawn interval]

            send_messsage_object = None

            for message_object in message_queue:
                if message_object[0] < current_time:

                    if message_object[2] > cancel_reminder_id:
                        
                        if send_messsage_object == None:
                            send_messsage_object = message_object
                        else:
                            send_messsage_object[1] = send_messsage_object[1] + f", {message_object[1]}"

                    message_queue.remove(message_object)

                    # add the message back to the queue with the new ping time
                    message_queue.append([message_object[0] + timedelta(seconds=message_object[4]), message_object[1], message_object[2], message_object[3], message_object[4]])

                    if message_object[4] == 1698:
                        pun_spawn_time = pun_spawn_time + timedelta(seconds=1698)
                    elif message_object[4] == 3600:
                        deci_spawn_time = deci_spawn_time + timedelta(seconds=3600)
                    elif message_object[4] == 4200:
                        galle_spawn_time = galle_spawn_time + timedelta(seconds=4200)
                    elif message_object[4] == 7200:
                        kodi_spawn_time = kodi_spawn_time + timedelta(seconds=7200)

            if send_messsage_object != None:
                # send the message
                await send_messsage_object[3].send(f"{ping_role.mention}\n{send_messsage_object[1]} is spawning in 3 minutes")

            timecount = timecount + 1
            if timecount > 6:
                timecount = 0

                # attempt to retrieve the react for roles message from the channel
                try:
                    react_message = await channel.fetch_message(int(react_message_id))
                except:
                    try:
                        react_message = await react_message_channel.fetch_message(int(react_message_id))
                    except: 
                        pass

                try:
                    # refresh the user list every 6 seconds
                    found_users_ids = []

                    if react_message:
                        for reaction_type in react_message.reactions:
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

                except Exception as e:
                    #traceback.print_exc()
                    pass



    # do this when the bot is connected to discord
    @bot.event
    async def on_ready():

        global guild, channel, ping_role, react_message, react_message_id, react_message_channel_id, react_message_channel
        guild = bot.get_guild(int(guild_id))
        channel = bot.get_channel(int(channel_id))

        if react_message_channel_id == 1:
            react_message_channel_id = channel_id
        react_message_channel = bot.get_channel(int(react_message_channel_id))
        ping_role = guild.get_role(int(ping_role_id))
        
        commands = await command_tree.sync(guild=guild_discord_object)
        print("Bot is ready")

        asyncio.ensure_future(start_timer())

        try:
            react_message = await channel.fetch_message(int(react_message_id))
        except:
            try:
                react_message = await react_message_channel.fetch_message(int(react_message_id))
            except:
                pass
    

    bot.run(bot_token)

except Exception as e:
    print(e)
    traceback.print_exc()
    input("Press enter to exit")






