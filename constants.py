from enum import Enum

RICH_PRESENCE_ACTIVITY = "Submit codes with /submit"

STATUS_URL = "https://kvn3s3cpcdk4fl6j-c.uvwx.xyz:8443/2222/status"
STATUS_FILE = "raw_status.json"

LOG_FILE = "bot.log"
GUILDS_CONFIG_PATH = "guild_configs"
BLACKLIST_FILE = "blacklist.json"
PRIVILEGE_FILE = "privelege.json"
LISTINGS_FILE = "listings.json"
LEADERBOARD_FILE = "leaderboard.json"

OPERATOR_IDS = [1000953569689747507] #auriga
#                 854537568654065675 #xeroc

class TeamColor(Enum):
    Red = 0
    Blue = 1
    Green = 2
    Purple = 4

class AddRemove(Enum):
    Add = 0
    Remove = 1
