import json
import os
import requests
from enum import IntEnum

import constants

raw_server_data = []
valid_server_data = []

servers = []
sandboxes = []

class ServerRegion(IntEnum):
    US_WEST = 0
    US_CENTRAL = 1
    EUROPE = 2
    ASIA = 3
    OCEANIA = 4

class GameMode(IntEnum):
    FFA = 0
    TDM1 = 1
    TDM2 = 2
    TDM3 = 3
    TDM4 = 4
    DUOS = 5
    CLANWARS = 6

class GameModifiers(IntEnum):
    NONE = 0
    GROWTH = 1
    ARMSRACE = 2
    PORTAL = 4
    ROCK = 8
    MAZE = 16
    OPEN = 32

simple_region_map = {
    "w": ["US West", ServerRegion.US_WEST],
    "c": ["US Central", ServerRegion.US_CENTRAL],
    "e": ["Europe", ServerRegion.EUROPE],
    "a": ["Asia", ServerRegion.ASIA],
    "o": ["Oceania", ServerRegion.OCEANIA]
}
def get_region_name(region_code):
    region = region_code
    return simple_region_map.get(region, region_code)[0]
def get_region_int(region_code):
    region = region_code
    return simple_region_map.get(region, region_code)[1]

#============Hosting Code============
host_map = {
    "z": ["Private", None],
    "x": ["Local", None],
    "glitch": ["Glitch", 10],
    "buyvm": ["BuyVM", 15],
    "extravm": ["ExtraVM", 40],
    "hetzner": ["Hetzner", 50],
    "ovh": ["OVH", 45],
    "wsi": ["WSI", 50],
    "vultr": ["Vultr", 30]
}

region_map = {
    "xyz": ["Local", "Localhost", None],
    "unk": ["Unknown", "Unknown", None],
    "svx": ["US West", "Silicon Valley, CA, US", -7],
    "lax": ["US West", "Los Angeles, CA, US", -7],
    "dal": ["USA", "Dallas, TX, US", -5],
    "kci": ["USA", "Kansas City, MO, US", -5],
    "vin": ["US East", "Vint Hill, VA, US", -4],
    "mtl": ["US East", "Montreal, CA", -4],
    "lon": ["Europe", "London, UK", 1],
    "fra": ["Europe", "Frankfurt, DE", 2],
    "fsn": ["Europe", "Falkenstein, DE", 2],
    "sgp": ["Asia", "Singapore", 8]
}

#============Game Code============

game_modes_map = {
    "2": [GameMode.TDM2, "2TDM", 2],
    "3": [GameMode.TDM3, "3TDM", 3],
    "4": [GameMode.TDM4, "4TDM", 4],
    "1": [GameMode.TDM1, "1TDM", 0],
    "f": [GameMode.FFA, "FFA", 0],
    "d": [GameMode.DUOS, "Duos", 0],
    "c": [GameMode.CLANWARS, "Clan Wars", 0]
}
def get_game_mode_int(game_mode):
    tuple = game_modes_map.get(game_mode, 0)
    return tuple[0]

def get_game_mode_name(game_mode):
    tuple = game_modes_map.get(game_mode, "Unknown")
    return tuple[1]

def get_game_mode_coded(game_mode):
    tuple = game_modes_map.get(game_mode, 0)
    return tuple[2]

game_modifiers_map = {
    "g": ["Growth", GameModifiers.GROWTH],
    "a": ["Arms Race", GameModifiers.ARMSRACE],
    "p": ["Portal", GameModifiers.PORTAL],
    "r": ["Rock", GameModifiers.ROCK],
    "m": ["Maze", GameModifiers.MAZE],
    "o": ["Open", GameModifiers.OPEN]
}
def get_game_modifier_name(game_mode):
    tuple = game_modifiers_map.get(game_mode, None)
    return tuple[0]

def get_game_modifier_flag(game_mode):
    tuple = game_modifiers_map.get(game_mode, None)
    return int(tuple[1])

game_varients_map = {
    "b": ["Soccer", ["2"]],
    "t": ["Tag", ["2","3","4","o"]],
    "d": ["Domination", []],
    "m": ["Mothership", ["2","4"]],
    "c": ["Capture The Flag", ["m", "2"]],
    "e": ["Elimination", ["o","m","4"]],
    "p": ["Pandemic", ["o"]],
    "g": ["Grudge Ball", ["m", "o"]],
    "a": ["Assault", ["m","2"]],
    "s": ["Siege", ["1"]]
}
def get_game_varient_name(game_mode):
    return game_varients_map.get(game_mode, "Unknown")[0]
def get_game_varient_ignore(game_mode):
    return game_varients_map.get(game_mode, [])[1]


def clear_servers():
    servers.clear()
    sandboxes.clear()

def load_status():
    if os.path.exists(constants.STATUS_FILE):
        with open(constants.STATUS_FILE, "r", encoding="utf-8") as f:
            raw_status = json.load(f)

    return raw_status["status"]

