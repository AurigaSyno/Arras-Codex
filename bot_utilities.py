import os
import json
import re
import discord
from discord import PartialEmoji

import constants
from bot_logger import get_logger
from bot_instance import bot

logger = get_logger("utilities")

bot_initialized = False

def is_bot_initialized():
    return bot_initialized

def finish_initializing():
    global bot_initialized
    bot_initialized = True

def new_config_builder():
    config = {
            "guild_name": None,
            "codes_channel_id": None,
            "is_blacklisted": False,
            "blacklist_reason": ""
        }

    return config

#================Blacklist Block================
def save_blacklist(blacklist):
    blacklist_file = constants.BLACKLIST_FILE
    with open(blacklist_file, "w", encoding="utf-8") as f:
        json.dump(blacklist, f, indent=2, ensure_ascii=False)

def create_blacklist():
    blacklist_file = constants.BLACKLIST_FILE
    blacklist = []
    with open(blacklist_file, "w", encoding="utf-8") as f:
        json.dump(blacklist, f, indent=2, ensure_ascii=False)

def load_blacklist():
    blacklist_file = constants.BLACKLIST_FILE
    if os.path.exists(blacklist_file): #load blacklist
        with open(blacklist_file, "r", encoding="utf-8") as f:
            blacklist = json.load(f)
            return blacklist
    else:
        create_blacklist()

        if os.path.exists(blacklist_file): #load blacklist
            with open(blacklist_file, "r", encoding="utf-8") as f:
                blacklist = json.load(f)
                return blacklist
            
#================Privilege Block================
def save_privilege(privilege):
    privilege_file = constants.PRIVILEGE_FILE
    with open(privilege_file, "w", encoding="utf-8") as f:
        json.dump(privilege, f, indent=2, ensure_ascii=False)

def create_privilege():
    privilege_file = constants.PRIVILEGE_FILE
    privilege = []
    with open(privilege_file, "w", encoding="utf-8") as f:
        json.dump(privilege, f, indent=2, ensure_ascii=False)

def load_privilege():
    privilege_file = constants.PRIVILEGE_FILE
    if os.path.exists(privilege_file): #load privilege
        with open(privilege_file, "r", encoding="utf-8") as f:
            privilege = json.load(f)
            return privilege
    else:
        create_privilege()

        if os.path.exists(privilege_file): #load privilege
            with open(privilege_file, "r", encoding="utf-8") as f:
                privilege = json.load(f)
                return privilege

#================Config Block================
def load_config_file(guild_id):
    config_path = os.path.join(constants.GUILDS_CONFIG_PATH, f"{guild_id}.json")
    if os.path.exists(config_path): #load server config
        with open(config_path, "r", encoding="utf-8") as f:
            configs = json.load(f)
            return configs
    else:
        guild = bot.get_guild(guild_id)
        create_config_file(guild)

        #try loading new file
        if os.path.exists(config_path): #load server config
            with open(config_path, "r", encoding="utf-8") as f:
                configs = json.load(f)
                return configs
        else:
            return None #Serious issues

def create_config_file(guild):
    
    os.makedirs(constants.GUILDS_CONFIG_PATH, exist_ok=True)

    config = new_config_builder()
    config["guild_name"] = guild.name

    config_path = os.path.join(constants.GUILDS_CONFIG_PATH, f"{guild.id}.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    logger.info(f"Created {config_path}")

def save_config_file(guild_id, config):
    config_path = os.path.join(constants.GUILDS_CONFIG_PATH, f"{guild_id}.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

async def clear_guild_code_channel(guild):
    config = load_config_file(guild.id)
    if config:
        channel_id = config.get("codes_channel_id", None)
        if channel_id:
            try:
                channel = await bot.fetch_channel(channel_id)
                if channel:
                        def check_message(message):
                            return message.author == bot.user
                        
                        await channel.purge(limit=None, check=check_message)
                
            except discord.Forbidden:
                print(f"Bot lacks purge permissions for guild: {guild.name}")
                pass
                    #TODO:Don't allow codes to be posted in this channel
            except discord.NotFound:
                print(f"Unable to find channel for guild {guild.name}")
                pass
            except Exception as e:
                print(f"Error in clear_all_code_channels: {e}")
                pass

def bot_has_manage_msg_perms(guild):
    bot_member = guild.me
    if bot_member.guild_permissions.manage_messages:
        return True
    
    return False

tank_emojis = {
    "red": "<:basicred:1449457381082791956>",
    "blue": "<:basicblue:1449457376624119971>",
    "green": "<:basicgreen:1449457378004304002>",
    "purple": "<:basicpurple:1449457379644280964>"
}

def get_emoji_for_tank(name):
    emoji_str = tank_emojis.get(name, None)

    if emoji_str:
        m = re.match(r"<:([a-zA-Z0-9_]+):(\d+)>", emoji_str)
        if m:
            emoji_obj = PartialEmoji(name=m.group(1), id=int(m.group(2)))
            return emoji_obj
        
    return "❌"

def get_emoji_str_for_tank(name):
    return tank_emojis.get(str(name), "❌")