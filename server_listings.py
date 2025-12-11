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

def clear_all_listings():
    global server_listings
    server_listings = []
    save_listings_file()

def get_listing_for_server(id):
    global server_listings
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

def server_listing_has_codes(id):
    for server_listing in server_listings:
        if server_listing.get("id", None) == id:
            if server_listing.get("red_code", None) or server_listing.get("blue_code", None) or server_listing.get("green_code", None) or server_listing.get("purple_code", None):
                return True

    return False

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
    
def remove_code_from_listing(id, team):
    server_listing = get_listing_for_server(id)

    if server_listing:
        if team == TeamColor.Red:
            server_listing["red_code"] = None
            server_listing["red_submitted"] = None
        if team == TeamColor.Blue:
            server_listing["blue_code"] = None
            server_listing["blue_submitted"] = None
        if team == TeamColor.Green:
            server_listing["green_code"] = None
            server_listing["green_submitted"] = None
        if team == TeamColor.Purple:
            server_listing["purple_code"] = None
            server_listing["purple_submitted"] = None

        save_listing(server_listing, id)
        return True
    else:
        print(f"Error, tried to remove code from server [{id}] that has no listing!")
        return False

async def get_listing_message_for_server(guild, server_id):
    server_listing = get_listing_for_server(server_id)
    guild_embeds = server_listing.get("guild_embeds", {})
    #print(guild_embeds)
    if str(guild.id) in guild_embeds:
        #print(guild.id)
        guild_embed_data = guild_embeds.get(str(guild.id))
        #print(guild_embed_data)
        channel_id = guild_embed_data[0]
        msg_id = guild_embed_data[1]
        channel = await bot.fetch_channel(channel_id)
        if channel:
            try:
                message = await channel.fetch_message(msg_id)
                if message:
                    #print("returned message")
                    return message
            except:
                print("Unable to fetch message: get_listing_message_for_server")
                pass
                
    return None

async def send_listing_message_for_server(guild, server_id):
    server_listing = get_listing_for_server(server_id)
    guild_embeds = server_listing.get("guild_embeds", {})
    config = load_config_file(guild.id)
    if config:
        channel_id = config.get("codes_channel_id", None)
        if channel_id:
            channel = await bot.fetch_channel(channel_id)
            if channel:
                code_embed = await get_listing_embed_for_server(server_id)
                if code_embed:
                    try:
                        new_message = await channel.send(embed=code_embed[0], view=code_embed[1])
                        if new_message:
                            guild_embeds[str(guild.id)] = [channel_id, new_message.id]
                            save_listing(server_listing, server_id)
                            return True
                    except discord.Forbidden:
                        print(f"Bot lacks posting permissions for {channel.name} in {guild.name}")
                        pass
                    except Exception as e:
                        print(f"Error in send_listing_message_for_server: {e}")
                        pass

    return False

# Valid listing with codes for aa
# Valid listing with codes for eb
# Valid listing with codes for aa
# Valid listing with codes for aa
# The offending crime shown above
# async def send_all_available_listing_messages(): #I'm leaving this here to remind myself for loops are shit and cannot be trusted
#     for listing in server_listings: #what the actual fuck is happening, why doesn't this work
#         for guild in bot.guilds:
#             if is_guild_accepts_codes(guild):
#                 server_id = listing.get("id")
#                 if server_listing_has_codes(server_id):
#                     print(f"Valid listing with codes for {server_id}")
#                     await send_listing_message_for_server(guild, server_id)

async def send_all_available_listing_messages():
    for guild in bot.guilds:
        await send_available_listing_messages_in_guild(guild)

async def send_available_listing_messages_in_guild(guild):
    for i in range(len(server_listings)):
        listing = server_listings[i]
        print(f"listing num: {i}")
        if is_guild_accepts_codes(guild):
            server_id = listing.get("id")
            print(f"Listing id for i {i} is: {server_id}")
            if server_listing_has_codes(server_id):
                print(f"Valid listing with codes for {server_id}")
                await send_listing_message_for_server(guild, server_id)

async def update_listing_message(message, server_id):
    #print("update_listing_message called" )
    code_embed = await get_listing_embed_for_server(server_id)
    await message.edit(embed=code_embed[0], view=code_embed[1])
    
