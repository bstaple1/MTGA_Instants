#!/usr/bin/env python3
"""! @brief Magic the Gathering draft application that utilizes 17Lands data"""


##
# @mainpage Magic Draft Application
#
# @section description_main Description
# A program that utilizes 17Lands data to dispay pick ratings, deck statistics, and deck suggestions
#
# @section notes_main Notes
# - 
#


##
# @file main.py
#
# @brief 
#
# @section Description
# A program that utilizes 17Lands data to dispay pick ratings, deck statistics, and deck suggestions
#
# @section libraries_main Libraries/Modules
# - tkinter standard library (https://docs.python.org/3/library/tkinter.html)
#   - Access to GUI functions.
# - pynput library (https://pypi.org/project/pynput)
#   - Access to the keypress monitoring function
# - urllib standard library (https://docs.python.org/3/library/urllib.html)
#   - Access to URL opening function.
# - json standard library (https://docs.python.org/3/library/json.html)
#   - Access to the json encoding and decoding functions
# - os standard library (https://docs.python.org/3/library/os.html)
#   - Access to the file system navigation functions.
# - time standard library (https://docs.python.org/3/library/time.html)
#   - Access to sleep function.
# - getopt standard library (https://docs.python.org/3/library/getopt.html)
#   - Access to the command line interface functions.
# - sys standard library (https://docs.python.org/3/library/sys.html)
#   - Access to the command line argument list.
# - io standard library (https://docs.python.org/3/library/io.html)
#   - Access to the command line argument list.
# - itertools standard library (https://docs.python.org/3/library/itertools.html)
#   - Access to the product function.
# - PIL library (https://pillow.readthedocs.io/en/stable/)
#   - Access to image manipulation modules.
# - file_extractor module (local)
#   - Access to the functions used for downloading the data sets.
# - card_logic module (local)
#   - Access to the functions used for processing the card data.
#
#
# @section Author(s)
# - Created by Bryan Stapleton on 12/27/2021

from tkinter import *
from tkinter.ttk import *
import tkinter
import json
import os
import time 
import getopt
import sys
import urllib.request
import io
import itertools
from tkinter.font import Font
from pynput.keyboard import Key, Listener, KeyCode
from urllib.parse import quote as urlencode

LOG_LOCATION_PC = "\\AppData\\LocalLow\\Wizards Of The Coast\\MTGA\\Player.log"
LOG_LOCATION_MAC = "/Library/Logs/Wizards of the Coast/MTGA/Player.log"


os_log_dict = {
    "MAC" : LOG_LOCATION_MAC,
    "PC"  : LOG_LOCATION_PC,
}

def ManaCount(mana_cost):
    cmc = 0
    mana_types = ["R","G","B","U","W"]
    
    numeric = [int(x) for x in mana_cost if x.isdigit()]
    if len(numeric) != 0:
        cmc += numeric[0]
        
    for type in mana_types:
        count = mana_cost.count(type)
        cmc += count
    
    return cmc

def ExtractTypes(type_line):
    types = []
    if "Creature" in type_line:
        types.append("Creature")
        
    if "Planeswalker" in type_line:
        types.append("Planeswalker")
        
    if "Land" in type_line:
        types.append("Land")
        
    if "Instant" in type_line:
        types.append("Instant")
        
    if "Sorcery" in type_line:
        types.append("Sorcery")
       
    if "Enchantment" in type_line:
        types.append("Enchantment")
        
    if "Artifact" in type_line:
        types.append("Artifact")

    return types

