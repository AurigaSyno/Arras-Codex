import discord
from discord import Interaction, Guild
import constants
from bot_utilities import load_blacklist, save_blacklist, load_config_file, save_config_file
from server_listings import add_code_to_listing, get_listing_embed_for_server, get_code_for_server_team, server_is_valid, coded_for_server
from bot_instance import bot
from bot_logger import get_logger

from bot_parser import servers, fetch_status_then_parse

logger = get_logger("commands")

def setup(bot):
    tree = bot.tree

def user_is_blacklisted(id):
    blacklist = load_blacklist()
    if id in blacklist:
        return True
    return False

async def send_user_is_blacklisted_msg(interaction):
    embed = discord.Embed(title="Blacklisted", description="You have been blacklisted from the codex.", color=0xff0000)
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
    return

async def send_server_is_blacklisted_msg(interaction, reason):
    embed = discord.Embed(title="Blacklisted", description=f"This server has been blacklisted from the codex for: {reason}, please use another server.", color=0xff0000)
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
    return

def guild_is_blacklisted(guild_id):
    config = load_config_file(guild_id)
    if config:
        return config.get("is_blacklisted")
    return False
    
def get_blacklist_reason(guild_id):
    config = load_config_file(guild_id)
    if config:
        return config.get("blacklist_reason")
    return "Database Error"


#==================Command Block==================

#TODO: blacklist server
#TODO: blacklist user


@bot.tree.command(name="status", description="Get a server's status")
async def status_command(interaction: Interaction, code: str):
    if user_is_blacklisted(interaction.user.id):
        send_user_is_blacklisted_msg(interaction)
        return
    
    if guild_is_blacklisted(interaction.guild.id):
        reason = get_blacklist_reason(interaction.guild.id)
        send_server_is_blacklisted_msg(interaction, reason)
        return
    
    for server in servers:
        if server["id"] == code:
            embed = discord.Embed(title=f"#{code} {server.get("server_name")}")
            embed.add_field(name="Status", value="Ok")
            embed.add_field(name="Clients", value=server.get("clients"))
            embed.add_field(name="Mspt", value=server.get("mspt"))
            embed.add_field(name="Code String", value=server.get("server_code"))
            embed.add_field(name="Has Codes", value=server.get("coded"))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
            return
    
    await interaction.response.send_message(f"Unable to find server \"{code}\"", ephemeral=True)

@bot.tree.command(name="refresh", description="Refresh internal server list")
async def status_command(interaction: Interaction):
    fetch_status_then_parse()
    await interaction.response.send_message("Refreshed internal server list", ephemeral=True, delete_after=30)

def get_code_and_server_from_url(url):
    index = url.find('#')
    if index == -1:
        return None

    server = url[index+1:index+3]
    code = url[index+3:]

    return [code, server]
    #https://arras.io/#aa2964
    #arras.io/#aa2964

@bot.tree.command(name="submit", description="Submit a code to the codex (URL)")
async def submit_command(interaction: Interaction, url: str, team: constants.TeamColor):
    if user_is_blacklisted(interaction.user.id):
        send_user_is_blacklisted_msg(interaction)
        return
    
    if guild_is_blacklisted(interaction.guild.id):
        reason = get_blacklist_reason(interaction.guild.id)
        send_server_is_blacklisted_msg(interaction, reason)
        return

    tuple = get_code_and_server_from_url(url)

    if not tuple:
        embed = discord.Embed(title="Error", description=f"Invalid URL!", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
        return
    
    code = tuple[0]
    server = tuple[1]

    existing_code = get_code_for_server_team(server, team)
    if existing_code:
        if existing_code == code:
            embed = discord.Embed(title="Thank You", description=f"This code has already been submitted by another user.", color=0x00ff00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
            return
        # else:
        #     #TODO: Warning message about already submitted code

    coded_num = coded_for_server(server)

    if team.name.lower() == "purple" and coded_num < 4:
        embed = discord.Embed(title="Error", description=f"This server has no purple team!", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
        return
    
    if team.name.lower() == "red" and coded_num < 3:
        embed = discord.Embed(title="Error", description=f"This server has no red team!", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
        return
    
    success = add_code_to_listing(server, code, team, interaction.user.id)

    if success:
        embed = discord.Embed(title="Thank You", description=f"Your {team.name.lower()} code for #{server} was successfully submitted!", color=0x00ff00)
        print(f"Code: {code} submitted for Server: {server} by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, delete_after=60)
    else:
        embed = discord.Embed(title="Error", description=f"Something went wrong!", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)



@bot.tree.command(name="codes", description="Get codes for a server")
async def submit_command(interaction: Interaction, server: str):
    if user_is_blacklisted(interaction.user.id):
        send_user_is_blacklisted_msg(interaction)
        return
    
    if guild_is_blacklisted(interaction.guild.id):
        reason = get_blacklist_reason(interaction.guild.id)
        send_server_is_blacklisted_msg(interaction, reason)
        return
    
    if not server_is_valid(server):
        embed = discord.Embed(title="Error", description=f"#{server} is not a valid server!", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
        return

    embedtuple = await get_listing_embed_for_server(server)
    embed = embedtuple[0]
    view = embedtuple[1]

    if embed:
        await interaction.response.send_message(embed=embed, view=view, delete_after=360)
        return
    else:
        embed = discord.Embed(title="Error", description=f"Something went wrong!", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
        return