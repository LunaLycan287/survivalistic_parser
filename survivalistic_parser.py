import os
import json5
import json
from tkinter.filedialog import askdirectory

##########
# CONFIG #
##########

# How much thirst you recover from drinkable items
DRINKABLE_THIRST_RECOVERY = 60

# Cooked food base thirst recovery
COOKED_THIRST_RECOVERY = 10

# Cooked Foods that count as watery and give extra thirst recovery
WATERY_FOODS = ['Stew', 'Soup', 'Gumbo', 'Broth', 'Ramen']

# Watery cooked food thirst recover
COOKED_WATERY_THIRST_RECOVERY = 30

# List of keywords to count as potion
POTIONS = ['Potion', 'Elixir', 'Tincture', 'Concoction']

# Potion thirst recovery fixed value
POTION_THIRST_RECOVERY = 75

# How much console output you see (Possible values "VERBOSE", "DEBUG", "INFO")
LOG_LEVEL = "INFO"

##########################
# DO NOT EDIT BELOW HERE #
##########################

INFO = "INFO"
DEBUG = "DEBUG"
VERBOSE = "VERBOSE"
OUT = "./output"
JA_MOD_ID = "spacechase0.JsonAssets"


def log_lvl_to_int(lvl):
    if lvl == VERBOSE:
        return 5
    elif lvl == INFO:
        return 1
    else:  # DEBUG
        return 3


def log(msg, lvl, end=os.linesep, show_lvl=True):
    if log_lvl_to_int(lvl) <= log_lvl_to_int(LOG_LEVEL):
        if show_lvl:
            if isinstance(msg, str):
                msg = '[' + lvl + ']: ' + msg
            else:
                print('[' + lvl + ']: ', end='')
        print(msg, end=end)


def list_mod_folders(path):
    log("Checking all mod folders, this can take some time.", INFO)
    dir_list = list()
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            if name.lower() == 'manifest.json':
                with open(os.path.join(root, name), 'r', encoding='utf-8') as infile:
                    data = json5.load(infile)
                    mod_id = data.get('UniqueID')

                    log('Checking ' + mod_id + '...', DEBUG, end=' ')
                    valid = False
                    if data.get('ContentPackFor', {}).get('UniqueID') == JA_MOD_ID:
                        valid = True
                    else:
                        dependencies = data.get('Dependencies')
                        if not (dependencies is None):
                            for dep in dependencies:
                                if dep.get('UniqueID') == JA_MOD_ID:
                                    valid = True
                                    break

                    if valid:
                        log('IS JsonAssets', DEBUG, show_lvl=False)
                        dir_list.append({
                            'id': mod_id,
                            'path': root,
                            'name': os.path.basename(os.path.normpath(root))
                        })
                    else:
                        log('is NOT JsonAssets', DEBUG, show_lvl=False)
    return dir_list


def get_object_list(path):
    obj_list = list()
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            if name.lower() == "object.json":
                obj_list.append(os.path.join(root, name))
    return obj_list


def get_entries(obj_list):
    entries = list()
    for objFile in obj_list:
        log('    File: ' + objFile, DEBUG)
        infile = open(objFile, 'r', encoding='utf-8')
        jdata = json5.load(infile)

        name = jdata.get('Name')

        edibility = jdata.get('Edibility')
        # According to the JA docs in edible items can be set to -300
        # https://github.com/spacechase0/StardewValleyMods/blob/develop/JsonAssets/docs/author-guide.md#objects
        if edibility != -300:
            food_value = 0
            if not (edibility is None):
                food_value = max(-100, min(edibility, 100))

            drink_value = 0
            if any(word in name for word in POTIONS):
                drink_value = POTION_THIRST_RECOVERY
            elif jdata.get('EdibleIsDrink') is True:
                drink_value = DRINKABLE_THIRST_RECOVERY
            else:
                if jdata.get('Category') == 'Cooking':
                    if any(word in name for word in WATERY_FOODS):
                        drink_value = COOKED_WATERY_THIRST_RECOVERY
                    else:
                        drink_value = COOKED_THIRST_RECOVERY
            if food_value != 0 or drink_value != 0:
                log('Adding: "' + name + '" with ' + str(food_value) + ' food and ' + str(drink_value) + ' water', VERBOSE)
                entries.append([name, str(food_value) + '/' + str(drink_value)])

        infile.close()
    return entries


if __name__ == '__main__':
    if not os.path.exists(OUT):
        os.mkdir(OUT)

    in_folder = askdirectory(title='Select Input Folder')

    mod_info_list = list_mod_folders(in_folder)
    for mod_info in mod_info_list:
        log('Working on: ' + mod_info.get('name'), INFO)

        ja_obj_list = get_object_list(mod_info.get('path'))

        db_entries = get_entries(ja_obj_list)

        if db_entries:
            out_name = mod_info.get('id') + '_edibles.json'
            with open(os.path.join(OUT, out_name), 'w+') as outfile:
                log(db_entries, VERBOSE)
                out_data = {
                    "edibles": db_entries
                }
                json.dump(out_data, outfile, indent=4)
            log("Finished creating: " + out_name, INFO, end=os.linesep+os.linesep)
        else:
            log("Did not create for " + mod_info.get('id') + " no food items found.", INFO, end=os.linesep+os.linesep)

    input("Press Enter to continue...")