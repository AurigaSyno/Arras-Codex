import os
import json

import constants
from bot_logger import get_logger
from bot_instance import bot

logger = get_logger("utilities")

def new_config_builder():
    config = {
            "guild_name": None,
            "codes_channel_id": None,
            "is_blacklisted": False
        }

    return config

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