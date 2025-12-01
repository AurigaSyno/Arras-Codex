import discord
from bot_parser import servers

def

server_listings = []

def get_listing_for_code(id):
    for server_listing in server_listings:
        if server_listing.get("id", None):
            return server_listing
    return None

def update_server_listings():
    for server in servers:
        if server.get("coded"):
            server_listing = get_listing_for_code(server.get("id"))
            has_server_changed = (server.get("server_code") == server_listing.get("server_code"))
            
            if server_listing and not has_server_changed:

            else: #There is no listing, so we need to send one

def server_listing_builder():
    server_listing = {
        "id": None, #wpd
        "name": None,
        "server_code": None,
        "server_uptime": None,
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

def listing_embed_builder(listing):
    embed = discord.Embed(title=f"#{code} {listing.get("name")}")

    red blue green purple