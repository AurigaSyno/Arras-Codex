import os
import discord
from discord.ext import tasks
import bot_logger

import constants
import slash_commands
from bot_instance import bot

from bot_parser import fetch_status_then_parse
from leaderboard import save_leaderboard_data
from server_listings import update_all_server_listings, send_all_available_listing_messages, update_leaderboard_messages
from bot_utilities import load_config_file, save_config_file, finish_initializing, clear_guild_code_channel

from dotenv import load_dotenv
from bot_logger import get_logger

async def print_error_to_operator(string):
    operator_ids = constants.OPERATOR_IDS
    for operator_id in operator_ids:
        operator = await bot.fetch_user(operator_id)
        if operator:
            try:
                await operator.send(f"Error in main loop: {string}")
                print(f"Sent error message to {operator.name}")
            except:
                print(f"Could not send error message to operator: {operator_id}")
                continue

@discord.ext.tasks.loop(seconds=30)
async def update_server_list_task():
    try:
        if fetch_status_then_parse():
            await update_leaderboard_messages()
            await update_all_server_listings()
    except Exception as e:
        await print_error_to_operator(e)
        pass

async def clear_all_code_channels():
    for guild in bot.guilds:
        await clear_guild_code_channel(guild)

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
    if fetch_status_then_parse():
        await update_all_server_listings()

    print("Sending leaderboards")
    await update_leaderboard_messages()

    print("Posting all relevant listings...")
    await send_all_available_listing_messages()

    print("Starting server refresh loop...")
    update_server_list_task.start()

    print("Bot initialized") 
    finish_initializing()

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("❌ DISCORD_TOKEN not found! Make sure you have a .env file with DISCORD_TOKEN set.")

logger = bot_logger.get_logger("bot") #bot refers to the name of this file!
guild_configs = None

bot.add_listener(init_on_ready, "on_ready")
print( "Bot is starting...")
bot.run(TOKEN) #Run the bot