class DataPlatform:
    def __init__(self):
        self.sets = {}
        self.card_list = []
    def SessionCardData(self, set):
        cards = {}
        try:
            #https://api.scryfall.com/cards/search?order=set&q=e%3AKHM
            url = "https://api.scryfall.com/cards/search?order=set&q=e" + urlencode(':', safe='') + "%s" % (set)
            print(url)
            url_data = urllib.request.urlopen(url).read()
            
            set_json_data = json.loads(url_data)
            cards = self.ProcessCardData(set_json_data["data"], cards)
            
            while set_json_data["has_more"] == True:
                url = set_json_data["next_page"]
                url_data = urllib.request.urlopen(url).read()
                set_json_data = json.loads(url_data)
                cards = self.ProcessCardData(set_json_data["data"], cards)
                
                
        except Exception as error:
            print("SessionCardData Error: %s" % error)
        return cards
    def SessionSets(self):
        try:
            url = "https://api.scryfall.com/sets"
            url_data = urllib.request.urlopen(url).read()
            
            set_json_data = json.loads(url_data)
            self.ProcessSetData(set_json_data["data"])
            while set_json_data["has_more"] == True:
                url = set_json_data["next_page"]
                url_data = urllib.request.urlopen(url).read()
                set_json_data = json.loads(url_data)
                self.ProcessSetData(set_json_data["data"])
                
                
        except Exception as error:
            print("SessionCardData Error: %s" % error)
            
    def ProcessSetData (self, data):
        self.sets = {}
        counter = 0
        for set in data:
            try:
                set_name = set["name"]
                set_code = set["code"]
                
                if (len(set_code) == 3) and (set["set_type"] == "expansion"):
                    self.sets[set_name] = set_code
                    counter += 1
                    
                    # Only retrieve the last 10 sets
                    if counter >= 10:
                        break
            except Exception as error:
                print("ProcessSetData Error: %s" % error)
            
    def ProcessCardData (self, data, cards):
        
        for card_data in data:
            try:
                types = ExtractTypes(card_data["type_line"])
                if ("Instant" in types) or ("Flash" in card_data["keywords"]):
                    card = {}
                    name = card_data["name"]
                    card["cmc"] = card_data["cmc"]
                    card["name"] = card_data["name"]
                    card["colors"] = card_data["color_identity"]
                    card["types"] = types
                    card["image"] = []
                    card["keywords"] = card_data["keywords"]
                    card["text"] = card_data["oracle_text"]
                    
                    try:
                        if "card_faces" in card_data.keys():
                            card["mana_cost"] = card_data["card_faces"][0]["mana_cost"]
                            card["image"].append(card_data["card_faces"][0]["image_uris"]["normal"])
                            card["image"].append(card_data["card_faces"][1]["image_uris"]["normal"])
                            
                        else:
                            card["mana_cost"] = card_data["mana_cost"]
                            card["image"] = [card_data["image_uris"]["normal"]]
                    except Exception as error:
                        print(error)
                        card["mana_cost"] = "0"
                        card["image"] = []
                    print("%s, %s" % (card["name"], card["mana_cost"]))
                    if name not in cards.keys():
                        card[name] = {}
                        cards[name] = card
                
                
            except Exception as error:
                print("ProcessCardData Error: %s" % error)
        return cards
def KeyListener(window_ui):
    Listener(on_press=lambda event: OnPress(event, ui=window_ui)).start()

def OnPress(key, ui):
    if key == KeyCode.from_char('\x06'): #CTRL+F
        ui.WindowLift()
        
def NavigateFileLocation(os_type):
    file_location = ""
    try:
        computer_root = os.path.abspath(os.sep);
        
        for root, dirs, files in os.walk(computer_root):
            for path in root:
                try:
                    user_directory = path + "Users/"
                    for directories in os.walk(user_directory):
                        users = directories[1]
                        
                        for user in users:
                            file_path = user_directory + user + os_log_dict[os_type]
                            
                            print("File Path: %s" % file_path)
                            try:
                                if os.path.exists(file_path):
                                    file_location = file_path
                            except Exception as error:
                                print(error)
                        break
                    
                except Exception as error:
                    print (error)
            break
    except Exception as error:
        print("NavigateFileLocation Error: %s" % error)
    return file_location
    

def FixedMap(style, option):
    # Returns the style map for 'option' with any styles starting with
    # ("!disabled", "!selected", ...) filtered out

    # style.map() returns an empty list for missing options, so this should
    # be future-safe
    return [elm for elm in style.map("Treeview", query_opt=option)
            if elm[:2] != ("!disabled", "!selected")]
                 

                 
def RowColorTag(colors):
    row_tag = "goldcard"
    
    if len(colors) > 1:
        row_tag = "goldcard"
    elif "R" in colors:
        row_tag = "redcard"
    elif "U" in colors:
        row_tag = "bluecard"
    elif "B" in colors:
        row_tag = "blackcard"
    elif "W" in colors:
        row_tag = "whitecard"
    elif "G" in colors:
        row_tag = "greencard"
    return row_tag       

