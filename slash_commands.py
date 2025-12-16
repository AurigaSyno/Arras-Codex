import discord
from discord import Interaction, Guild
import constants
from bot_utilities import load_blacklist, save_blacklist, load_config_file, save_config_file, load_privilege, save_privilege
from bot_utilities import is_bot_initialized, clear_guild_code_channel, bot_has_manage_msg_perms
from server_listings import add_code_to_listing, get_listing_embed_for_server, get_code_for_server_team, update_server_listing_messages
from server_listings import server_is_valid, coded_for_server, update_all_server_listings, clear_all_listings, remove_code_from_listing
from server_listings import send_available_listing_messages_in_guild, get_submitter_for_server_team
from bot_instance import bot
from bot_logger import get_logger

from bot_parser import servers, sandboxes, fetch_status_then_parse

logger = get_logger("commands")

def setup(bot):
    tree = bot.tree

def is_operator(user_id):
    if user_id not in constants.OPERATOR_IDS:
        return False
    else:
        return True #return true if bot operator

async def operator_fail_message(interaction: Interaction):
    embed = discord.Embed(title="Permission Denied", description="You don't have bot administrator permissions.", color=0xff0000)
    await interaction.response.send_message(embed=embed, ephemeral=True)

def is_admin(interaction: Interaction):
    if is_operator(interaction):
        return True #FIXME: operators probably should NOT get this permission
    
    if not interaction.user.guild_permissions.administrator:
        return False
    else:
        return True #return true if admin

async def admin_fail_message(interaction: Interaction):
    embed = discord.Embed(title="Permission Denied", description="You do not have administrator permissions.", color=0xff0000)
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def bot_not_initialized_message(interaction: Interaction):
    embed = discord.Embed(title="Bot Not Initialized", description="Wait a minute or two to allow the bot to start", color=0xff0000)
    await interaction.response.send_message(embed=embed, ephemeral=True)

def user_is_blacklisted(id):
    blacklist = load_blacklist()
    if id in blacklist:
        return True
    return False

def blacklist_user(id):
    blacklist = load_blacklist()
    blacklist.append(id)
    save_blacklist(blacklist)

def unblacklist_user(id):
    blacklist = load_blacklist()
    blacklist.remove(id)
    save_blacklist(blacklist)

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

def user_is_privileged(id):
    if is_operator(id):
        return True
    
    privilege = load_privilege()
    if id in privilege:
        return True
    return False

def privilege_user(id):
    privilege = load_privilege()
    privilege.append(id)
    save_privilege(privilege)

def unprivilege_user(id):
    privilege = load_privilege()
    privilege.remove(id)
    save_privilege(privilege)

async def send_user_is_unprivileged_msg(interaction):
    embed = discord.Embed(title="Permissions Error", description="You don't have permission to use this command.", color=0xff0000)
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
    return

async def bot_does_not_have_permission_msg(interaction):
    embed = discord.Embed(title="Permissions Error", description="Bot does not have manage_messages permissions for this server, this feature is unavailable.", color=0xff0000)
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
    return


#==================Operator Block==================
@bot.tree.command(name="refresh", description="Refresh internal server list")
async def refresh_command(interaction: Interaction):
    if not is_operator(interaction.user.id):
        await operator_fail_message(interaction)
        return

    if fetch_status_then_parse():
        await update_all_server_listings()

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

@bot.tree.command(name="deletelistings", description="Operator Only")
async def del_listings_command(interaction: Interaction):
    if not is_bot_initialized():
        await bot_not_initialized_message(interaction)
        return
    
    if not is_operator(interaction.user.id):
        await operator_fail_message(interaction)
        return
    
    clear_all_listings()

    embed = discord.Embed(title="Cleared Listings", description=f"Listings deleted and file cleared", color=0x00ff00)
    await interaction.response.send_message(embed=embed, delete_after=30)
    return

