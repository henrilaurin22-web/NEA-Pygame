import pygame, pygame_menu, json, subprocess, math
from pygame_menu import themes

import pygame_menu.widgets

pygame.init()
surface = pygame.display.set_mode((600,400))

SettingsConfirmed = False

PEOPLE = 10
GWIDTH = 20
GHEIGHT = 20
GSPEED = 1
MLEVELS = 6

def startgame():
    print("Game started")
def options():
    print("Options opened")
    mainmenu._open(optionsmenu)

def ConfirmClick():
    global SettingsConfirmed
    SettingsConfirmed = True

def StorePeople(Value):
    global PEOPLE
    PEOPLE = math.floor(Value)
def StoreWidth(Value):
    global GWIDTH
    GWIDTH = math.floor(Value)
def StoreHeight(Value):
    global GHEIGHT
    GHEIGHT = math.floor(Value)
def StoreSpeed(Value):
    global GSPEED
    GSPEED = (Value)
def StoreMaxLevels(Value):
    global MLEVELS
    MLEVELS = math.floor(Value)

mainmenu = pygame_menu.Menu("Menu", 600, 400, theme=themes.THEME_BLUE)
mainmenu.add.button("Play", options)
mainmenu.add.button("Quit", pygame_menu.events.EXIT)

optionsmenu = pygame_menu.Menu("Options", 600, 400, theme=themes.THEME_BLUE)
optionsmenu.add.range_slider(title="Grid width",
    default=GWIDTH,              # Initial value
    range_values=(int(0), int(50)),   # Min and max values
    increment=1, onchange=StoreWidth)
optionsmenu.add.range_slider(title="Grid Height",
    default=GHEIGHT,              # Initial value
    range_values=(int(0), int(50)),   # Min and max values
    increment=1, onchange=StoreHeight)
#optionsmenu.add.range_slider(title="Amount of people",
    #default=PEOPLE,              # Initial value
    #range_values=(int(0), int(50)),   # Min and max values
    #increment=1, onchange=StorePeople)
optionsmenu.add.range_slider(title="Game speed",
    default=GSPEED,              # Initial value
    range_values=(int(0), int(5)),   # Min and max values
    increment=0.1, onchange=StoreSpeed)
optionsmenu.add.range_slider(title="Amount of levels",
    default=MLEVELS,              # Initial value
    range_values=(int(0), int(10)),   # Min and max values
    increment=1, onchange=StoreMaxLevels)
optionsmenu.add.button("Confirm",ConfirmClick)

Arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size=(10,15))

update_loading = pygame.USEREVENT + 0

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            exit()

    if mainmenu.is_enabled():
        mainmenu.update(events)
        mainmenu.draw(surface)
        if(mainmenu.get_current().get_selected_widget()):
            Arrow.draw(surface, mainmenu.get_current().get_selected_widget())
    
    if SettingsConfirmed == True:
        settings = {
            #"PEOPLE": PEOPLE,
            "GWIDTH": GWIDTH,
            "GHEIGHT": GHEIGHT,
            "GSPEED": GSPEED,
            "MLevels": MLEVELS
        }

        with open("config.json", "w") as f:
            json.dump(settings, f)

        subprocess.Popen(["python", "main.py"])
        exit()

    pygame.display.update()