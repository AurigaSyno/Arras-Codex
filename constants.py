from enum import Enum

RICH_PRESENCE_ACTIVITY = "Keeping a Watchful Eye..."

STATUS_URL = "https://kvn3s3cpcdk4fl6j-c.uvwx.xyz:8443/2222/status"
STATUS_FILE = "raw_status.json"

LOG_FILE = "bot.log"
GUILDS_CONFIG_PATH = "guild_configs"
BLACKLIST_FILE = "blacklist.json"

class TeamColor(Enum):
    Red = 0
    Blue = 1
    Green = 2
    Purple = 4
