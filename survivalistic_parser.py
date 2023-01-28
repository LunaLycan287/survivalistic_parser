import os
import json5
import json
from tkinter.filedialog import askdirectory

from constants import *
from config import *

OUT = "./output"
JA_MOD_ID = "spacechase0.JsonAssets"

HUNGER_MAX_CLAMPED = min(HUNGER_MAX, HUNGER_CLAMP_UPPER)
HUNGER_MIN_CLAMPED = max(HUNGER_MIN, HUNGER_CLAMP_LOWER)


def log_lvl_to_string(lvl):
    if lvl == VERBOSE:
        return "VERBOSE"
    elif lvl == INFO:
        return "INFO"
    else:  # DEBUG
        return "DEBUG"


def log(msg, lvl, end=os.linesep, show_lvl=True):
    if lvl <= LOG_LEVEL:
        if show_lvl:
            if isinstance(msg, str):
                msg = '[' + log_lvl_to_string(lvl) + ']: ' + msg
            else:
                print('[' + log_lvl_to_string(lvl) + ']: ', end='')
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


def get_clamped_food(value):
    return max(HUNGER_MIN_CLAMPED, min(value, HUNGER_MAX_CLAMPED))


def get_food_value(edible_value):
    food_value = 0
    if not (edible_value is None):
        food_value = get_clamped_food(edible_value)

        food_value2 = food_value
        if food_value2 > 0:
            food_value2 += HUNGER_POSITIVE_MODIFIER
            if food_value2 > 0:
                food_value = get_clamped_food(food_value2)
        elif food_value2 < 0:
            food_value2 += HUNGER_NEGATIVE_MODIFIER
            if food_value2 < 0:
                food_value = get_clamped_food(food_value2)

    return food_value


def get_drink_value(name, jdata):
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
    return drink_value


def get_entries(obj_list):
    entries = list()
    for objFile in obj_list:
        log('    File: ' + objFile, DEBUG)
        infile = open(objFile, 'r', encoding='utf-8')
        jdata = json5.load(infile)

        edibility = jdata.get('Edibility')
        # According to the JA docs in edible items can be set to -300
        # https://github.com/spacechase0/StardewValleyMods/blob/develop/JsonAssets/docs/author-guide.md#objects
        if edibility != -300:
            name = jdata.get('Name')

            food_value = get_food_value(edibility)

            drink_value = get_drink_value(name, jdata)

            if food_value != 0 or drink_value != 0:
                log('Adding: "' + name + '" with ' + str(food_value) + ' food and ' + str(drink_value) + ' water',
                    VERBOSE)
                entries.append([name, str(food_value) + '/' + str(drink_value)])

        infile.close()
    return entries


if __name__ == '__main__':
    # create output_adjusted dir if it does not exist
    if not os.path.exists(OUT):
        os.mkdir(OUT)

    # let user select input folder
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
            log("Finished creating: " + out_name, INFO, end=os.linesep + os.linesep)
        else:
            log("Did not create for " + mod_info.get('id') + " no food items found.", INFO, end=os.linesep + os.linesep)

    input("Press Enter to continue...")