def is_guild_accepts_codes(guild):
    config = load_config_file(guild.id)
    if config:
        channel_id = config.get("codes_channel_id", None)
        if channel_id:
            return True
        
    return False

async def update_server_listing_messages(server_id):
    for guild in bot.guilds:
        if is_guild_accepts_codes(guild):
            message = await get_listing_message_for_server(guild, server_id)
            if message:
                await update_listing_message(message, server_id)
            else: #either it was never sent, or there's an issue
                await send_listing_message_for_server(guild, server_id)

async def remove_listing_messages(server_id):
    for guild in bot.guilds:
        message = await get_listing_message_for_server(guild, server_id)
        if message:
            await message.delete()

async def update_all_server_listings():
    for server in servers:
        coded_num = server.get("coded")
        if coded_num > 0:
            server_id = server.get("id")
            server_listing = get_listing_for_server(server_id)

            if server_listing:
                recorded_listing = server_listing.get("server_code")
                server_changed = not (server.get("server_code") == server_listing.get("server_code"))
                if server_changed:
                    await remove_listing_messages(server_id)
                    new_listing = server_listing_builder()
                    new_listing["id"] = server_id
                    new_listing["name"] = server.get("server_name")
                    new_listing["server_code"] = server.get("server_code")
                    new_listing["server_uptime"] = server.get("uptime")
                    new_listing["coded_num"] = coded_num
                    new_listing["guild_embeds"] = {}

                    save_listing(new_listing, server_id)
                    print(f"Reset listing for {server_id} ({recorded_listing} -> {server.get("server_code")})")
                    continue
            
            if not server_listing or server_changed: #we need a new listing
                new_listing = server_listing_builder()
                new_listing["id"] = server_id
                new_listing["name"] = server.get("server_name")
                new_listing["server_code"] = server.get("server_code")
                new_listing["server_uptime"] = server.get("uptime")
                new_listing["coded_num"] = coded_num
                new_listing["guild_embeds"] = {}
                save_listing(new_listing, server_id)
                print(f"Added listing for {server_id}")
                continue

    for listing in server_listings:
        server_id = listing.get("id", None)
        if server_id:
            if not server_is_coded(server_id):
                await remove_listing_messages(server_id)
                server_listings.remove(listing)
                print(f"Server #{server_id} is no longer coded, removing listing")

    save_listings_file()

# How guild embed is stored:
# #wa server listing:
# listing {
#     "guild_embeds" : {
#         guild_id: [code_channel_id, msg_id]
#         guild_id: [code_channel_id, msg_id]
#         ...
#     }
# }

def server_listing_builder():
    server_listing = {
        "guild_embeds": {},
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

    color_str = ""
    code_str = ""
    submitter_str = ""

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

    if red_code:
        color_str = color_str + "🟥 Red\n"
        code_str = code_str + f"{red_code}\n"
        submitter_str = submitter_str + f"{red_supplier.name}\n"

    if blue_code:
        color_str = color_str + "🟦 Blue\n"
        code_str = code_str + f"{blue_code}\n"
        submitter_str = submitter_str + f"{blue_supplier.name}\n"
    
    if green_code:
        color_str = color_str + "🟩 Green\n"
        code_str = code_str + f"{green_code}\n"
        submitter_str = submitter_str + f"{green_supplier.name}\n"
    
    if purple_code:
        color_str = color_str + "🟪 Purple\n"
        code_str = code_str + f"{purple_code}\n"
        submitter_str = submitter_str + f"{purple_supplier.name}\n"

    if color_str:
        embed = discord.Embed(title=f"#{id} {name}", color=0x00ff00)
        embed.add_field(name="Team", value=color_str, inline=True)
        embed.add_field(name="Code", value=code_str, inline = True)
        embed.add_field(name="Submitted By", value=submitter_str, inline = True)
    else:
        description_str = "No codes have been submitted"
        embed = discord.Embed(title=f"#{id} {name}", description=description_str, color=0x87CEEB)

    view = ListingButtonView(listing)
    return [embed, view]

async def get_listing_embed_for_server(id):
    server_listing = get_listing_for_server(id)

    if server_listing:
        embedtuple = await listing_embed_builder(server_listing)
        return embedtuple
    else:
        return None