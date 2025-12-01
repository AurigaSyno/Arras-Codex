import discord
from discord import Interaction, Guild
import constants
from bot_instance import bot
from bot_logger import get_logger

from parser import servers, fetch_status_then_parse

logger = get_logger("commands")

def setup(bot):
    tree = bot.tree

@bot.tree.command(name="status", description="Get a server's status")
async def status_command(interaction: Interaction, code: str):
    for server in servers:
        if server["id"] == code:
            embed = discord.Embed(title=f"#{code} {server.get("server_name")}")
            embed.add_field(name="Status", value="Ok")
            embed.add_field(name="Clients", value=server.get("clients"))
            embed.add_field(name="Mspt", value=server.get("mspt"))
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    
    await interaction.response.send_message(f"Unable to find server \"{code}\"", ephemeral=True)

@bot.tree.command(name="refresh", description="Refresh internal server list")
async def status_command(interaction: Interaction):
    fetch_status_then_parse()
    await interaction.response.send_message("Refreshed internal server list", ephemeral=True)