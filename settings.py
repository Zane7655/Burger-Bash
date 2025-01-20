import pygame
from pygame import mixer
from os import walk
from os.path import join
from pytmx.util_pygame import load_pygame
import time
from random import randint, uniform, choice
from math import floor, ceil, atan2, degrees, hypot, floor, sqrt, dist, sin, pi

# general vars
WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
FRAMERATE = 120
BG_COLOR = '#fcdfcd'
FULLSCREEN = False
MAX_FILLINGS = 5
NUM_PLAYERS = 4
ROUND_PAUSE_TIME = 500
LOADING_SCREEN_SKIP = False
WIN_SCREEN_DUR = 1000 * 15

# wall vars
WALL_SIZE = (1000, WINDOW_WIDTH)
WALL_PADDING_X = 343
WALL_PADDING_Y = 63

# arena vars
WALL_OFFSET_X = -1 # 10
WALL_OFFSET_Y = 1 # 15
WALL_SCALE = 0.45 # 0.51 # 0.53
SHOW_WALLS = False
SODA_POS_X = [340, 940, 340, 940] # [300, 980, 300, 980]
SODA_POS_Y = [40, 40, 680, 680] # [20, 20, 700, 700]
SODA_SCALE = 0.1 # 0.08
SODA_MASS = 60
SODA_SPEED_MULTIPLYER = 5
SODA_MAX_SPEED = 2800

# tile vars
TILE_OVERIDE = False
TILE = 'tan-orange'
TILES = ['Lred-Dred', 'purple', 'teal-white', 'Dcafe', 'Lcafe', 'orange', 'Dnavy', 'Dgray', 'orange-red', 'Dmint-tan', 'tan-orange']
TILE_TYPES = ['svg', 'svg', 'svg', 'svg', 'svg', 'svg', 'svg', 'svg', 'svg', 'svg', 'svg']
TILE_TYPE = 'svg'
BG_TILE_SIZE = 99
NUM_TILES_WIDTH = ceil(1280/BG_TILE_SIZE)
TILE_OFFSET_X = -3
TILE_OFFSET_Y = -36
TILE_NUM = 150

# landing zone vars
LANDING_ZONE_PADDING = 75
LANDING_ZONE_SIZE = 125 + LANDING_ZONE_PADDING
LANDING_ZONE_SPACE_BUBBLE = 125
ZONE_DOTS_SCALE = 0.7
ZONE_DOTS_SPD = 80
ZONE_SPAWN_SPEED = 50
ZONE_FONT_COLORS = {'empty': 'white', 'player1': '#2184bf', 'player2': '#95cc3a', 'player3': '#ffc634', 'player4': '#fe5a59'}

# profile vars
PROFILE_PADDING_X = 150 # 120 edge of screen
PROFILE_PADDING_Y = 123 # 93 edge of screen
PROFILE_POS = [(PROFILE_PADDING_X, PROFILE_PADDING_Y), (WINDOW_WIDTH - PROFILE_PADDING_X, WINDOW_HEIGHT - PROFILE_PADDING_Y), (WINDOW_WIDTH - PROFILE_PADDING_X, PROFILE_PADDING_Y), (PROFILE_PADDING_X, WINDOW_HEIGHT - PROFILE_PADDING_Y)]

# score
SCORE_PADDING_X = 220 # 120 edge of screen
SCORE_PADDING_Y = 117 # 93 edge of screen
EXTRA_SCORE_PADDING_Y = 2
SCORE_POS = [(SCORE_PADDING_X, SCORE_PADDING_Y), (WINDOW_WIDTH - SCORE_PADDING_X, WINDOW_HEIGHT - SCORE_PADDING_Y + EXTRA_SCORE_PADDING_Y), (WINDOW_WIDTH - SCORE_PADDING_X, SCORE_PADDING_Y), (SCORE_PADDING_X, WINDOW_HEIGHT - SCORE_PADDING_Y + EXTRA_SCORE_PADDING_Y)]