def sandbox_data_builder():
    sandbox = {
        "id": None,
        "region": None,
        "mspt": None,
        "clients": None,
        "server_code": None
    }
    return sandbox

def server_builder():
    server = {
        "id": None,
        "hidden": None,
        "region": None,
        "region_str": None,
        "host": None,
        "location": None,
        "mspt": None,
        "clients": None,
        "uptime": None,
        "server_code": "",
        "server_name": "",
        "coded": 0,
        "gamemodes": []
    }
    return server

#===================================================
def server_is_coded(id):
    for server in servers:
        if server.get("id", None) == id:
            return server.get("coded", 0)
    return 0

def fetch_status_then_parse():
    if fetch_status():
        if parse_status():
            return True
        
    return False
    #sort_servers() #I suspect this is causing issues

#===================================================
def sort_servers():
    global servers
    sort1 = sorted(servers, key = lambda id: id["id"][1]) #sort by the secord letter in the id
    sort2 = sorted(sort1, key = lambda region: region["region"]) #sort by region, US West, Europe, etc
    servers = sort2

    # with open("saved_servers.json", "w", encoding="utf-8") as f:
    #     json.dump(servers, f, indent=2, ensure_ascii=False)

def fetch_status():
    try:
        response = requests.get(constants.STATUS_URL, stream=True)
        response.raise_for_status()

        with open(constants.STATUS_FILE, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        #print(f"Fetched server status from arras.io successfully")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading status: {e}")
        pass

    except Exception as e:
        print(f"Unknown error fetching status: {e}")
        pass

    return False

def parse_status(): #FIXME: Siege maps with more than one word are a bit buggy
    raw_status = load_status()
    # pretty_status = json.dumps(raw_status, indent=4)
    # print(pretty_status)

    if not raw_status: #should never happen
        print("Unable to parse, raw_status does not exist!")
        return False
    
    clear_servers()
    
    for server_id in raw_status:
        server = raw_status[f"{server_id}"]
        if server.get("online", False) == True:
            name_string = server.get("name")
            #print(f"Parsing server {name_string}")
            code_string = server.get("code")
            if code_string[-1] == '%':
                #this server game mode is not set/unknown
                continue

            unlistable = False
            server_hidden = server.get("hidden", False)
            if not (code_string[-1] == 'z') and server_hidden:
                #this server is hidden and not a sandbox
                unlistable = True

            if name_string[1] == 'z': #sandbox nexuses
                server_hidden = True

            #We should have parsed out all sandboxes, offline, and unknown servers by now
            #Begin parsing the codes

            #wsi-kci-4, 4TDM, this code is Host-Region-Gamecode, this code splits that apart
            strip_code = code_string #using this so I can slice various parts off
            index = strip_code.index('-')
            host = strip_code[:index]
            location_strip = strip_code[(index+1):]
            index = location_strip.index('-')
            location = location_strip[:index]
            strip_code = location_strip[(index+1):]
            gamecode_str = strip_code

            if gamecode_str == "z":
                #this is a sandbox
                clients = server.get("clients")
                # if clients <= 0:
                #     #no point in storing sandboxes with no-one in them yet
                #     continue
                name_string = server.get("name")

                sandbox = sandbox_data_builder()
                sandbox["id"] = name_string
                sandbox["region"] = get_region_int(name_string)
                sandbox["region_str"] = get_region_name(name_string)
                sandbox["mspt"] = server.get("mspt", 0)
                sandbox["clients"] = clients
                sandbox["server_code"] = code_string
                sandboxes.append(sandbox)
                continue

            #aom4e, Arms Race Elimination, (Arms Race Open 4TDM Elimination), this code parses gamecodes, details in code_examples.txt
            if gamecode_str:
                full_game_str = ""
                game_mode_char = ""
                game_mode_char_index = -1
                e_index = -1
                game_mode_e = ""
                w_index = -1
                game_mode_w = ""
                game_modifiers_str = ""
                game_varients_str = ""
                game_varient_char = ""
                game_varients_ignore = []
                is_siege = False
                is_assault = False
                #Find the core game mode "4,2,c,f...", then divide into three parts
                game_slice_str = gamecode_str
                for index in range(len(game_slice_str)):
                    if game_slice_str[index] in game_modes_map:
                        game_mode_char = game_slice_str[index]
                        game_mode_char_index = index
                        #print(f"Game Mode found: {game_mode_char}")
                        break
                    if game_slice_str[index] == "e" and e_index < 0:
                        e_index = index
                        #print(f"e index found at {e_index}")
                        continue
                    if game_slice_str[index] == "w" and w_index < 0:
                        w_index = index
                        #print(f"w index found at {w_index}")
                        continue
                    else:
                        continue

                # if not game_mode_char:
                #     print("No game mode found, assuming e or w")
                if game_mode_char: #TODO: The proper way to parse siege x15 or whatever, as outlined in code_examples.txt
                    if game_mode_char == "1": #This is a siege server, most likely
                        if len(game_slice_str) > game_mode_char_index + 1:
                            if game_slice_str[game_mode_char_index+1] == "s": #Siege Server
                                is_siege = True
                    if game_mode_char == "2":
                        if len(game_slice_str) > game_mode_char_index + 1:
                            if game_slice_str[game_mode_char_index+1] == "a": #Assault Server
                                is_assault = True
                    is_coded = get_game_mode_coded(game_mode_char)
                    #Now split off the modifiers and varients
                    game_modifiers_str = game_slice_str[:game_mode_char_index]
                    game_varients_str = game_slice_str[(game_mode_char_index+1):]
                    #print(f"Game Modifiers: {game_modifiers_str}")
                    #print(f"Game Varients: {game_varients_str}")
                else:
                    is_coded = 0

                #Parse varient first to get the ignore vars and name
                if e_index >= 0:
                    #FIXME: This could cause some issues, but we are going to assume that if it's an e,
                    #Then there are no varients beyond that
                    game_varients_str = ""

                    game_mode_e_length = int(game_slice_str[(e_index+1)])
                    #print(f"e game mode found, {game_mode_e_length} chars long")
                    #e_full_string = game_slice_str[(e_index):(e_index+2+game_mode_e_length)]
                    game_mode_e = game_slice_str[(e_index+2):(e_index+2+game_mode_e_length)]
                    #print(f"e mode name: {game_mode_e.capitalize()}")
                elif w_index >= 0:
                    #FIXME: This could cause some issues, but we are going to assume that if it's a w,
                    #Then there are no varients beyond that
                    game_varients_str = ""

                    #FIXME: Hack until I figure out how w actually works
                    if game_slice_str[w_index:] == "w33oldscdreadnoughts":
                        game_mode_w = "Old Dreadnoughts"
                        #print(f"w mode found: Old Dreadnoughts")
                    if game_slice_str[w_index:] == "w33olds5forge":
                        game_mode_w = "Old Forge"
                        #print(f"w mode found: Old Forge")
                    if game_slice_str[w_index:] == "w33olds9labyrinth":
                        game_mode_w = "Old Labyrinth"
                elif game_varients_str:
                    for index in range(len(game_varients_str)):
                        if game_varients_str[index] in game_varients_map:
                            #FIXME: We can only have one game varient right?
                            game_varient_char = game_varients_str[index]
                            #print(f"Game varient found: {game_varient_char}")
                            game_varients_ignore = get_game_varient_ignore(game_varient_char)
                            #print(f"Game varients ignore: {game_varients_ignore}")

                #Parse the modifiers now
                game_modifiers = 0
                if game_modifiers_str:
                    skip_num = 0
                    for index in range(len(game_modifiers_str)):
                        if skip_num > 0:
                            skip_num -= 1
                            continue
                        if game_modifiers_str[index] in game_modifiers_map:
                            game_modifiers |= get_game_modifier_flag(game_modifiers_str[index])
                            #print(f"Found modifier for gamemode: {game_modifiers_str[index]}")
                            #print(f"Game Mod flag: {get_game_modifier_flag(game_modifiers_str[index])}")
                            #print(f"Game Mod name: {get_game_modifier_name(game_modifiers_str[index])}")
                            if game_modifiers_str[index] not in game_varients_ignore:
                                full_game_str += get_game_modifier_name(game_modifiers_str[index]) + " "
                            continue
                        if game_modifiers_str[index] == "e":
                            e_len = int(game_modifiers_str[index+1])
                            #print(f"Game modifiers, e len = {e_len}")
                            full_game_str += game_mode_e.capitalize() + " "
                            skip_num = e_len+1
                            continue
                
                if is_assault or is_siege:
                    map_name = game_slice_str[game_mode_char_index+5:].capitalize()
                    if is_assault:
                        full_game_str += "Assault " + map_name
                    if is_siege:
                        full_game_str += "Siege " + map_name
                else:
                    if game_mode_char and game_mode_char not in game_varients_ignore and e_index < 0 and w_index < 0:
                        full_game_str += get_game_mode_name(game_mode_char) + " "

                    if game_varient_char:
                        full_game_str += get_game_varient_name(game_varient_char)
                
                    if not full_game_str and game_mode_w:
                        full_game_str += game_mode_w

                    if not full_game_str and game_mode_e:
                        full_game_str += game_mode_e.capitalize()

                if full_game_str == "Labyrinth": #HAAAAACKZ
                    is_coded = 4

                #Parsing complete, save server
                saved_server = server_builder()
                saved_server["id"] = name_string
                saved_server["hidden"] = server_hidden
                saved_server["region"] = get_region_int(name_string[0])
                saved_server["region_str"] = get_region_name(name_string[0])
                saved_server["host"] = host
                saved_server["location"] = location
                saved_server["mspt"] = server.get("mspt", 0)
                saved_server["clients"] = server.get("clients")
                saved_server["uptime"] = server.get("uptime")
                saved_server["server_code"] = code_string
                saved_server["server_name"] = full_game_str
                if is_coded > 0 and not unlistable:
                    saved_server["coded"] = is_coded

                servers.append(saved_server)
                continue
        else:
            continue
    
    return True