@bot.tree.command(name="blacklistserver", description="Blacklist Servers")
async def blacklistserver_command(interaction: Interaction, action: constants.AddRemove, server: str, reason : str = None):
    if not is_operator(interaction.user.id):
        await operator_fail_message(interaction)
        return
    
    valid_id = False
    for guild in bot.guilds:
        if guild.id == server:
            valid_id = True

    if not valid_id:
        embed = discord.Embed(title="Invalid Arguments", description=f"Invalid Server ID!", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
        return
    
    config = load_config_file(server)
    if config:
        is_blacklisted = config.get("is_blacklisted", False)
    
        if action == constants.AddRemove.Add:
            if not reason:
                embed = discord.Embed(title="Invalid Arguments", description=f"You must set a reason!", color=0xff0000)
                await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
                return
            if is_blacklisted:
                embed = discord.Embed(title="No Action", description=f"This server is already blacklisted!", color=0xff0000)
                await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
                return
            else:
                config["is_blacklisted"] = True
                config["blacklist_reason"] = reason
                save_config_file(server, config)
                embed = discord.Embed(title="Server Blacklisted", description=f"Server ID: {server} was blacklisted.", color=0x00ff00)
                await interaction.response.send_message(embed=embed, delete_after=30)
                return
        
        if action == constants.AddRemove.Remove:
            if not is_blacklisted:
                embed = discord.Embed(title="No Action", description=f"This server is not blacklisted!", color=0xff0000)
                await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
                return
            else:
                config["is_blacklisted"] = False
                config["blacklist_reason"] = ""
                save_config_file(server, config)
                embed = discord.Embed(title="Server Unblacklisted", description=f"Server ID: {server} was unblacklisted.", color=0x00ff00)
                await interaction.response.send_message(embed=embed, delete_after=30)
                return

@bot.tree.command(name="blacklistuser", description="Blacklist Users")
async def blacklistuser_command(interaction: Interaction, action: constants.AddRemove, user: discord.User):
    if not is_operator(interaction.user.id):
        await operator_fail_message(interaction)
        return
    
    if action == constants.AddRemove.Add:
        if user_is_blacklisted(user.id):
            embed = discord.Embed(title="No Action", description=f"This user is already blacklisted!", color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
            return
        else:
            blacklist_user(user.id)
            embed = discord.Embed(title="User Blacklisted", description=f"{user.name} was blacklisted from the codex by {interaction.user.name}", color=0x00ff00)
            await interaction.response.send_message(embed=embed, delete_after=30)
            return
    
    if action == constants.AddRemove.Remove:
        if not user_is_blacklisted(user.id):
            embed = discord.Embed(title="No Action", description=f"This user is not blacklisted!", color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
            return
        else:
            unblacklist_user(user.id)
            embed = discord.Embed(title="User Unblacklisted", description=f"{user.name} was removed from the codex blacklist by {interaction.user.name}", color=0x00ff00)
            await interaction.response.send_message(embed=embed, delete_after=30)
            return

@bot.tree.command(name="privilegeuser", description="Privilege Users")
async def privilege_command(interaction: Interaction, action: constants.AddRemove, user: discord.User):
    if not is_operator(interaction.user.id):
        await operator_fail_message(interaction)
        return
    
    if action == constants.AddRemove.Add:
        if user_is_privileged(user.id):
            embed = discord.Embed(title="No Action", description=f"This user is already privileged!", color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
            return
        else:
            privilege_user(user.id)
            embed = discord.Embed(title="User Privileged", description=f"{user.name} was given privilege by {interaction.user.name}", color=0x00ff00)
            await interaction.response.send_message(embed=embed, delete_after=30)
            return
    
    if action == constants.AddRemove.Remove:
        if not user_is_privileged(user.id):
            embed = discord.Embed(title="No Action", description=f"This user is not privileged!", color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
            return
        else:
            unprivilege_user(user.id)
            embed = discord.Embed(title="User Unprivileged", description=f"{user.name}'s privilege was removed by {interaction.user.name}", color=0x00ff00)
            await interaction.response.send_message(embed=embed, delete_after=30)
            return
        
#==================Admin==================
@bot.tree.command(name="setcodeschannel", description="Sets the channel codes are automatically posted to")
async def setcodeschannel_command(interaction: Interaction, channel: discord.TextChannel):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server!", ephemeral=True)
        return

    if not is_admin(interaction):
        await admin_fail_message(interaction)
        return
    
    if not bot_has_manage_msg_perms:
        await bot_does_not_have_permission_msg(interaction)
        return

    config = load_config_file(interaction.guild.id)
    if config:
        config["codes_channel_id"] = channel.id
    
    save_config_file(interaction.guild.id, config)

    #await clear_guild_code_channel(interaction.guild) #doesn't need to be here

    embed = discord.Embed(title="Channel Set", description=f"Successfully set code channel", color=0x00ff00)
    await interaction.response.send_message(embed=embed, delete_after=30)
    return

@bot.tree.command(name="clearcodeschannel", description="Clears codes channel")
async def clearcodeschannel_command(interaction: Interaction):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server!", ephemeral=True)
        return
    
    if not is_admin(interaction):
        await admin_fail_message(interaction)
        return
    
    if not bot_has_manage_msg_perms:
        await bot_does_not_have_permission_msg(interaction)
        return
    
    await interaction.response.defer(ephemeral=True)

    await clear_guild_code_channel(interaction.guild)

    embed = discord.Embed(title="Channel Cleared", description=f"Successfully cleared code channel", color=0x00ff00)
    await interaction.followup.send(embed=embed)
    return

@bot.tree.command(name="reloadcodeschannel", description="Reloads codes channel")
async def reloadcodeschannel_command(interaction: Interaction):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server!", ephemeral=True)
        return
    
    if not is_admin(interaction):
        await admin_fail_message(interaction)
        return
    
    if not bot_has_manage_msg_perms:
        await bot_does_not_have_permission_msg(interaction)
        return
    
    await interaction.response.defer(ephemeral=True)
    print(f"{interaction.user.name} is reloading a code channel in {interaction.guild.name}.")
    
    await clear_guild_code_channel(interaction.guild)
    await send_available_listing_messages_in_guild(interaction.guild)

    embed = discord.Embed(title="Channel Reloaded", description=f"Successfully reloaded code channel", color=0x00ff00)
    await interaction.followup.send(embed=embed)
    return

#==================Privileged==================
@bot.tree.command(name="sandboxes", description="Get all active sandboxes")
async def sandboxes_command(interaction: Interaction, show_hidden: bool = False):
    if not user_is_privileged(interaction.user.id):
        await send_user_is_unprivileged_msg(interaction)
        return
    
    if not show_hidden:
        embed = discord.Embed(title="Sandboxes")
        total_sandboxes = 0
        for sandbox in sandboxes:
            clients = sandbox.get("clients", 0)
            if clients:
                total_sandboxes += 1
                embed.add_field(name=f"#{sandbox.get("id")}", value=f"{clients}")
                embed.set_footer(text=f"Total active sandboxes: {total_sandboxes}.")
        
        if total_sandboxes > 0:
            await interaction.response.send_message(embed=embed)
            return
        else:
            embed.add_field(name="No active sandboxes", value="No active sandboxes")
            await interaction.response.send_message(embed=embed)
            return
    
    else:
        desc = ""
        for sandbox in sandboxes:
            desc = desc + f"#{sandbox.get("id")}: {sandbox.get("clients", 0)}\n"
        embed = discord.Embed(title="Sandboxes", description=desc)
        await interaction.response.send_message(embed=embed)
        return
    
# @bot.tree.command(name="sandbox", description="Get information about a sandbox")
# async def sandbox_command(interaction: Interaction):

@bot.tree.command(name="status", description="Get a server's status")
async def status_command(interaction: Interaction, code: str):
    if user_is_blacklisted(interaction.user.id):
        await send_user_is_blacklisted_msg(interaction)
        return
    if interaction.guild:
        if guild_is_blacklisted(interaction.guild.id):
            reason = get_blacklist_reason(interaction.guild.id)
            await send_server_is_blacklisted_msg(interaction, reason)
            return
    
    for server in servers:
        if server["id"] == code:
            embed = discord.Embed(title=f"#{code} {server.get("server_name")}", color=0x00ff00)
            embed.add_field(name="Status", value="Ok")
            embed.add_field(name="Clients", value=server.get("clients"))
            embed.add_field(name="Mspt", value=server.get("mspt"))
            embed.add_field(name="Code String", value=server.get("server_code"))
            embed.add_field(name="Has Codes", value=server.get("coded"))
            embed.set_footer(text=f"Requested by {interaction.user.name}")
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
            return
    
    await interaction.response.send_message(f"Unable to find server \"{code}\"", ephemeral=True)

@bot.tree.command(name="removecode", description="Remove a code from codex")
async def remove_code_command(interaction: Interaction, server: str, team: constants.TeamColor):
    if not is_bot_initialized():
        await bot_not_initialized_message(interaction)
        return

    if not user_is_privileged(interaction.user.id):
        await send_user_is_unprivileged_msg(interaction)
        return

    server_str = server.replace("#", "")

    existing_code = get_code_for_server_team(server_str, team)
    if not existing_code:
        embed = discord.Embed(title="No code", description=f"There is no {team.name.lower()} code for #{server_str}", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
        return
    
    success = remove_code_from_listing(server_str, team)

    if success:
        embed = discord.Embed(title="Code Removed", description=f"The {team.name.lower()} code for #{server_str} was successfully removed!", color=0x00ff00)
        print(f"Code removed from server: {server_str} by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=60)
    else:
        embed = discord.Embed(title="Error", description=f"Something went wrong!", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)

    if success:
        await update_server_listing_messages(server_str)

#==================Normal Users==================
@bot.tree.command(name="servers", description="List all servers")
async def servers_command(interaction: Interaction, showhidden: bool = False):
    if user_is_blacklisted(interaction.user.id):
        await send_user_is_blacklisted_msg(interaction)
        return
    
    if interaction.guild:
        if guild_is_blacklisted(interaction.guild.id):
            reason = get_blacklist_reason(interaction.guild.id)
            await send_server_is_blacklisted_msg(interaction, reason)
            return
    
    link_str = ""
    #region_str = ""
    name_str = ""
    clients_str = ""
    for server in servers:
        hidden = server.get("hidden", False)
        if not hidden or showhidden:
            link_str = link_str + f"[#{server.get("id","x")}](https://arras.io/#{server.get("id","x")})\n"
            #region_str = region_str + f"{server.get("region_str", "N/A")}\n"
            name_str = name_str + f"{server.get("region_str", "N/A")} {server.get("server_name","Unknown")}\n"
            clients_str = clients_str + f"{server.get("clients", "0")}/80\n"
    
    embed = discord.Embed(title="Arras Server List", color=0x00ff00)
    embed.add_field(name="Link", value=link_str, inline=True)
    #embed.add_field(name="Region", value=region_str, inline=True)
    embed.add_field(name="Name", value=name_str, inline=True)
    embed.add_field(name="Players", value=clients_str, inline=True)
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

class EditCodeView(discord.ui.View):
    def __init__(self, server_id, code, team):
        self.used = False
        self.server_id = server_id
        self.code = code
        self.team = team
        super().__init__()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel")
    async def cancel_button_callback(self, interaction: discord.Interaction, button):
        if self.used == True:
            await interaction.response.send_message("This interaction is expired", ephemeral=True)
            return
        for btn in self.children:
            btn.disabled = True
        self.used = True
        await interaction.response.defer()

    @discord.ui.button(label="Change Code", style=discord.ButtonStyle.success, custom_id="change")
    async def change_button_callback(self, interaction: discord.Interaction, button):
        if self.used == True:
            await interaction.response.send_message("This interaction is expired", ephemeral=True)
            return
        
        success = add_code_to_listing(self.server_id, self.code, self.team, interaction.user.id, interaction.user.name)

        if success:
            embed = discord.Embed(title="Thank You", description=f"Your {self.team.name.lower()} code for #{self.server_id} was successfully changed!", color=0x00ff00)
            print(f"Code: {self.code} submitted for Server: {self.server_id} by {interaction.user.display_name}")
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=60)
        else:
            embed = discord.Embed(title="Error", description=f"Something went wrong!", color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
        
        for btn in self.children:
            btn.disabled = True
        self.used = True

        await update_server_listing_messages(self.server_id) #Put this at the end to avoid the interaction timing out

@bot.tree.command(name="submit", description="Submit a code to the codex (URL)")
async def submit_command(interaction: Interaction, url: str, team: constants.TeamColor):
    if not is_bot_initialized():
        await bot_not_initialized_message(interaction)
        return
    
    if user_is_blacklisted(interaction.user.id):
        await send_user_is_blacklisted_msg(interaction)
        return
    
    if interaction.guild:
        if guild_is_blacklisted(interaction.guild.id):
            reason = get_blacklist_reason(interaction.guild.id)
            await send_server_is_blacklisted_msg(interaction, reason)
            return

    tuple = get_code_and_server_from_url(url)

    if not tuple:
        embed = discord.Embed(title="Error", description=f"Invalid URL!\n Example usage: `/submit https://arras.io/#ca3757 Red`", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
        return
    
    code = tuple[0]
    server = tuple[1]

    coded_num = coded_for_server(server)

    if team.name.lower() == "purple" and coded_num < 4:
        embed = discord.Embed(title="Error", description=f"This server has no purple team!", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
        return
    
    if team.name.lower() == "red" and coded_num < 3:
        embed = discord.Embed(title="Error", description=f"This server has no red team!", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
        return
    
    existing_code = get_code_for_server_team(server, team)
    if existing_code:
        if existing_code == code:
            embed = discord.Embed(title="Thank You", description=f"This code has already been submitted by another user.", color=0x00ff00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
            return
        else:
            if not (get_submitter_for_server_team(server, team) == interaction.user.id): #if this is not the user who submitted this code
                embed = discord.Embed(title="Confirm Code Change", description="You are about to submit a different code than the one that is already submitted.\nOnly confirm this if the current code is wrong!", color=0x00ff00)
                view = EditCodeView(server, code, team)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                return
            else:
                success = add_code_to_listing(server, code, team, interaction.user.id, interaction.user.name)

                if success:
                    embed = discord.Embed(title="Thank You", description=f"Your {team.name.lower()} code for #{server} was successfully updated!", color=0x00ff00)
                    print(f"Code: {code} submitted for Server: {server} by {interaction.user.display_name}")
                    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=60)
                    await update_server_listing_messages(server) #Put this at the end to avoid the interaction timing out
                    return
                else:
                    embed = discord.Embed(title="Error", description=f"Something went wrong!", color=0xff0000)
                    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
                    return
    
    success = add_code_to_listing(server, code, team, interaction.user.id, interaction.user.name)

    if success:
        embed = discord.Embed(title="Thank You", description=f"Your {team.name.lower()} code for #{server} was successfully submitted!", color=0x00ff00)
        print(f"Code: {code} submitted for Server: {server} by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=60)
    else:
        embed = discord.Embed(title="Error", description=f"Something went wrong!", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)

    await update_server_listing_messages(server) #Put this at the end to avoid the interaction timing out

@bot.tree.command(name="codes", description="Get codes for a server")
async def codes_command(interaction: Interaction, server: str):
    if not is_bot_initialized():
        await bot_not_initialized_message(interaction)
        return
    
    if user_is_blacklisted(interaction.user.id):
        await send_user_is_blacklisted_msg(interaction)
        return
    
    if interaction.guild:
        if guild_is_blacklisted(interaction.guild.id):
            reason = get_blacklist_reason(interaction.guild.id)
            await send_server_is_blacklisted_msg(interaction, reason)
            return
    
    server_str = server.replace("#", "")
    
    if not server_is_valid(server_str):
        embed = discord.Embed(title="Error", description=f"#{server_str} is not a valid server!", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)
        return
    
    await interaction.response.defer(ephemeral=True)

    embedtuple = await get_listing_embed_for_server(server_str)
    embed = embedtuple[0]
    view = embedtuple[1]

    if embed:
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        await interaction.followup.send(embed=embed, view=view)
        return
    else:
        embed = discord.Embed(title="Error", description=f"Something went wrong!", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return