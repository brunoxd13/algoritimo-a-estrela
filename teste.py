#!/usr/bin/env python
# coding=utf-8

# Glittering Light -- a casual turn-based maze game for the Linux console
# 2015-04-25 Felix PleÈ™oianu <felix@plesoianu.ro>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import division

import random

import curses
from curses.textpad import rectangle

C_WHITE = 0
C_FLOOR = 1
C_WALL = 2
C_WATER = 3
C_PLANT = 4
C_ITEM = 5
C_FOUNT = 6
C_ENEMY = 7

UNIT_FEAR = 3
MAX_FEAR = 10 # So that you don't die instantly when you reach 3 fear.

dirkeys = {
	ord('h'): 'w', ord('j'): 's', ord('k'): 'n', ord('l'): 'e',
	curses.KEY_LEFT: 'w', curses.KEY_DOWN: 's',
	curses.KEY_UP: 'n', curses.KEY_RIGHT: 'e',
}

main_menu = ["[N]ew game", "[C]ontinue game",
	"[H]ow to play", "[B]est scores", "[Q]uit"]

title_banner = [
"  __  _                                          _            _        ",
" /  || | o                  o                 \_|_)  o       | |       ",
" \__|| |   _|__|_  _   ,_       _  _    __,     |        __, | |   _|_ ",
"    ||/  |  |  |  |/  /  |  |  / |/ |  /  |    _|    |  /  | |/ \   |  ",
"(__/ |__/|_/|_/|_/|__/   |_/|_/  |  |_/\_/|/  (/\___/|_/\_/|/|   |_/|_/",
"                                         /|               /|           ",
"                                         \|               \|           "
]

end_banner = [
	" _                                   _                     ",
	"(_|   |                             | |                    ",
	"  |   |  __                    __,  | |   _             _  ",
	"  |   | /  \_|   |    |  |  |_/  |  |/_) |/    |   |  |/ \_",
	"   \_/|/\__/  \_/|_/   \/ \/  \_/|_/| \_/|__/   \_/|_/|__/ ",
	"     /|                                              /|    ",
	"     \|                                              \|    ",
	"                                  _                        ",
	"  o               |              | |                       ",
	"      _  _      __|   __,   ,_   | |   _  _    _   ,   ,   ",
	"  |  / |/ |    /  |  /  |  /  |  |/_) / |/ |  |/  / \_/ \_ ",
	"  |_/  |  |_/  \_/|_/\_/|_/   |_/| \_/  |  |_/|__/ \/  \/  "
]

help_text = [
	"Get as far as you can, collecting glitter for score.",
	"Being right next to nightmares increases your fear.",
	"",
	"Arrow keys or h-j-k-l to move. '.' (period) to wait.",
	"'r' and a direction to run that way until stopped.",
	"",
	"? to show instructions during the game.",
	"",
	"Press 'x' and a digit to examine nearby items.",
	"You can also click the mouse for it, where available."
]

terrain = {
	ord('.'): {"name": "a floor tile", "color": C_FLOOR},
	ord('*'): {"name": "a fountain", "color": C_FOUNT},
	ord('+'): {"name": "a wall", "color": C_WALL},
	ord('~'): {"name": "a pool of water", "color": C_WATER},
	ord('='): {"name": "brambles", "color": C_PLANT}
}

items = {
	"light": {"char": "!", "color": C_ITEM},
	"glitter": {"char": "$", "color": C_ITEM},
	"speed": {"char": "?", "color": C_ITEM}
}

item_odds = ["light", "light", "glitter", "glitter", "speed", "speed",
	None, None, None, None]
fear_odds = ["nightmare"] * 6 + [None] * 4

world = None
log = None
highscores = []

title_screen = None
game_screen = None
score_screen = None

active_screen = None

finished = False