# player vars
PLAYER_FRICTION_MULTIPLYER = 3
PLAYER_FRICTION = [1.9, 2.0, 2.1, 2.2, 2.2, 2.2] # higher is more
PLAYER_MAX_HEIGHTS = [210, 200, 190, 170, 160, 160]
PLAYER_MASS = [10, 15, 20, 25, 30, 30]
PLAYER_SPEED_MULTIPLYER = 12
PLAYER_SOFTNESS = [0.65, 0.75, 0.85, 0.95, 1, 1] # 1-0 | 1 has no effect
PLAYER_SPAWNS = ['blank', (450, 170), (830, 550), (830, 170), (450, 550)]
PLAYER_DEF_WIDTH = 79
PLAYER_DEF_HEIGHT = 79
PLAYER_SQUASH_AMOUNTS = [20, 20, 23, 26, 30, 35] # higher is less
PLAYER_AIM_MAX_SHAKE = 5
PLAYER_RADIUS = 79

# menu vars
MENU_COUNTER_SIZE_X = 2475/720
MENU_COUNTER_SIZE_Y = 2475/720
MAIN_MENU_FADE_SPD = 750
MENU_PLAY_SIZE_X = 2.8
MENU_PLAY_SIZE_Y = 2.8
MENU_TITLE_SIZE_X = 2.8
MENU_TITLE_SIZE_Y = 2.8
MENU_BOARD_SIZE_X = 3.4
MENU_BOARD_SIZE_Y = 3.4

MENU_FILLING_SIZES = {'cheese': 3.4, 'lettuce': 3.4, 'pickle': 3.4, 'tomato': 3.4}
MENU_FILLING_SPAWN_SIZE = 2.3
MENU_CHEESE_SPAWN_POS = [(167, 360), (167, 327), (167, 293), (167, 260)]
MENU_CHEESE_SPAWN_DELAY = [0, 100, 200, 300]
MENU_LETTUCE_SPAWN_POS = [(392, 355), (332, 325), (422, 295), (362, 265)] 
MENU_LETTUCE_SPAWN_DELAY = [0, 100, 200, 300]
MENU_PICKLE_SPAWN_POS = [(132, 552), (132, 515), (132, 482), (157, 552), (157, 515), (157, 482), (182, 552), (182, 515), (182, 482), (207, 552), (207, 515), (207, 482)]
MENU_PICKLE_SPAWN_DELAY = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550]
MENU_TOMATO_SPAWN_POS = [(337, 520), (357, 520), (377, 520), (397, 520)] # X: 367 Y: 540
MENU_TOMATO_SPAWN_DELAY = [0, 100, 200, 300]

MENU_BURNER_POS = [(775, 170), (1065, 170), (775, 460), (1065, 460)] # 560 is oven left, total space is 720 | Burner is 229 wide
MENU_KNOB_POS = [(690, 650), (800, 650), (1040, 650), (1150, 650)]
MENU_FIRE_SPAWN_DELAY = 100
MENU_FIRE_AMPLITUDE = 3
MENU_FIRE_PERIOD = 30
TWO_PI = 2 * pi

# item select
ITEM_SELECTOR_POS = [((WINDOW_WIDTH/2) - 300, (WINDOW_HEIGHT/2)-131), (WINDOW_WIDTH/2, (WINDOW_HEIGHT/2)-131), ((WINDOW_WIDTH/2) + 300, (WINDOW_HEIGHT/2)-131)]
ITEM_TYPES = ['toaster', 'garbage', 'ketchup']
KETCHUP_FRICTION = 4
GARBAGE_SPEED_MULTIPLYER = 5
GARBAGE_MAX_SPEED = 2200
GARBAGE_MASS = 30
BREAD_SPEED = 700
BREAD_MASS = 1
BREAD_POWER = 5

# droppings