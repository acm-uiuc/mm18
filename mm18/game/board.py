#! /usr/bin/env python

import constants
import json
import os
from collections import deque, defaultdict
from path import Path
import itertools

## @file board.py


## This is the board class.
#  It is where the code for the board goes.
class Board:

	## Board class. 
	#  The board consists of two lists and a dictionary.
	#  The dictionary contains the locations of the towers
	#  (key is a tuple for location on the board, entry is a tower object).
	#  The base list contains the tuple locations of the base - unordered.
	#  The path list contains the tuple locations of the path,
	#  ordered starting with those closest to the base and working outwards.
	#  @param base A list of tuples that represent the base location
	#  @param path A list of tuples that represent the path locations (ordered in orderPathsByClosest method)
	#  @param width An optional arguement, the width of the board
	#  @param height An optional arguement, the height of the board
	def __init__(self, base, path, width=constants.BOARD_SIDE, height=constants.BOARD_SIDE):
		self.base = base
		self.path = self.orderPathSquaresByClosest(base, path)
		
		self.width = width
		self.height = height
		
		self.tower = {}
		self.hitList = defaultdict(list)

		self.startPos = 4*[None]
		for x,y in self.path:
			if y is 0:
				self.startPos[constants.NORTH] = (x,y)
			elif x is self.width - 1:
				self.startPos[constants.EAST] = (x,y)
			elif y is self.height - 1:
				self.startPos[constants.SOUTH] = (x,y)
			elif x is 0:
				self.startPos[constants.WEST] = (x,y)

		pathList = self.findPaths()
		self.paths={}
		# The Path class takes paths starting at the base, so reverse
		for path in pathList:
			if path is not None:
				path.reverse()
		for direction in constants.DIRECTIONS:
			self.paths[direction]=Path(pathList[direction])
		

	## Reads in json for the board layout from a file and sorts it into two lists
	#  one for base positions and the other for path positions
	@staticmethod
	def jsonLoad(filename):
		filePath = os.path.join(os.path.dirname(__file__), filename)
		data =json.load(open(filePath))
		
		bases = data['bases']
		baseList = [tuple(pair) for pair in bases]
		
		paths = data['paths']
		pathList = [tuple(pair) for pair in paths]
		
		width = data['width']
		height = data['height']

		return Board(baseList, pathList)

	## Breadth-first search method that takes the unordered list of path locations
	#  and sorts them by how far from the base they are.
	#  @param baseList A list that contains the base locations
	#  @param pathList A list that contains the paths to the base in no order
	def orderPathSquaresByClosest(self, baseList, pathList):
		pathQueue = deque(baseList)
		outPath = []
		while pathQueue:
			x,y = pathQueue.popleft()
			if (x,y) not in outPath:
				if (x, y + 1) in pathList:
					pathQueue.append((x, y + 1))
				if (x, y - 1) in pathList:
					pathQueue.append((x, y - 1))
				if (x + 1, y) in pathList:
					pathQueue.append((x + 1, y))
				if (x - 1, y) in pathList:
					pathQueue.append((x - 1, y))
				if (x,y) not in baseList:
					outPath.append((x,y))
		return outPath

	## Depth-first search method that uses a list of path locations to build a
	#  list of paths, where each path starts at a starting path square (on the
	#  edge of the board) and ends at the base.
	#  TODO: make sure that paths end at a base
	def findPaths(self):
		paths = []
		
		northStack = self.startPos[constants.NORTH]
		eastStack = self.startPos[constants.EAST]
		southStack = self.startPos[constants.SOUTH]
		westStack = self.startPos[constants.WEST]
		
		if northStack:
			self.findPathsRecurse([northStack], paths)
		else:
			paths.append(None)
		if eastStack:
			self.findPathsRecurse([eastStack], paths)
		else:
			paths.append(None)
		if southStack:
			self.findPathsRecurse([southStack], paths)
		else:
			paths.append(None)
		if westStack:
			self.findPathsRecurse([westStack], paths)
		else:
			paths.append(None)

		return paths
	
	## The helper function to findPaths, it actually travels down the paths via a
	#  depth first search and adds a completed path the the paths list when it
	#  cannot go any farther.
	def findPathsRecurse(self, pathStack, paths):
		pathEnds = True
		x,y = pathStack[-1]
		north = (x, y+1)
		if north not in pathStack and north in self.path:
			pathEnds = False
			pathStack.append(north)
			self.findPathsRecurse(pathStack, paths)

		east = (x+1, y)
		if east not in pathStack and east in self.path:
			pathEnds = False
			pathStack.append(east)
			self.findPathsRecurse(pathStack, paths)
		
		south = (x, y-1)
		if south not in pathStack and south in self.path:
			pathEnds = False
			pathStack.append(south)
			self.findPathsRecurse(pathStack, paths)
		
		west = (x-1, y)
		if west not in pathStack and west in self.path:
			pathEnds = False
			pathStack.append(west)
			self.findPathsRecurse(pathStack, paths)
		
		if pathEnds:
			paths.append(pathStack[:])
		
		pathStack.pop()
		return paths

	## Check whether the position of the object being inserted is a valid placement on the board.
	#  Will contain error handling for invalid positions.
	#  @param position Tuple containing object position
	def validPosition(self, position):
		x,y=position
		
		for house in self.base:
			if house==(x,y):
				return 0

		for road in self.path:
			if road==(x,y):
				return 0

		if position in self.tower:
			return 0

		return x >= 0 and y >=0 and x < constants.BOARD_SIDE and y < constants.BOARD_SIDE

	## Adds an object to the board provided nothing is already in the location.
	#  @return true if successful and false if not
	#  @param item An object, most likely a tower
	#  @param position A tuple for the position of the object
	def addItem(self, item, position):
		if self.validPosition(position) and self.getItem(position) == None and position not in self.base and position not in self.path:
			self.tower[position] = item
			self.addToHitList(item, position)
			return True
		else:
			return False

	## Gets the item at the position or returns none if no object exists.
	#  Will contain error handling for something?
	#  If no error handling is needed class is unecessary and can be replaced just by the dict.get method.
	#  @return Item at the position or none if no object exists
	#  @param position A tuple containing object position
	def getItem(self, position):
		return self.tower.get(position,None)

	## Removes the item at the position
	#  @param position A tuple containing object position
	def removeItem(self, position):
		if self.getItem(position) != None:
			self.removeFromHitList(self.tower[position])
			del self.tower[position]
			

	## Adds a tower to all the appropriate places of the hitList
	#  @param self The board
	#  @param tower The tower to add to the hitList
	def addToHitList(self, tower, position):
		tX, tY = position

		tXLower = tX - constants.TOWER_RANGE[tower.upgrade]
		if tXLower < 0:
			tXLower = 0

		tXUpper = tX + constants.TOWER_RANGE[tower.upgrade]
		if tXUpper >= constants.BOARD_SIDE:
			txUpper = constants.BOARD_SIDE - 1

		tYLower = tY - constants.TOWER_RANGE[tower.upgrade]
		if tYLower < 0:
			tYLower = 0

		tYUpper = tY + constants.TOWER_RANGE[tower.upgrade]
		if tYUpper >= constants.BOARD_SIDE:
			tYUpper = constants.BOARD_SIDE - 1
		
		for elem in self.path:
			elemX, elemY = elem
			if elemX >= tXLower and elemX <= tXUpper:
				if elemY >= tYLower and elemY <= tYUpper:
					self.hitList[elem].append(tower)

	## Removes a certain tower from all places of the hitlist
	#  @param self The board
	#  @param tower The tower to be removed
	def removeFromHitList(self, tower):
		for elem, i in self.hitList.iteritems():
			if tower in self.hitList[elem]:
				self.hitList[elem].remove(tower)
	
	def getTowerPosition(self, tower_id):
		for pos, tower in self.tower.iteritems():
			if tower.ID == tower_id:
				return pos
		return None

	## Goes through the paths, and if there is an enemy unit, attack it.
	#  @param self The board
	#  @return a list of dicts describing the attacks made by towers
	def fireTowers(self):
		attacks = []
		deaths = []
		used = set()
		for pos, unit in self.units():
			for tower in self.hitList[pos]:
				if unit.health <= 0:
					break
				if tower not in used:
					used.add(tower)
					tower.fire(unit)
					attacks.append({
						'tower': tower,
						'tower_pos': self.getTowerPosition(tower.ID),
						'unit': unit,
						'unit_pos': pos
					})
					if unit.health <= 0:
						deaths.append({
							'unit': unit,
							'unit_pos': pos
						})
		return attacks, deaths

	## Queue's the unit at the entrance of the path it is supposed to take.
	#  @param unit The unit being placed
	#  @param q Which entrance the unit needs to go to
	def queueUnit(self, unit, q):
		if q in self.paths:
			if self.paths[q].moving is not None:
				self.paths[q].start(unit)
				return True
		return False

	## Return a generator of pairs of unit and position on the board,
	#  in order of increasing distance from the base
	def units(self):

		units = []
		
		for direction in constants.DIRECTIONS:
			path= self.paths[direction]
			for x in range (0, len(path.path)):
				if(path.moving[x] != None):
					units.append((path.path[x], path.moving[x]))

		return units

	def get_adjacent(self, pos, choices):
		x1, y1 = pos
		for x2, y2 in choices:
			# Adjacent if the Manhattan distance is 1
			if abs(x1 - x2) + abs(y1 - y2) == 1:
				return (x2, y2)
		return None

	## Advance the board state.
	#  Incoming units move forward, ones reaching the base do damage
	# @return: damage to be dealt to the player
	def moveUnits(self):
		units = []
		for path in self.paths.itervalues():
			unit = path.advance()
			pos = self.get_adjacent(path.path[0], self.base)
			if unit is not None and unit.health > 0:
				units.append({
					'unit': unit,
					'base_pos': pos
				})
		return units

	## Return the tower list
	def getTowers(self):
		return self.tower
