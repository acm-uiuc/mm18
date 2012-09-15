#! /usr/bin/env python

import constants
import json
import os
from collections import deque
from collections import defaultdict


"""
This is the board class.
It is where the code for the board goes.
"""

class Board:
	
	"""
	Board class. 
	The board consists of two lists and a dictionary.  The dictionary contains the locations of the towers (key is a tuple for location on the board, entry is a tower object).  The base list contains the tuple locations of the base - unordered.   The path list contains the tuple locations of the path, ordered starting with those closest to the base and working outwards.

	base -- a list of tuples that represent the base location
	path -- a list of tuples that represent the path locations (ordered in orderPathsByClosest method)
	"""
	def __init__(self, base, path):
		self.base = base
		self.path = path
		self.tower = {}
		self.qN = deque()
		self.qE = deque()
		self.qS = deque()
		self.qW = deque()
		self.hitList = defaultdict(list)

	"""
	Reads in json for the board layout from a file and sorts it into two lists one for base positions and the other for path positions
	"""
	@staticmethod
	def jsonLoad(filename):
		filePath = os.path.join(os.path.dirname(__file__), filename)
		data =json.load(open(filePath))
		bases = data['bases']
		baseList = [tuple(pair) for pair in bases]
		paths = data['paths']
		pathList = [tuple(pair) for pair in paths]
		return Board.orderPathsByClosest(baseList, pathList)


	"""
	Breadth-first search method that takes the unordered list of path locations and sorts them by how far from the base they are.

	baseList -- a list that contains the base locations
	pathList -- a list that contains the paths to the base in no order
	"""
	@staticmethod
	def orderPathsByClosest(baseList, pathList):
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
		return Board(baseList,outPath)

	"""
	Check whether the position of the object being inserted is a valid placement on the board.
	Will contain error handling for invalid positions.

	position -- tuple containing object position
	"""

	def validPosition(self, position):
		x,y=position
		return x >= 0 and y >=0 and x < constants.BOARD_SIDE and y < constants.BOARD_SIDE

	"""
	Adds an object to the board provided nothing is already in the location.
	Returns true if successful and false if not

	item -- an object, most likely a tower
	position -- a tuple for the position of the object
	"""
	def addItem(self, item, position):
		if self.validPosition(position) and self.getItem(position) == None and position not in self.base and position not in self.path:
			self.tower[position] = item
			return True
		else:
			return False

	"""
	Gets the item at the position or returns none if no object exists.
	Will contain error handling for something?
	If no error handling is needed class is unecessary and can be replaced just by the dict.get method.

	position -- a tuple containing object position
	"""
	def getItem(self, position):
		return self.tower.get(position,None)

	"""
	Removes the item at the position

	position -- a tuple containing object position
	"""
	def removeItem(self, position):
		if self.getItem(position) != None:
			del self.tower[position]


	"""
	Adds a tower to all the appropriate places of the hitList

	self -- the board
	tower -- the tower to add to the hitList
	"""
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
	

	"""
	Removes a certain tower from all places of the hitlist

	self -- the board
	tower -- the tower to be removed
	"""

	def removeFromHitList(self, tower):
		for elem, i in self.hitList.iteritems():
			for i in self.hitList[elem]:
				i.remove(tower)
			

	"""
	Goes through the path (orderPathByClosest ensures that it is ordered), and if there is an enemy unit, attack it.

	self -- the board
	"""
	
	def fireTowers(self):
		self.resetTowers() #load the cannons/catapults/death rays
		for p in self.path: #go through paths
			for u in self.unitList: #if a unit is standing there
				if p in self.unitList: 
					for t in self.hitList[p]: #Go through hitList at that spot
						if u.health >0 : #if the unit is NOT out of health
							t.fire(u) #fire the cannons/lasers/steam-propelled tesla coils 


	"""
	Reset towers to having not fired (called once before every fireTowers call)

	self-- the board
	"""

	def resetTowers(self):
		for t in self.tower:
			t.reset()

	def queueUnit(self, unit, q):

		"""
		Queue's the unit at the entrance of the path it is supposed to take.

		unit -- the unit being placed
		q --  which entrance the unit needs to go to
		"""

		if q == 1:
			qN.append(unit)
			return true
		elif q == 2:
			qE.append(unit)
			return true
		elif q == 3:
			qS.append(unit)
			return true
		elif q == 4:
			qW.append(unit)
			return true
		return false
