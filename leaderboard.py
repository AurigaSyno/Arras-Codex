import json
import discord
import os
from constants import LEADERBOARD_FILE
from bot_instance import bot

# #data_storage
# {
#     "player_id": {
#         "codes":
#         "clicks"
#     },
#    "player_id": {
#         "codes":
#         "clicks"
#     },
#     ...
# }

from bot_logger import get_logger

logger = get_logger("leaderboard")

print("Loading leaderboard into memory...")
try:
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            leaderboard_users = json.load(f)
        logger.info(f"Loaded {len(leaderboard_users)} players from {LEADERBOARD_FILE}.")
    else:
        logger.warning(f"❌{LEADERBOARD_FILE} does not exist, creating blank file.")
        leaderboard_users = []
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(leaderboard_users, f, indent=2, ensure_ascii=False)
except Exception as e:
    logger.error(f"Error loading leaderboard file {e}.")
    leaderboard_users = []

def save_leaderboard_data():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(leaderboard_users, f, indent=2, ensure_ascii=False)

def user_data_builder(id, name):
    user_data = {}
    user_data["id"] = id
    user_data["name"] = name
    user_data["codes"] = 0
    user_data["clicks"] = 0
    return user_data

def create_user_data(user_id, name):
    user_data = user_data_builder(user_id, name)
    leaderboard_users.append(user_data)

def add_code_credit_to_user(user_id, name):
    for user in leaderboard_users:
        if user["id"] == user_id:
            user["codes"] += 1
            save_leaderboard_data()
            return

    #user must not exist
    create_user_data(user_id, name)
    for user in leaderboard_users:
        if user["id"] == user_id:
            user["codes"] += 1
            save_leaderboard_data()
            return

def add_click_credit_to_user(user_id, name):
    for user in leaderboard_users:
        if user["id"] == user_id:
            user["clicks"] += 1
            save_leaderboard_data()
            return

    #user must not exist
    create_user_data(user_id, name)
    for user in leaderboard_users:
        if user["id"] == user_id:
            user["clicks"] += 1
            save_leaderboard_data()
            return

def get_top_ten_users():
    sorted_users = sorted(leaderboard_users, key=lambda x: x["codes"], reverse=True)
    return sorted_users[:10]

async def get_leaderboard_embed():
    users = get_top_ten_users()

    i = 1
    desc_data = ""
    for user in users:
        user_obj = await bot.fetch_user(user["id"])
        #desc_data = desc_data + f"#{i}: {user_obj.display_name} with {user["codes"]} codes and {user["clicks"]} clicks.\n\n"
        desc_data = desc_data + f"#{i}: **{user_obj.display_name}** with **{user["codes"]}** codes.\n\n"
        i += 1

    embed = discord.Embed(title="Top Code Contributors", description=desc_data, color=0x00ff00)
    return embed