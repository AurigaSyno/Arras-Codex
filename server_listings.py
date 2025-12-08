import os
import json
import discord
from bot_parser import servers, server_is_coded
from bot_instance import bot
from bot_utilities import load_config_file

from constants import TeamColor, LISTINGS_FILE
from bot_logger import get_logger

logger = get_logger("listings")

print("Loading listings into memory...")
try:
    if os.path.exists(LISTINGS_FILE):
        with open(LISTINGS_FILE, "r", encoding="utf-8") as f:
            server_listings = json.load(f)
        logger.info(f"Loaded {len(server_listings)} listings from {LISTINGS_FILE}.")
    else:
        logger.warning(f"❌{LISTINGS_FILE} does not exist, creating blank file.")
        server_listings = []
        with open(LISTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(server_listings, f, indent=2, ensure_ascii=False)
except Exception:
    server_listings = []

def save_listings_file():
    if os.path.exists(LISTINGS_FILE):
        with open(LISTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(server_listings, f, indent=2, ensure_ascii=False)
        #logger.info(f"Saved {len(server_listings)} listings to {LISTINGS_FILE}.")

def get_listing_for_server(id):
    for server_listing in server_listings:
        if server_listing.get("id", None) == id:
            return server_listing
    return None

def save_listing(listing, id):
    for server_listing in server_listings:
        if server_listing.get("id", None) == id:
            server_listings.remove(server_listing)

    server_listings.append(listing)
    return

def server_is_valid(id):
    if not get_listing_for_server(id):
        return False
    return True

def coded_for_server(id):
    listing = get_listing_for_server(id)
    if listing:
        return listing.get("coded_num", 0)
    return 0

def get_code_for_server_team(id, team):
    for server_listing in server_listings:
        if server_listing.get("id", None) == id:
            if team == TeamColor.Red:
                return server_listing.get("red_code", None)
            if team == TeamColor.Blue:
                return server_listing.get("blue_code", None)
            if team == TeamColor.Green:
                return server_listing.get("green_code", None)
            if team == TeamColor.Purple:
                return server_listing.get("purple_code", None)

def add_code_to_listing(id, code, team, user_id):
    server_listing = get_listing_for_server(id)

    if server_listing:
        if team == TeamColor.Red:
            server_listing["red_code"] = code
            server_listing["red_submitted"] = user_id
        if team == TeamColor.Blue:
            server_listing["blue_code"] = code
            server_listing["blue_submitted"] = user_id
        if team == TeamColor.Green:
            server_listing["green_code"] = code
            server_listing["green_submitted"] = user_id
        if team == TeamColor.Purple:
            server_listing["purple_code"] = code
            server_listing["purple_submitted"] = user_id

        save_listing(server_listing, id)
        return True
    else:
        print(f"Error, tried to add code to server [{id}] that has no listing!")
        return False

# def update_server_listing(id):
#     for guild in bot.guilds:

async def update_server_listing_embeds(server_id):
    server_listing = get_listing_for_server(server_id)
    guild_embeds = server_listing.get("guild_embeds", [])
    if guild_embeds:
        for guild_id in guild_embeds:
            guild_embed_data = guild_embeds[f"{guild_id}"]
            msg_id = guild_embed_data[0]
            channel_id = guild_embed_data[1]
            channel = await bot.fetch_channel(channel_id)
            if channel:
                message = await channel.fetch_message(msg_id)
                if message:
                    code_embed = await get_listing_embed_for_server(server_id)
                    if code_embed:
                        await message.edit(embed=code_embed[0], view=code_embed[1])

async def update_all_server_listings():
    for server in servers:
        coded_num = server.get("coded")
        if coded_num > 0:
            server_id = server.get("id")
            server_listing = get_listing_for_server(server_id)

            if server_listing:
                server_changed = not (server.get("server_code") == server_listing.get("server_code"))
                if server_changed:
                    new_listing = server_listing_builder()
                    new_listing["id"] = server_id
                    new_listing["name"] = server.get("server_name")
                    new_listing["server_code"] = server.get("server_code")
                    new_listing["server_uptime"] = server.get("uptime")
                    new_listing["coded_num"] = coded_num

                    # guild_embeds = server_listing.get("guild_embeds", []) #Disabled until I get it working
                    # if guild_embeds:
                    #     for guild_id in guild_embeds.items():
                    #         guild_embed_data = guild_embeds[f"{guild_id}"]
                    #         msg_id = guild_embed_data[0]
                    #         channel_id = guild_embed_data[1]
                    #         channel = await bot.fetch_channel(channel_id)
                    #         if channel:
                    #             message = await channel.fetch_message(msg_id)
                    #             if message:
                    #                 code_embed = await get_listing_embed_for_server(server_id)
                    #                 if code_embed:
                    #                     await message.edit(embed=code_embed[0], view=code_embed[1])

                    save_listing(new_listing, server_id)
                    print(f"Reset listing for {server_id}")
                    continue
            
            if not server_listing or server_changed: #we need a new listing
                new_listing = server_listing_builder()
                new_listing["id"] = server_id
                new_listing["name"] = server.get("server_name")
                new_listing["server_code"] = server.get("server_code")
                new_listing["server_uptime"] = server.get("uptime")
                new_listing["coded_num"] = coded_num
                save_listing(new_listing, server_id) #FIXME: I have to save it twice because get_listing_embed needs this listing to already exist!
                guild_embeds = []
                # for guild in bot.guilds: #Disabled until I can get it working
                #     config = load_config_file(guild.id)
                #     if config:
                #         code_channel_id = config.get("codes_channel_id", None)
                #         print(f"Got code id: {code_channel_id}")
                #         if code_channel_id:
                #             code_channel = await bot.fetch_channel(code_channel_id)
                            
                #             if code_channel:
                #                 print("got code channel")
                #                 code_embed = await get_listing_embed_for_server(server_id)
                #                 if code_embed:
                #                     print("sending embed")
                #                     message = await code_channel.send(embed=code_embed[0], view=code_embed[1])
                #                     embed_dict = {guild.id: [code_channel_id, message.id]}
                #                     guild_embeds.append(embed_dict)

                new_listing["guild_embeds"] = guild_embeds
                save_listing(new_listing, server_id)
                print(f"Added listing for {server_id}")
                continue

    for listing in server_listings:
        server_id = listing.get("id", None)
        if server_id:
            if not server_is_coded(server_id):
                server_listings.remove(listing)
                print(f"Server #{server_id} is no longer coded, removing")

    save_listings_file()

# How guild embed is stored:
# #wa server listing:
# listing {
#     "guild_embeds" : [
#         guild_id: [code_channel_id, msg_id]
#         guild_id: [code_channel_id, msg_id]
#         ...
#     ]
# }

def server_listing_builder():
    server_listing = {
        "guild_embeds": None,
        "id": None, #wpd
        "name": None,
        "server_code": None,
        "server_uptime": None,
        "coded_num": None,
        "red_code": None, #Code ####
        "blue_code": None,
        "green_code": None,
        "purple_code": None,
        "red_submitted": None, #ID of person who submitted the code
        "blue_submitted": None,
        "green_submitted": None,
        "purple_submitted": None
    }
    return server_listing

class ListingButtonView(discord.ui.View):
    def __init__(self, listing):
        super().__init__(timeout=3600)
        server_id = listing.get("id", None)
        red_code = listing.get("red_code", None)
        blue_code = listing.get("blue_code", None)
        green_code = listing.get("green_code", None)
        purple_code = listing.get("purple_code", None)

        if red_code:
            url = f"https://arras.io/#{server_id}{red_code}"
            button = discord.ui.Button(emoji="🟥", url=url)
            self.add_item(button)
        if blue_code:
            url = f"https://arras.io/#{server_id}{blue_code}"
            button = discord.ui.Button(emoji="🟦", url=url)
            self.add_item(button)
        if green_code:
            url = f"https://arras.io/#{server_id}{green_code}"
            button = discord.ui.Button(emoji="🟩", url=url)
            self.add_item(button)
        if purple_code:
            url = f"https://arras.io/#{server_id}{purple_code}"
            button = discord.ui.Button(emoji="🟪", url=url)
            self.add_item(button)

async def listing_embed_builder(listing):
    id = listing.get("id", "?")
    name = listing.get("name", "?")
    red_code = listing.get("red_code", None)
    if red_code:
        red_supplier = await bot.fetch_user(listing.get("red_submitted", None))
    blue_code = listing.get("blue_code", None)
    if blue_code:
        blue_supplier = await bot.fetch_user(listing.get("blue_submitted", None))
    green_code = listing.get("green_code", None)
    if green_code:
        green_supplier = await bot.fetch_user(listing.get("green_submitted", None))
    purple_code = listing.get("purple_code", None)
    if purple_code:
        purple_supplier = await bot.fetch_user(listing.get("purple_submitted", None))

    red_str = f"🟥 Red: #{id}{red_code}   ({red_supplier.name})\n" if red_code else ""
    blue_str = f"🟦 Blue: #{id}{blue_code}   ({blue_supplier.name})\n" if blue_code else ""
    green_str = f"🟩 Green: #{id}{green_code}   ({green_supplier.name})\n" if green_code else ""
    purple_str = f"🟪 Purple: #{id}{purple_code}   ({purple_supplier.name})\n" if purple_code else ""

    description_str = red_str + blue_str + green_str + purple_str
    if not description_str:
        description_str = "No codes have been submitted"

    embed = discord.Embed(title=f"{name} #{id}", description=description_str, color=0x87CEEB)
    view = ListingButtonView(listing)
    return [embed, view]

async def get_listing_embed_for_server(id):
    server_listing = get_listing_for_server(id)

    if server_listing:
        embedtuple = await listing_embed_builder(server_listing)
        return embedtuple
    else:
        return None