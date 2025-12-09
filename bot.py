import os
import discord
from discord.ext import tasks
import bot_logger

import constants
import slash_commands
from bot_instance import bot

from bot_parser import fetch_status_then_parse
from server_listings import update_all_server_listings, send_all_available_listing_messages
from bot_utilities import load_config_file, save_config_file

from dotenv import load_dotenv
from bot_logger import get_logger

@discord.ext.tasks.loop(seconds=30)
async def update_server_list_task():
    fetch_status_then_parse()
    await update_all_server_listings()

async def clear_all_code_channels():
    for guild in bot.guilds:
        config = load_config_file(guild.id)
        if config:
            channel_id = config.get("codes_channel_id", None)
            if channel_id:
                channel = await bot.fetch_channel(channel_id)
                if channel:
                    try:
                        def check_message(message):
                            return message.author == bot.user
                        
                        await channel.purge(limit=None, check=check_message)
                    
                    except discord.Forbidden:
                        print(f"Bot lacks purge permissions for guild: {guild.name}")
                        pass
                            #TODO:Don't allow codes to be posted in this channel
                    except Exception as e:
                        print(f"Error in clear_all_code_channels: {e}")
                        pass

async def init_on_ready():
    print("Bot initializing...")
    await bot.change_presence(activity=discord.Game(constants.RICH_PRESENCE_ACTIVITY))

    #await log_to_all_guilds(bot.guilds, f"✅ Bot connected as {bot.user}")

    print("Loading slash commands...")
    slash_commands.setup(bot)
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} global slash commands.")
        #await log_to_all_guilds(bot.guilds, f"Synced {len(synced)} global slash commands.")
    except Exception as e:
        logger.error(f"Error syncing slash commands: {e}")
        #await log_to_all_guilds(bot.guilds, f"Error syncing slash commands: {e}")
    
    print("Purging code channels...")
    await clear_all_code_channels()

    print("Fetching server list...")
    fetch_status_then_parse()

    print("Posting all relevant listings...")
    await update_all_server_listings()
    await send_all_available_listing_messages()

    print("Starting server refresh loop...")
    update_server_list_task.start()

    print("Bot initialized") 

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("❌ DISCORD_TOKEN not found! Make sure you have a .env file with DISCORD_TOKEN set.")

logger = bot_logger.get_logger("bot") #bot refers to the name of this file!
guild_configs = None

bot.add_listener(init_on_ready, "on_ready")
print( "Bot is starting...")
bot.run(TOKEN) #Run the bot