def ReadConfig():
    hotkey_enabled = False
    images_enabled = False
    table_width = 225
    try:
        with open("config.json", 'r') as config:
            config_json = config.read()
            config_data = json.loads(config_json)
        hotkey_enabled = config_data["features"]["hotkey_enabled"]
        images_enabled = config_data["features"]["images_enabled"]
        table_width = int(config_data["settings"]["table_width"])
    except Exception as error:
        print("ReadConfig Error: %s" % error)
    return hotkey_enabled, images_enabled, table_width


def LogEntry(log_name, entry_text, diag_log_enabled):
    if diag_log_enabled:
        try:
            with open(log_name, "a") as log_file:
                log_file.write("<%s>%s\n" % (time.strftime('%X %x'), entry_text))
        except Exception as error:
            print("LogEntry Error:  %s" % error)    
                 
class LogScanner:
    def __init__(self, log_file, os):
        self.os = os
        self.log_file = log_file
        self.offset = 0
        self.total_lands = {}
        self.tapped_lands = []
        self.land_permutations = []
        self.diag_enabled = False
        self.previous_turn = 1
        self.user_offset = 0
        self.user_name = ""
        self.seat_offset = 0
        self.opponent_seat = 0
        self.diag_log_file = "Instants_Log_%u.log" % (int(time.time()))
        self.IdentifyPlayerSeat()
        self.LandSearch()

    def IdentifyPlayerSeat(self):
        search_string_user = "[Accounts - Login] Logged in successfully. Display Name: "
        search_string_seat = "playerName"

        with open(self.log_file, 'r', errors="ignore") as log:
            #Identify user's name 
            log.seek(self.user_offset)
            for line in log:
                self.user_offset += len(line)
                
                string_offset = line.find(search_string_user)
                if string_offset != -1:
                    string_offset += len(search_string_user)
                    self.user_name = line[string_offset:-1]

            #Identify opponent's seat
            log.seek(self.seat_offset)
            for line in log:
                self.seat_offset += len(line)

                string_offset = line.find(search_string_seat)
                if string_offset != -1:
                    event_data = json.loads(line)
                    players = event_data["matchGameRoomStateChangedEvent"]["gameRoomInfo"]["gameRoomConfig"]["reservedPlayers"]
                    for player in players:
                        if player["playerName"] != self.user_name:
                            self.opponent_seat = player["systemSeatId"]

            print("Opponent's Seat: %u" % self.opponent_seat)

    def LandSearch(self):
        land_permutations = self.land_permutations
        offset = self.offset
        game_state_id = 0
        search_string = "gameObjects"
        with open(self.log_file, 'r', errors="ignore") as log:
            log.seek(offset)
            for line in log:
                try:
                    offset += len(line)
                    
                    string_offset = line.find(search_string)
                    if string_offset != -1:
                        self.offset = offset
                        
                        event_data = json.loads(line)
                        gre_to_client = event_data["greToClientEvent"]
                        for message in gre_to_client["greToClientMessages"]:
                            try:
                                turn_info = message["gameStateMessage"]["turnInfo"]
                                current_turn = turn_info["turnNumber"]
                                active_player = turn_info["activePlayer"]
                                if (current_turn != self.previous_turn):
                                    if (current_turn > self.previous_turn) and (active_player == self.opponent_seat):
                                        self.tapped_lands = []
                                    elif current_turn < self.previous_turn:
                                        self.tapped_lands = []
                                        self.land_permutation = []
                                        self.total_lands = {}
                    
                                log_string = "Current turn: %d, previous turn: %d, active player: %d" % (current_turn, self.previous_turn, active_player)
                                LogEntry(self.diag_log_file, log_string, self.diag_enabled)
                                self.previous_turn = current_turn
                            except Exception as error:
                                print(error)
                                
                            try:
                                game_objects = message["gameStateMessage"]["gameObjects"]
                                
                                found_flag = False
                                for object in game_objects:
                                    self.LandParse(object)
                                permutations = []
                                types = []
                                #identify the types
                                for land_id, land_types in self.total_lands.items():
                                    if land_id not in self.tapped_lands:
                                        types.append(land_types)
                                
                                
                                #identify the permutations
                                permutations = list(itertools.product(*types))
                   
                                self.land_permutations = permutations
                                #print(lands)
                            except Exception as error:
                                print(error)


                except Exception as error:
                    print("LandSearch Error: %s" % error)
                    LogEntry(self.diag_log_file, line, self.diag_enabled)
        return land_permutations
        
        
        
    def LandParse(self, game_object):
        land_subtypes = {"SubType_Forest" : "G", "SubType_Swamp" : "B", "SubType_Island" : "U", "SubType_Mountain" : "R", "SubType_Plains" : "W"}
        LogEntry(self.diag_log_file, str(game_object), self.diag_enabled)
        try:
            if (game_object["ownerSeatId"] == self.opponent_seat) and (game_object["visibility"] == "Visibility_Public"):
                instance_id = game_object["instanceId"]
                if "CardType_Land" in game_object["cardTypes"]:
                    #Generic lands with no color mana
                    if "subtypes" not in game_object.keys():
                        if "isTapped" not in game_object.keys():
                            if instance_id not in self.total_lands.keys():
                                self.total_lands[instance_id] = []
                                
                            if "NC" not in self.total_lands[instance_id]:
                                self.total_lands[instance_id].append("NC")
                        else:
                            if instance_id in self.total_lands.keys():
                                self.tapped_lands.append(instance_id)
                    else:
                        print("subtypes: %s" %(str(game_object["subtypes"])))
                        for subtype in game_object["subtypes"]:
                            if subtype in land_subtypes.keys():
                                if "isTapped" not in game_object.keys():
                                    if instance_id not in self.total_lands.keys():
                                        self.total_lands[instance_id] = []
                                        
                                    if land_subtypes[subtype] not in self.total_lands[instance_id]:
                                        self.total_lands[instance_id].append(land_subtypes[subtype])
                                else:
                                    if instance_id in self.total_lands.keys():
                                        self.tapped_lands.append(instance_id)

        except Exception as error:
            LogEntry(self.diag_log_file, error, self.diag_enabled)
            print(error)
