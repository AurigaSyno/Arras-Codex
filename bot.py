import os
import discord
from discord.ext import tasks
import bot_logger

import constants
import slash_commands
from bot_instance import bot

from bot_parser import fetch_status_then_parse
from server_listings import update_all_server_listings

from dotenv import load_dotenv
from bot_logger import get_logger

@discord.ext.tasks.loop(seconds=30)
async def update_server_list_task():
    fetch_status_then_parse()
    await update_all_server_listings()

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