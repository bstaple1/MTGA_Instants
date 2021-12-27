# MTGA_Instants
A Magic: The Gathering Arena tool that monitors your opponent's lands and displays instant speed spells that they could play

## Steps for Windows

- Step 1: In Arena, go to Adjust Options, Account, and then check the Detailed Logs (Plugin Support) check box

- Step 2: Double-click the tool executable (.exe) to start the application.

- Step 3: Start the match in Arena.

## Steps for Mac

- Step 1: In Arena, go to Adjust Options, Account, and then check the Detailed Logs (Plugin Support) check box.

- Step 2: Download and install the latest version of python 3 from this location: https://www.python.org/downloads/macos/.

- Step 3: Install the python package installer Pip by opening the Mac terminal and entering "python3.10 -m ensurepip --upgrade".

- Step 4: Install the python image library Pillow by opening the Mac terminal and entering "python3.10 -m pip install --upgrade Pillow".

- Step 5: Install web certificates by going to "/Applications/Python 3.10/" and double-clicking the file "Install Certificates.command".

- Step 6: Open the config.json file in a text editor and change the "hotkey_enabled" field from "true" to "false".

- Step 7: Start the application by opening the Mac terminal and entering "python3.10 main.py --os=MAC" without quotes

- Step 8: Start the match in Arena.

## UI Features

- Set: Drop-down listing the ten most recent expansion sets.

- Total Mana: Opponent's total open mana.

- Mana Colors: Color of your opponent's open mana.

- Card Table: Lists the instant speed spells that your opponent can play.
  - Clicking on the table will display the card images.
