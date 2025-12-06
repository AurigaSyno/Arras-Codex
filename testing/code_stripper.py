import sys
from enum import IntEnum
import re

# if __name__ == "__main__":
#     if len(sys.argv) > 1:
#         print(f"Hello, {sys.argv[1]}!")
#     else:
#         print("Hello, world!")

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
    CLANWARS = 5
    OLDD = 6
    OLDF = 7

class GameModifiers(IntEnum):
    NONE = 0
    GROWTH = 1
    ROCK = 2
    ARMSRACE = 4
    MAZE = 8
    OPEN = 16

game_modes_map = {
    "2": [GameMode.TDM2, "2TDM", 2],
    "3": [GameMode.TDM3, "3TDM", 3],
    "4": [GameMode.TDM4, "4TDM", 4],
    "1": [GameMode.TDM1, "1TDM", 0],
    "f": [GameMode.FFA, "FFA", 0],
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
    "r": ["Rock", GameModifiers.ROCK],
    "g": ["Growth", GameModifiers.GROWTH],
    "a": ["Arms Race", GameModifiers.ARMSRACE],
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
    "d": ["Domination"],
    "m": ["Mothership", ["2","4"]],
    "c": ["Capture The Flag", ["2"]],
    "e": ["Elimination", ["o","m","4"]],
    "a": ["Assault", ["m","2"]],
    "s": ["Siege", ["1"]]
}
def get_game_varient_name(game_mode):
    return game_varients_map.get(game_mode, "Unknown")[0]
def get_game_varient_ignore(game_mode):
    return game_varients_map.get(game_mode, [])[1]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        gamecode_str = sys.argv[1]
        # index = strip_code.index('-')
        # host = strip_code[:index]
        # location_strip = strip_code[(index+1):]
        # index = location_strip.index('-')
        # location = location_strip[:index]
        # strip_code = location_strip[(index+1):]
        # gamecode_str = strip_code

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
            if game_mode_char:
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
            
            print(f"{full_game_str}")
            print(f"Server coded: {is_coded}")
            #print(f"Unlistable: {}")