def run_in_curses(stdscr):
	global world, worldrng, log, scroll_lines
	global title_screen, game_screen, score_screen, active_screen
	
	scrheight, scrwidth = stdscr.getmaxyx()

	if (scrheight < 24 or scrwidth < 80):
		raise RuntimeError("80x24 or larger terminal required.")

	curses.mousemask(curses.BUTTON1_CLICKED)

	stdscr.leaveok(0)
	stdscr.idlok(1)
	stdscr.scrollok(True)
	stdscr.setscrreg(21, 23)

	if curses.has_colors():
		curses.init_pair(
			C_FLOOR, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
		curses.init_pair(
			C_WALL, curses.COLOR_WHITE, curses.COLOR_YELLOW)
		curses.init_pair(
			C_WATER, curses.COLOR_CYAN, curses.COLOR_BLUE)
		curses.init_pair(
			C_PLANT, curses.COLOR_BLACK, curses.COLOR_GREEN)
		curses.init_pair(
			C_ITEM, curses.COLOR_YELLOW, curses.COLOR_BLACK)
		curses.init_pair(
			C_FOUNT, curses.COLOR_CYAN, curses.COLOR_BLACK)
		curses.init_pair(
			C_ENEMY, curses.COLOR_RED, curses.COLOR_BLACK)

	log = GameLog()

	title_screen = TitleScreen(stdscr)
	game_screen = GameScreen(stdscr)
	score_screen = ScoreScreen(stdscr)
	
	active_screen = title_screen
	
	while not finished:
		if (scrheight < 24 or scrwidth < 80):
			stdscr.erase()
			stdscr.addstr(
				0, 0, "80x24 or larger terminal required.")
			stdscr.refresh()
		else:
			stdscr.setscrreg(21, scrheight - 1)
			active_screen.render()
		key = stdscr.getch()
		if key == curses.KEY_RESIZE:
			scrheight, scrwidth = stdscr.getmaxyx()
		else:
			active_screen.handle_key(key)

def draw_dialog_bg(window, top, left, height, width):
	window.attron(curses.A_REVERSE)
	for y in range(height):
		window.addstr(top + y, left, " " * width)
	rectangle(window, top, left, top + height - 1, left + width - 1)
	window.attroff(curses.A_REVERSE)
	
def draw_help_dialog(window):
	draw_dialog_bg(window, 1, 7, 18, 66)
	window.addstr(1, 8, "[How to play]", curses.A_REVERSE)
	for i in range(0, len(help_text)):
		window.addstr(3 + i, 8, help_text[i], curses.A_REVERSE)
	window.addstr(18, 57, "[Press any key]", curses.A_REVERSE)

def prompt(window, message):
	draw_dialog_bg(window, 9, 25, 4, 32)
	window.addstr(10, 26, message[0:50].center(30), curses.A_REVERSE)
	window.addstr(11, 26, " " * 30)
	curses.echo()
	answer = window.getstr(11, 26, 30)
	curses.noecho()
	return answer

def add_high_score(window, level, glitter):
	name = prompt(window, "High score! What's your name?")
	score = (name[0:30].decode(), level, glitter)
	highscores.append(score)

def next_coords(x, y, direction):
	if direction == 'n':
		return x, y - 1
	elif direction == 's':
		return x, y + 1
	elif direction == 'e':
		return x + 1, y
	elif direction ==  'w':
		return x - 1, y
	else:
		raise ValueError("Invalid compass direction " + str(direction))

def roll_dice(count, sides):
	roll = 0
	for i in range(count):
		roll += random.randint(1, sides)
	return roll

def score_value(score):
	# Over long games, you pick up 2-3 glitter piles per level.
	return score[1] * 125 + score[2]

class Screen:
	def __init__(self, window):
		self.window = window

	def render(self):
		self.render_viewport()
		
		self.window.addstr(
			20, 0,
			self.status_text().ljust(80),
			curses.A_REVERSE)
			
		self.render_messages()

		self.window.refresh()

	def render_messages(self):
		self.window.move(21, 0)
		self.window.clrtobot()
		height, width = self.window.getmaxyx()
		num_msg = height - 21
		tail = log.messages[-num_msg:]
		for i in range(len(tail)):
			self.window.addstr(21 + i, 0, tail[i])

class TitleScreen(Screen):
	def render_viewport(self):
		for i in range(20):
			self.window.move(i, 0)
			self.window.clrtoeol()
		
		self.window.attron(curses.A_BOLD)
		
		attr = 0

		if curses.has_colors():
			attr = curses.color_pair(C_FLOOR)
		for i in range(len(title_banner)):
			self.window.addstr(
				i, 0, title_banner[i].center(80), attr)
		
		if curses.has_colors():
			attr = curses.color_pair(C_WHITE)
		msg = "A 2015 game by"
		self.window.addstr(i + 2, 0, msg.center(80), attr)
		if curses.has_colors():
			attr = curses.color_pair(C_FOUNT)
		msg = "www.notimetoplay.org"
		self.window.addstr(i + 4, 0, msg.center(80), attr)
		
		self.window.attroff(curses.A_BOLD)
		
		for i in range(len(main_menu)):
			self.window.addstr(i + 13, 33, main_menu[i])
	
	def status_text(self):
		return ""

	def handle_key(self, key):
		global finished, world, active_screen
		
		if key == ord('q') or key == 27:
			finished = True
		elif key == ord('n'):
			world = GameWorld()
			world.player.log = log

			active_screen = game_screen
		elif key == ord('c'):
			if world == None:
				world = GameWorld()
				world.player.log = log

			active_screen = game_screen
		elif key == ord('h'):
			draw_help_dialog(self.window)
			self.window.getch()
		elif key == ord('b'):
			active_screen = score_screen
		else:
			curses.flash()

class ScoreScreen(Screen):
	def render_viewport(self):
		for i in range(20):
			self.window.move(i, 0)
			self.window.clrtoeol()

		self.window.addstr(1, 2, "High Score Table")
		msg = "%-30s | %5s | %5s" % ("Player", "Level", "Score")
		self.window.addstr(3, 2, msg)
		self.window.hline(4, 2, curses.ACS_HLINE, 46)
		for i in range(len(highscores)):
			top = highscores[i]
			msg = "%-30s | %5d | %5d" % (top[0], top[1], top[2])
			self.window.addstr(5 + i, 2, msg)
	
	def status_text(self):
		return "[Esc] Menu"

	def handle_key(self, key):
		global active_screen
		
		if key == ord('q') or key == 27:
			active_screen = title_screen
		else:
			curses.flash()

class GameScreen(Screen):
	def __init__(self, window):
		Screen.__init__(self, window)
		
		self.look_mode = False
		self.target_squares = []
	
	def render_viewport(self):
		level = world.palace
		lmap = level.level_map
		
		x1, y1, x2, y2 = self.update_seen()
		
		self.window.attron(curses.A_DIM)
		for y in range(level.height):
			for x in range(level.width):
				if level.seen[y][x]:
					self.render_tile(x, y, lmap[y][x])
				else:
					self.window.addch(y, x, " ")
		self.window.attroff(curses.A_DIM)
		
		for y in range(y1, y2 + 1):
			for x in range(x1, x2 + 1):
				self.render_tile(x, y, lmap[y][x])
		
		self.target_squares = []
		self.render_things(level, Thing)
		self.render_things(level, Creature)
		
		attr = curses.A_BOLD
		if curses.has_colors():
			attr = curses.color_pair(C_ENEMY) | attr
		if world.player.fear >= MAX_FEAR:
			for i in range(len(end_banner)):
				self.window.addstr(
					4 + i, 10, end_banner[i], attr)
	
	def update_seen(self):
		p = world.player
		sight_radius = p.sight_radius()
		x1 = max(0, p.x - sight_radius)
		y1 = max(0, p.y - sight_radius)
		x2 = min(p.level.width - 1, p.x + sight_radius)
		y2 = min(p.level.height - 1, p.y + sight_radius)
		
		for y in range(y1, y2 + 1):
			for x in range(x1, x2 + 1):
				p.level.seen[y][x] = True
		
		return x1, y1, x2, y2
	
	def render_tile(self, x, y, char):
		if curses.has_colors():
			color = curses.color_pair(terrain[char]["color"])
		else:
			color = 0
		self.window.addch(y, x, char, color)
	
	def render_things(self, level, thing_class):
		for i in level.content:
			# Strict check since Creature inherits from Thing.
			if type(i) != thing_class:
				continue
			elif not world.player.can_see(i.x, i.y):
				continue
			
			char = i.char
			if i != world.player:
				square = (i.x, i.y)
				if square not in self.target_squares:
					self.target_squares.append(square)
				target_num = self.target_squares.index(square)
				if self.look_mode:
					if target_num < 10:
						char = str(target_num)
				
			attr = curses.A_BOLD
			if curses.has_colors():
				attr = curses.color_pair(i.color) | attr
			self.window.addch(i.y, i.x, char, attr)

	def status_text(self):
		w = world
		p = w.player
		msg = "Level: %d Glitter: %d Light: %d Speed: %d Fear: %s"
		return msg % (w.level, w.glitter,
			p.light, p.speed, '&' * (p.fear // UNIT_FEAR))

	def handle_key(self, key):
		global world, active_screen
		
		if world.player.fear >= MAX_FEAR:
			log("You made it to level %d, with %d glitter." % (
				world.level, world.glitter))
			tmp = (None, world.level, world.glitter)
			if len(highscores) == 0:
				add_high_score(
					self.window,
					world.level,
					world.glitter)
			elif score_value(tmp) > score_value(highscores[-1]):
				add_high_score(
					self.window,
					world.level,
					world.glitter)
				highscores.sort(key=score_value, reverse=True)
				while len(highscores) > 10:
					del highscores[-1]
			self.look_mode = False
			active_screen = score_screen
			world = None
			return
		elif key == ord('q') or key == 27:
			self.look_mode = False
			active_screen = title_screen
			return
		elif key == ord('?'):
			self.look_mode = False
			draw_help_dialog(self.window)
			self.window.getch()
			return
		
		if world.player.action_points <= 0:
			world.update()

		if key in dirkeys:
			self.look_mode = False
			if world.player.walk(dirkeys[key]):
				world.update()
		elif key == ord('r'):
			self.look_mode = False
			world.player.log("Run which way?")
			self.render_messages()
			direction = self.window.getch()
			if direction in dirkeys:
				self.window.timeout(500)
				d = dirkeys[direction]
				while world.player.is_way_clear(d):
					world.player.walk(d)
					world.update()
					self.render()
					if self.window.getch() > -1:
						break
				self.window.timeout(-1)
			else:
				world.player.log("Canceled.")
		elif key == ord('.'):
			self.look_mode = False
			world.player.log("You stand still.")
			world.update()
		elif key == ord('x'):
			self.look_mode = not self.look_mode
		elif ord('0') <= key <= ord('9'):
			tnum = key - ord('0')
			if not self.look_mode:
				world.player.log("But you're not looking!")
			elif tnum >= len(self.target_squares):
				world.player.log("Too few things around.")
			elif self.look_mode:
				x, y = self.target_squares[tnum]
				world.player.look(x, y)
				self.look_mode = False
		elif key == curses.KEY_MOUSE:
			self.look_mode = False
			device, x, y, z, button = curses.getmouse()
			if button == curses.BUTTON1_CLICKED:
				world.player.look(x, y)
		else:
			curses.flash()

class GameLog:
	def __init__(self):
		self.messages = []
	
	def say(self, message):
		message = message[0].capitalize() + message[1:]
		self.messages.append(message)
		while len(self.messages) > 100:
			del self.messages[0]

	def __call__(self, message):
		self.say(message)

class GameWorld:
	def __init__(self):
		self.palace = Level()
		self.palace.populate()
		self.player = Creature(self.palace)
		self.player.color = C_WHITE
		#self.player.log = log
		#self.player.light = 200
		self.player.fear = 0
		self.player.base_speed = 100
		self.player.move_to(0, self.palace.entry_line)
		
		self.level = 1
		self.glitter = 0
	
	def update(self):
		p = self.player
		stuff = p.level.content
		for i in stuff.copy():
			if not isinstance(i, Creature):
				if i.x == p.x and i.y == p.y:
					p.get_item_here()
			else:
				if i == p:
					if i.light > 0:
						i.light -= i.light // 150 + 1
					if i.speed > 0:
						i.speed -= 1
				elif i.fear <= 0:
					stuff.remove(i)
					p.log("The nightmare plays itself out.")
				elif i.distance_to(p) < 2:
					i.fear -= 1
					p.fear += 1
					p.log("Your fear grows.")

				if i.action_points <= 0:
					i.action_points += (
						i.speed + i.base_speed) // 10
				elif i != p:
					self.run_ai(i)
	
	def run_ai(self, mob):
		p = self.player
		if mob.distance_to(p) == 1:
			mob.last_heading = None # To reset the chase mode.
			return
		elif mob.x == p.x:
			if mob.y < p.y:
				mob.last_heading = 's'
			elif mob.y > p.y:
				mob.last_heading = 'n'
		elif mob.y == p.y:
			if mob.x < p.x:
				mob.last_heading = 'e'
			elif mob.x > p.x:
				mob.last_heading = 'w'
		elif mob.last_heading == None:
			mob.last_heading = random.choice(
				['n', 's', 'e', 'w'])

		x, y = next_coords(mob.x, mob.y, mob.last_heading)
		if mob.level.is_on_grid(x, y) and mob.can_enter(x, y):
			mob.walk(mob.last_heading)
		else:
			mob.last_heading = None

class Level:
	def __init__(self):
		self.width = 80
		self.height = 20

		self.level_map = [bytearray(self.width)
			for i in range(self.height)]
		self.seen = [[False] * self.width for i in range(self.height)]
		
		self.entry_line = -1
		self.exit_line = 10
		
		self.content = set()
		
		self.generator = LevelGenerator()
	
	def is_on_grid(self, x, y):
		return x >= 0 and y >= 0 and x < self.width and y < self.height
	
	def terrain_at(self, x, y):
		tile = self.level_map[y][x]
		if tile in terrain.keys():
			return terrain[tile]
		else:
			return None
	
	def items_at(self, x, y):
		# Strict check since Creature inherits from Thing.
		return (i for i in self.content
			if type(i) == Thing and i.x == x and i.y == y)
	
	def creature_at(self, x, y):
		# Strict check since Creature inherits from Thing.
		for i in self.content:
			if type(i) == Creature and i.x == x and i.y == y:
				return i
		return None
	
	def populate(self):
		self.generator.populate(self)
		self.seen = [[False] * self.width for i in range(self.height)]

class Thing(object):
	def __init__(self, level):
		assert isinstance(level, Level)

		self.level = level
		self.level.content.add(self)
		self.x = -1
		self.y = -1
		
		self.name = "thing"
		self.pronoun = "it"
		self.proper_name = False
	
	def move_to(self, x, y, parent = None):
		if parent != None and parent != self.level:
			self.level.content.remove(self)
			parent.content.add(self)
			self.level = parent

		if self.level.is_on_grid(x, y):
			self.x = x
			self.y = y
		else:
			raise ValueError("Can't move outside the level map.")

	def the_name(self):
		if self.proper_name:
			return self.name
		else:
			return "the " + self.name
	
	def a_name(self):
		if self.name[0] in ('a', 'e', 'i', 'o', 'u'):
			return "an " + self.name
		else:
			return "a " + self.name

	def __str__(self):
		return self.a_name()

class Creature(Thing):
	def __init__(self, level):
		Thing.__init__(self, level)
		self.log = None

		self.char = "@"
		
		self.base_speed = 0
		self.speed = 0
		self.light = 0
		self.fear = 0
		
		self.action_points = 0
		
		self.last_heading = None # For the AI system.

	def can_see(self, x, y):
		radius = self.sight_radius()
		can_see_x = abs(self.x - x) <= radius
		can_see_y = abs(self.y - y) <= radius
		return can_see_x and can_see_y
		
	def can_enter(self, x, y):
		tile = chr(self.level.level_map[y][x])
		return tile == '.'

	def is_way_clear(self, direction):
		new_x, new_y = next_coords(self.x, self.y, direction)

		if not self.level.is_on_grid(new_x, new_y):
			return False
		elif self.level.creature_at(new_x, new_y) != None:
			return False
		elif not self.can_enter(new_x, new_y):
			return False
		else:
			return True

	def walk(self, direction):
		new_x, new_y = next_coords(self.x, self.y, direction)

		if not self.level.is_on_grid(new_x, new_y):
			if direction == 'w':
				self.log("There's no going back.")
				return False
			elif direction == 'e':
				world.level += 1
				self.level.populate()
				self.level.content.add(self)
				self.move_to(0, self.level.entry_line)
				self.fear -= UNIT_FEAR
				if self.fear < 0:
					self.fear = 0
				return True
			else:
				self.log("You can't stray from the path.")
				return False
		elif self.level.creature_at(new_x, new_y) != None:
			creature = self.level.creature_at(new_x, new_y)
			x, y = creature.x, creature.y
			creature.x, creature.y = self.x, self.y
			self.x, self.y = x, y
			self.action_points -= 5
			return True
		elif not self.can_enter(new_x, new_y):
			t = self.level.terrain_at(new_x, new_y)
			if t != None and t["name"] != None:
				self.log("The way is barred by " + t["name"])
			else:
				self.log("The way is barred.")
			return False
		else:
			self.x = new_x
			self.y = new_y
			self.action_points -= 5
			return True
	
	def distance_to(self, thing):
		return abs(self.x - thing.x) + abs(self.y - thing.y)
	
	def sight_radius(self):
		return self.light // 50 + 2
	
	def look(self, x, y):
		if not self.level.is_on_grid(x, y):
			return
		elif not self.can_see(x, y):
			self.log("You can't see that far right now.")
			return
		
		tile = self.level.level_map[y][x]
		msg = "You see: " + terrain[tile]["name"]
		for i in self.level.content:
			if i.x == x and i.y == y:
				if i == self:
					msg += ", yourself"
				else:
					msg += ", " + i.name
		self.log(msg)
	
	def get_item_here(self):
		item = next(self.level.items_at(self.x, self.y), None)
		if item == None:
			self.log("There's nothing portable here.")
			return
		
		if item.name == "light":
			self.light += 75
		elif item.name == "speed":
			self.speed += 50
		elif item.name == "glitter":
			world.glitter += roll_dice(5, 20)
		
		item.level.content.remove(item)
		self.log("You find %s." % (item.name,))

class LevelGenerator:
	def __init__(self):
		self.rng = random.Random()
		self.cellw = 7
		self.cellh = 5
	
	def populate(self, level):
		for x in range(level.width):
			for y in range(level.height):
				level.level_map[y][x] = ord('.')
		for x in range (level.width):
			level.level_map[0][x] = ord('+')
			level.level_map[level.height - 1][x] = ord('+')
		for y in range(level.height):
			level.level_map[y][0] = ord('+')
			level.level_map[y][level.width - 1] = ord('+')
		
		self.level = level
		self.subdivideWide(1, 1, level.width - 2, level.height - 2)
		
		level.entry_line = level.exit_line
		level.level_map[level.entry_line][0] = ord('.')
		level.level_map[level.entry_line][1] = ord('.')
		level.exit_line = self.rng.randint(1, 18)
		level.level_map[level.exit_line][79] = ord('.')
		level.level_map[level.exit_line][78] = ord('.')

		self.level.content.clear()

		for y in range(1, level.height - 1):
			for x in range(1, level.width - 1):
				if self.level.level_map[y][x] != ord('.'):
					continue
				if self.rng.random() >= 0.03:
					continue
				kind = self.rng.choice(item_odds)
				if kind != None:
					item = Thing(level)
					item.name = kind
					item.char = items[kind]["char"]
					item.color = items[kind]["color"]
					item.move_to(x, y)

		for y in range(1, level.height - 1):
			for x in range(1, level.width - 1):
				if self.level.level_map[y][x] != ord('.'):
					continue
				if self.rng.random() >= 0.03:
					continue
				if self.rng.choice(fear_odds) != None:
					creature = Creature(level)
					creature.log = log
					creature.name = "nightmare"
					creature.char = "&"
					creature.color = C_ENEMY
					creature.fear = UNIT_FEAR
					creature.base_speed = 150
					creature.move_to(x, y)
	
	def subdivideWide(self, x1, y1, x2, y2):
		w = x2 - x1 + 1
		h = y2 - y1 + 1
		# You have to check both dimensions
		# or you'll get oddly skewed levels.
		if w < self.cellw or h < self.cellh or w == h:
			self.furnishRoom(x1, y1, x2, y2)
			return 0
		
		if w == 3:
			x = x1 + 1
		else:
			x = x1 + self.rng.randint(1, w - 2)
		for y in range(y1, y2 + 1):
			self.level.level_map[y][x] = ord('+')

		wall1 =	self.subdivideHigh(x1, y1, x - 1, y2)
		wall2 = self.subdivideHigh(x + 1, y1, x2, y2)
		
		if h >= 15:
			doors = [y1 + h // 3, y2 - h // 3]
		else:
			doors = [y1 + h // 2]

		for y in doors:
			self.level.level_map[y][x] = ord('.')
			# Account for walls placed deeper into recursion.
			self.level.level_map[y][x - 1] = ord('.')
			self.level.level_map[y][x + 1] = ord('.')
			
		return x

	def subdivideHigh(self, x1, y1, x2, y2):
		w = x2 - x1 + 1
		h = y2 - y1 + 1
		# You have to check both dimensions
		# or you'll get oddly skewed levels.
		if w < self.cellw or h < self.cellh or w == h:
			self.furnishRoom(x1, y1, x2, y2)
			return 0
		
		if h == 3:
			y = y1 + 1
		else:
			y = y1 + self.rng.randint(1, h - 2)
		for x in range(x1, x2 + 1):
			self.level.level_map[y][x] = ord('+')

		wall1 = self.subdivideWide(x1, y1, x2, y - 1)
		wall2 = self.subdivideWide(x1, y + 1, x2, y2)

		if w >= 45:
			doors = [x1 + w // 4, x1 + w // 2, x2 - w // 4]
		elif w >= 15:
			doors = [x1 + w // 3, x2 - w // 3]
		else:
			doors = [x1 + w // 2]

		for x in doors:
			self.level.level_map[y][x] = ord('.')
			# Account for walls placed deeper into recursion.
			self.level.level_map[y - 1][x] = ord('.')
			self.level.level_map[y + 1][x] = ord('.')
			
		return y

	def furnishRoom(self, x1, y1, x2, y2):
		w = x2 - x1 + 1
		h = y2 - y1 + 1
		lmap = self.level.level_map

		if w == 3 and h == 3:
			lmap[y1 + 1][x1 + 1] = ord('*')
		elif w == 3 and h > 2:
			for y in range(y1, y2 + 1):
				if (y + x1 + 1) % 2 == 0:
					lmap[y][x1 + 1] = ord('+')
			if y == y2 and (y + x1 + 1) % 2 == 0:
				lmap[y][x1 + 1] = ord('*')
		elif h == 3 and w > 2:
			for x in range(x1, x2 + 1):
				if (y1 + 1 + x) % 2 == 0:
					lmap[y1 + 1][x] = ord('+')
			if x == x2 and (y1 + 1 + x) % 2 == 0:
				lmap[y1 + 1][x] = ord('*')
		elif w == 4:
			if self.rng.random() < 0.5:
				char = ord('~')
			else:
				char = ord('=')
			for y in range(y1 + 1, y2):
				lmap[y][x1 + 1] = char
				lmap[y][x2 - 1] = char
		elif h == 4:
			if self.rng.random() < 0.5:
				char = ord('~')
			else:
				char = ord('=')
			for x in range(x1 + 1, x2):
				lmap[y1 + 1][x] = char
				lmap[y2 - 1][x] = char
		elif w == 5 and h == 5:
			lmap[y1 + 1][x1 + 1] = ord('*')
			lmap[y1 + 3][x1 + 3] = ord('*')
			lmap[y1 + 1][x1 + 3] = ord('*')
			lmap[y1 + 3][x1 + 1] = ord('*')
		elif w == 5 and h > 2:
			for y in range(y1, y2 + 1):
				if (y + x1 + 1) % 2 == 0:
					lmap[y][x1 + 1] = ord('+')
					lmap[y][x2 - 1] = ord('+')
			if y == y2 and (y + x1 + 1) % 2 == 0:
				lmap[y][x1 + 1] = ord('*')
				lmap[y][x2 - 1] = ord('*')
		elif h == 5 and w > 2:
			for x in range(x1, x2 + 1):
				if (y1 + 1 + x) % 2 == 0:
					lmap[y1 + 1][x] = ord('+')
					lmap[y2 - 1][x] = ord('+')
			if x == x2 and (y1 + 1 + x) % 2 == 0:
				lmap[y1 + 1][x] = ord('*')
				lmap[y2 - 1][x] = ord('*')
		elif w == 7 and h == 7:
			for y in range(y1 + 1, y1 + 3):
				for x in range(x1 + 1, x1 + 3):
					lmap[y][x] = ord('=')
			for y in range(y1 + 1, y1 + 3):
				for x in range(x1 + 4, x1 + 6):
					lmap[y][x] = ord('~')
			for y in range(y1 + 4, y1 + 6):
				for x in range(x1 + 4, x1 + 6):
					lmap[y][x] = ord('=')
			for y in range(y1 + 4, y1 + 6):
				for x in range(x1 + 1, x1 + 3):
					lmap[y][x] = ord('~')
		elif w > 5 and h > 5 and (w % 2 == 1 or h % 2 == 1):
			if h % 2 == 1:
				for y in range(y1 + 1, y2, 2):
					lmap[y][x1 + 1] = ord('+')
					lmap[y][x2 - 1] = ord('+')
			if w % 2 == 1:
				for x in range(x1 + 1, x2, 2):
					lmap[y1 + 1][x] = ord('+')
					lmap[y2 - 1][x] = ord('+')
			self.furnishRoom(x1 + 2, y1 + 2, x2 - 2, y2 - 2)

if __name__ == "__main__":
	try:
		curses.wrapper(run_in_curses)
	except RuntimeError as e:
		print(e)