class WindowUI:
    def __init__(self, root, filename, os, images, table_width):
        self.root = root
        self.elevated = False
        Grid.rowconfigure(self.root, 4, weight = 1)
        
        self.filename = filename
        self.os = os
        self.player_log = LogScanner(self.filename, self.os)
        self.previous_timestamp = 0
        self.previous_permutations = {}
        self.previous_set = ""
        
        style = Style()
        style.map("Treeview", 
                foreground=FixedMap(style, "foreground"),
                background=FixedMap(style, "background"))
        
        self.set_data = DataPlatform()
        self.set_data.SessionSets()
        
        self.set_label = Label(self.root, text="Set:", font='Consolas 10 bold', anchor="w")
        
        self.set_options_selection = StringVar(self.root)
        self.set_options_list = []
        self.set_options_selection.trace("w", self.UpdateCallback)
        
        optionsStyle = Style()
        optionsStyle.configure('my.TMenubutton', font=('Consolas', 10))
        
        self.set_options = OptionMenu(self.root, self.set_options_selection, *self.set_options_list, style="my.TMenubutton")
        
        self.total_mana_label = Label(self.root, text="Total Mana:", font='Consolas 10 bold', anchor="e")
        self.total_mana_value = StringVar()
        self.total_mana_value.set("")
        self.total_mana_value_label = Label(self.root, textvariable=self.total_mana_value, font='Consolas 10', anchor="w")
        
        self.mana_colors_label = Label(self.root, text="Mana Colors:", font='Consolas 10 bold', anchor="e")
        self.mana_colors_value = StringVar()
        self.mana_colors_value_label = Label(self.root, textvariable=self.mana_colors_value, font='Consolas 10', anchor="w")
        
        self.refresh_button_frame = Frame(self.root)
        self.update_button = Button(self.refresh_button_frame, command=self.UpdateCallback, text="REFRESH");
        
        
        self.instants_table_frame = Frame(self.root)
        
        headers = {"Card"  : {"width" : .70, "anchor" : W},
                   "Cost"  : {"width" : .30, "anchor" : CENTER}}
        
        self.instants_table = self.CreateHeader(self.instants_table_frame, 0, headers, table_width)
        
        self.set_label.grid(row = 0, column = 0, columnspan = 1, sticky = 'e')
        self.set_options.grid(row = 0, column = 1, columnspan = 1, sticky = 'w')
        self.total_mana_label.grid(row = 1, column = 0, columnspan = 1, sticky = 'e')
        self.total_mana_value_label.grid(row = 1, column = 1, columnspan = 1, sticky = 'w')
        self.mana_colors_label.grid(row = 2, column = 0, columnspan = 1, sticky = 'e')
        self.mana_colors_value_label.grid(row = 2, column = 1, columnspan = 1, sticky = 'w')
        self.refresh_button_frame.grid(row = 3, column = 0, columnspan = 2, stick = 'nsew')
        self.instants_table_frame.grid(row = 4, column = 0, columnspan = 2, sticky = 'nsew')
        self.instants_table_frame.grid_rowconfigure(0, weight=1)
        
        self.update_button.pack(expand = True, fill = "both")
        
        self.instants_table.pack(expand = True, fill = 'both', anchor = "n")          
        
        self.UpdateCallback()
        self.UpdateUI()
        
        self.root.attributes("-topmost", True)
        
    def CreateHeader(self, frame, height, headers, total_width):
        header_labels = tuple(headers.keys())
        list_box = Treeview(frame, columns = header_labels, show = 'headings')
        list_box.config(height=height)
        style = Style() 
        style.configure("Treeview.Heading", font=("Arial", 8))
        try:
            list_box.tag_configure("darkgrey", background="#808080")
            list_box.tag_configure("custombold", font=("Arial Bold", 8))
            list_box.tag_configure("customfont", font=("Arial", 8))
            list_box.tag_configure("whitecard", font=("Arial", 8, "bold"), background = "#FFFFFF", foreground = "#000000")
            list_box.tag_configure("redcard", font=("Arial", 8, "bold"), background = "#FF6C6C", foreground = "#000000")
            list_box.tag_configure("bluecard", font=("Arial", 8, "bold"), background = "#6078F3", foreground = "#000000")
            list_box.tag_configure("blackcard", font=("Arial", 8, "bold"), background = "#BFBFBF", foreground = "#000000")
            list_box.tag_configure("greencard", font=("Arial", 8, "bold"), background = "#60DC68", foreground = "#000000")
            list_box.tag_configure("goldcard", font=("Arial", 8, "bold"), background = "#F0E657", foreground = "#000000")
            for count, column in enumerate(header_labels):
                list_box.column(column, stretch = NO, anchor = headers[column]["anchor"], width = int(headers[column]["width"] * total_width))
                list_box.heading(column, text = column, anchor = CENTER)
            list_box["show"] = "headings"  # use after setting column's size
        except Exception as error:
            error_string = "CreateHeader Error: %s" % error
            print(error_string)
        return list_box
        
    def UpdateOptions(self, options_list):
        try: 
            
            menu = self.set_options["menu"]
            menu.delete(0, "end")
            self.set_options_list = []
            for key, data in options_list.items():
                if len(data):
                    data = data.upper()
                    menu.add_command(label=data, 
                                    command=lambda value=data: self.set_options_selection.set(value))
                    self.set_options_list.append(data)
              
            if len(self.set_options_list):        
                selected_option = next(iter(self.set_options_list))
                self.set_options_selection.set(selected_option)
        except Exception as error:
            print("UpdateOptions Error: %s" % error) 
            
    def UpdateCallback(self, *args):
        self.player_log.IdentifyPlayerSeat()
        land_permutations = self.player_log.LandSearch()
        
        if len(self.set_options_list) == 0:
           self.UpdateOptions(self.set_data.sets)
        self.UpdateInstants(land_permutations)
        
    def ClearCallback(self, *args):
        self.UpdateInstants()
         
    def UpdateInstants(self, land_permutations):
        try:
            current_set = self.set_options_selection.get()
            
            if (land_permutations != self.previous_permutations) or (current_set != self.previous_set):
                self.total_mana_value.set(len(land_permutations[0]))
                
                total_colors = [i for sub in land_permutations for i in sub]
                unique_colors = ",".join(list(dict.fromkeys(total_colors)))
                self.mana_colors_value.set(unique_colors)
            
                cards = self.set_data.SessionCardData(current_set)
                    
                self.UpdateInstantsTable(cards, land_permutations)
                self.previous_permutations = land_permutations
                self.previous_set = current_set
        except Exception as error:
            print("UpdateInstants Error: %s" % error)
            
    def UpdateInstantsTable(self, card_list, land_permutations):
        try:
            for row in self.instants_table.get_children():
                self.instants_table.delete(row)
            self.root.update()
            filtered_dict = self.CardCostFilter(card_list, land_permutations)
            sorted_dict = dict(sorted(filtered_dict.items(), key=lambda x: x[1]['cmc'], reverse=True))
            
            list_length = len(sorted_dict)
            
            if list_length:
                self.instants_table.config(height = list_length)
            else:
                self.instants_table.config(height=1)
            
            for count, card in enumerate(sorted_dict):
                row_tag = RowColorTag(sorted_dict[card]["colors"])
                
                self.instants_table.insert("",index = count, iid = count, values = (card, sorted_dict[card]["mana_cost"]), tag = row_tag)
            self.instants_table.bind("<<TreeviewSelect>>", lambda event: self.OnClickTable(event, table=self.instants_table, card_list=card_list))

        except Exception as error:
            print("UpdateInstantsTable Error: %s" % error) 
            
    def CardForetellCost(self, card):
        mana_cost = ""
        cmc = 0
        try:
            if "Foretell" in card["keywords"]:
                #scan the text for the foretell cost
                search_string = "Foretell {"
                index = card["text"].find(search_string)
                if index != -1:
                    sections = card["text"][(index + len(search_string) - 1):].split(" ")
                    
                    mana_cost = sections[0]
                    
                    cmc = ManaCount(mana_cost)
        except Exception as error:
            print("CardForetellCost Error: %s" % error)
        return mana_cost, cmc
            
    def CardCostFilter(self, card_list, land_permutations):
        filter_dict = {}
        
        for permutation in land_permutations:
            try:
                red_mana = 0
                black_mana = 0
                blue_mana = 0
                white_mana = 0
                green_mana = 0
                colorless_mana = 0
                
                for land in permutation:
                    if land == "R":
                        red_mana += 1
                    elif land == "B":
                        black_mana += 1
                    elif land == "U":
                        blue_mana += 1
                    elif land == "W":
                        white_mana += 1
                    elif land == "G":
                        green_mana += 1
                    elif land == "NC":
                        colorless_mana += 1
                total_mana = red_mana + black_mana + blue_mana + white_mana + green_mana + colorless_mana
                
                
                for card in card_list:
                    #print("Card:%s, cmc: %s, mana_cost: %s" % (card, card_list[card]["cmc"], card_list[card]["mana_cost"]))
                    conditions_met = True
                    mana_cost = card_list[card]["mana_cost"]
                    cmc = card_list[card]["cmc"]
                    foretell_mana, foretell_cmc = self.CardForetellCost(card_list[card])
                    if foretell_mana != "":
                        mana_cost = foretell_mana
                        cmc = foretell_cmc
                    while(True):
                        
                        if (cmc <= total_mana):
                            if ("R" in mana_cost):
                                if(mana_cost.count("R") > red_mana):
                                    conditions_met = False
                                    break
                                    
                            if ("B" in mana_cost):
                                if(mana_cost.count("B") > black_mana):
                                    conditions_met = False
                                    break
                                    
                            if ("U" in mana_cost):
                                if(mana_cost.count("U") > blue_mana):
                                    conditions_met = False
                                    break
    
                            if ("G" in mana_cost):
                                if(mana_cost.count("G") > green_mana):
                                    conditions_met = False
                                    break
    
                            if ("W" in mana_cost):
                                if(mana_cost.count("W") > white_mana):
                                    conditions_met = False
                                    break                                
                        else:
                            conditions_met = False
                        break
                    
                    if(conditions_met):
                        filter_dict[card] = card_list[card]
            
            except Exception as error:
                print("CardCostFilter Error: %s" % error)
        return filter_dict
        
    def WindowLift(self):
        if self.elevated == False:
            self.elevated = True
            self.root.deiconify()
            self.root.lift()
            self.root.attributes("-topmost", True)
        else:
            self.elevated = False
            self.root.attributes("-topmost", False)
            #self.root.lower()
            self.root.iconify()
            
    def OnClickTable(self, event, table, card_list):
        for item in table.selection():
            card_name = table.item(item, "value")[0]
            for name, card in card_list.items():
                if card_name == name:
                    try:
                        tooltip = CreateCardToolTip(table, event,
                                                           card["image"],
                                                           True,
                                                           self.os)
                    except Exception as error:
                        tooltip = CreateCardToolTip(table, event,
                                                           card["image"],
                                                           True,
                                                           self.os)
                    break
                    
    def UpdateUI(self):
        try:
            self.current_timestamp = os.stat(self.filename).st_mtime
            
            if self.current_timestamp != self.previous_timestamp:
                self.previous_timestamp = self.current_timestamp
                
                self.UpdateCallback()
        except Exception as error:
            error_string = "UpdateUI Error: %s" % error
            print(error_string)
            
        self.root.after(500, self.UpdateUI)
