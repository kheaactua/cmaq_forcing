#!/usr/bin/env python

# Colour code things
class bcolours:

	colours = {'red': 91, 'green': 32, 'blue': 94, 'yellow': 43, 'purple': 35, 'orange': 40, 'cyan': 36, 'clear': 0}

	#red="\033[%dm"%_red

	#lgreen='\033[1;%d;43m'%_green
	#green='\033[32m'
	#dgreen='\033[1;%d;40m'%_green

	#lblue='\033[%dm'%_blue
	#blue='\033[%dm'%_blue
	#dblue='\033[%dm'%_blue

	#yellow='\033[%dm'%yellow

	#purple='\033[%dm'%_purple

	#clear='\033[%dm'%_clear

	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	FAIL = "\033[1;91m"

	_yesterday = colours['green']
	_today = colours['blue']
	_tomorrow = colours['purple']


	@staticmethod
	def ansiColour(c):
		return '\033[%dm'%c

	@property
	def yesterday(self):
		return bcolours.ansiColour(bcolours._yesterday)

	@property
	def today(self):
		return bcolours.ansiColour(bcolours._today)

	@property
	def tomorrow(self):
		return bcolours.ansiColour(bcolours._tomorrow)

	@property
	def red(self):
		return self.ansiColour(bcolours.colours['red'])

	@property
	def green(self):
		return self.ansiColour(bcolours.colours['green'])

	@property
	def blue(self):
		return self.ansiColour(bcolours.colours['blue'])

	@property
	def purple(self):
		return self.ansiColour(bcolours.colours['purple'])

	@property
	def yellow(self):
		return self.ansiColour(bcolours.colours['yellow'])

	@property
	def cyan(self):
		return self.ansiColour(bcolours.colours['cyan'])

	@property
	def orange(self):
		return self.ansiColour(bcolours.colours['orange'])

	@property
	def HEADER(self):
		return '\033[1;36;40m'

	@property
	def WARNING(self):
		return self.ansiColour(bcolours.colours['yellow'])

	@property
	def clear(self):
		return self.ansiColour(bcolours.colours['clear'])

	def light(self, day):
		if day == "yesterday":
			c=bcolours._yesterday
		elif day == "today":
			c=bcolours._today
		elif day == "tomorrow":
			c=bcolours._tomorrow
		else:
			c=bcolours._colours['clear']

		return '\033[1;%d;43m'%c

	def dark(self, day):
		if day == "yesterday":
			c=bcolours._yesterday
		elif day == "today":
			c=bcolours._today
		elif day == "tomorrow":
			c=bcolours._tomorrow
		else:
			c=bcolours._colours['clear']

		return '\033[1;%d;40m'%c


class colouredNum():
	""" Classes used for debugging, it simply carries a number and a int """

	val=0
	c=0
	bg=bcolours.colours['clear']

	def __init__(self, val, c, bg=bcolours.colours['clear']):
		self.val=val
		self.c=c
		self.bg=bg

	def __str__(self):
		return bcolours.ansiColour(self.c) + "%4.3f"%self.val + bcolours.ansiColour(self.bg)
