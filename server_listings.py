import discord
from bot_parser import servers
from bot_instance import bot
from bot_utilities import load_config_file

from constants import TeamColor

server_listings = []

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

#def update_server_listing(guild, id):

def update_all_server_listings():
    for server in servers:
        coded_num = server.get("coded")
        if coded_num > 0:
            server_id = server.get("id")
            server_listing = get_listing_for_server(server_id)

            if server_listing:
                has_server_changed = not (server.get("server_code") == server_listing.get("server_code"))
            
            if not server_listing or has_server_changed: #we need a new listing
                new_listing = server_listing_builder()
                new_listing["id"] = server_id
                new_listing["name"] = server.get("server_name")
                new_listing["server_code"] = server.get("server_code")
                new_listing["server_uptime"] = server.get("uptime")
                new_listing["coded_num"] = coded_num
                save_listing(new_listing, server_id)
                print(f"Added listing for {server_id}")


def server_listing_builder():
    server_listing = {
        # "message_id": None, #FIXME, this can't be here, it needs to be per server, not per listing
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

    embed = discord.Embed(title=f"{name} #{id}", description=description_str)
    view = ListingButtonView(listing)
    return [embed, view]

async def get_listing_embed_for_server(id):
    server_listing = get_listing_for_server(id)

    if server_listing:
        embed = await listing_embed_builder(server_listing)
        return embed
    else:
        return None