class CreateCardToolTip(object):
    def __init__(self, widget, event, image, images_enabled, os):
        self.waittime = 1     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.image = image
        self.os = os
        self.images_enabled = images_enabled
        self.widget.bind("<Leave>", self.Leave)
        self.widget.bind("<ButtonPress>", self.Leave)
        self.id = None
        self.tw = None
        self.event = event
        self.images = []
        self.Enter()
       
    def Enter(self, event=None):
        self.Schedule()

    def Leave(self, event=None):
        self.Unschedule()
        self.HideTip()

    def Schedule(self):
        self.Unschedule()
        self.id = self.widget.after(self.waittime, self.ShowTip)

    def Unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def ShowTip(self, event=None):  
        try:
            x = y = 0
            x = self.widget.winfo_pointerx() + 25
            y = self.widget.winfo_pointery() + 20
            # creates a toplevel window
            self.tw = Toplevel(self.widget)
            # Leaves only the label and removes the app window
            self.tw.wm_overrideredirect(True)
            if self.os == "MAC":
               self.tw.wm_overrideredirect(False) 
            self.tw.wm_geometry("+%d+%d" % (x, y))
   
            tt_frame = Frame(self.tw)
            
            #Add scryfall image
            if self.images_enabled:
                from PIL import Image, ImageTk
                size = 260, 362
                
                self.images = []
                for count, picture in enumerate(self.image):
                    raw_data = urllib.request.urlopen(picture).read()
                    im = Image.open(io.BytesIO(raw_data))
                    im.thumbnail(size, Image.ANTIALIAS)
                    image = ImageTk.PhotoImage(im)
                    image_label = Label(tt_frame, image=image, background="red")
                    columnspan = 1 if len(self.image) == 2 else 2
                    image_label.grid(column=count, row=4, columnspan=columnspan)
                    self.images.append(image)

            tt_frame.pack()
           
            self.tw.attributes("-topmost", True)
            self.tw.attributes("-transparentcolor", "red")
        except Exception as error:
            print("Showtip Error: %s" % error)

    def HideTip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()            
        
def main(argv):
    version = 1.00
    file_location = ""
    step_through = False
    diag_log_enabled = True
    os = "PC"
    try:
        opts, args = getopt.getopt(argv, "f:",["step","disablediag","os="])
    except Exception as error:
        print(error)
        
    try:
        for opt, arg in opts:
            if opt in "-f":
                file_location = arg
            elif opt in "--step":
                step_through = True
            elif opt in "--disablediag":
                diag_log_enabled = False
            elif opt in "--os=":
                            os = arg      
    except Exception as error:
        print(error)
       
    if file_location == "":
        file_location = NavigateFileLocation(os);
    
    window = Tk()
    window.title("Magic Instants %.2f" % version)
    window.resizable(width = True, height = True)
    
    hotkey, images, table_width = ReadConfig()
    
    ui = WindowUI(window, file_location, os, images, table_width)
    
    if hotkey:
        KeyListener(ui)
    
    window.mainloop()
    
if __name__ == "__main__":
    main(sys.argv[1:])
    