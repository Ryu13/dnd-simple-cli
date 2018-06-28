#!/usr/bin/python
import sys, getopt, operator, json, math

keepTurn = False
monsters = []
players = []
commands = [
			{'text': "Skip -- skips current turn and moves onto the next creature in the initiative order", 'action': True},
			{'text': "Add Player -- Adds a player to the battle", 'action': False, 'function': 'addPlayer'}, 
			{'text': 'Remove Creature -- Removes a creature from the battle', 'action': False, 'function': 'removeCreature'},
			{'text': "Attack -- Current turn applies damage to target monster; ends turn after", 'action': True, 'function': 'attack'}, 
			{'text': "Apply Damage -- Applies damage to target (only monster supported); does not end turn after", 'action': False, 'function': 'applyDamage'},
			{'text': "List Players", 'action': False, 'function': 'listPlayers'},
			{'text': "List Monsters", 'action': False, 'function': 'listMonsters'},
			{'text': 'List Creatures', 'action': False, 'function': 'listCreatures'}
]
BREAK_LINE = '----------------------------------'

# TODO: move me to util file
def _isNewline(string):
	return string == '\n' or string == '\r\n'

def _isEmptyInput(string):
	return string == '' or _isNewline(string)

# TODO: move me to util file 
def _getNonEmptyInput(message):
	_input = raw_input(message)
	while _isEmptyInput(_input):
		_input = raw_input(message)
	return _input

def _tryInt(_input):
	try:
		int(_input)
	except ValueError:
		print 'input (' + _input + ') must be an integer'
		return False

def _getNonEmptyIntInput(message):
	_input = raw_input(message)
	while _tryInt(_input) == False:
		_input = raw_input(message)
	return _input


# TODO: move me to a util file
def getModifier(_value):
	value = int(_value)
	mod = (value - 10) / 2
	return int(math.floor(mod))

# used in case of a tie on initial initiative rolls
def getSecondaryInit(creature):
	if creature.has_key("STATS") and creature["STATS"].has_key("DEX"):
		dexStat = getModifier(creature["STATS"]["DEX"])
	else:
		dexStat = _getNonEmptyInput("Require DEX for " + creature["NAME"] + ": ")		
		if (not creature.has_key("STATS")):
			creature["STATS"] = {}
			
		creature["STATS"]["DEX"] = dexStat
	dexMod = getModifier(dexStat)
	return dexMod

# used in case of a tie on initial initiative rolls and tie on DEX mod
def getNthInit(creature):
	return _getNonEmptyInput("Initiative roll for " + creature["NAME"] + "\n")

# This should read in a file and grab any applicable data
# ATM this only covers monsters. If more data should be extracted, this should be a wrapper method for explicit data extraction methods
# Players are not "closely" tracked and the user will later be prompted for player names / initiative
def readBattleFile(batFile):
	global monsters

	if batFile == '':
		print 'no battle to run, aborting'
		sys.exit(2)

	fileContents = open(batFile, 'r').read()
	data = json.loads(fileContents)

	if data["monsters"] == "" or len(data["monsters"]) == 0:
		print 'No enemies!'
		sys.exit(2)

	for monster in data["monsters"]:
		if "file" in monster:
			print 'Monster file option not yet supported'
			sys.exit(2)
			# TODO: load monster template from json file
		monster["TYPE"] = "monster"
		monsters.append(monster)
		
# Method to add a player with name and initiative
# This is a very non-invasive player tracker as this is designed to merely supplement the experience of
# 	either knowing a character's AC or asking the player whether some roll hits.
def addPlayer():
	global players

	if len(players) == 0: # must be at least 1 player
		playerName = raw_input("Player Name: ")
		while playerName == '' or _isNewline(playerName):
			playerName = raw_input("Player Name: ")
	else:
		playerName = raw_input("Player Name (blank for no more players): ")
		if playerName == '' or _isNewline(playerName): # done entering users, move on
			return False

	playerInit = _getNonEmptyIntInput(playerName + '\'s initiative: ')
	new_player = {"NAME": playerName, "INITIATIVE": playerInit, "TYPE": 'player'}
	new_player = json.dumps(new_player)
	new_player = json.loads(new_player)
	players.append(new_player)

	return True

# iterates through the array with optional _type and prints NAME value
def filterByType(arr, _type = ''):
	printTargets([itr for itr in arr if itr["TYPE"] == _type or _type == ''])
		# print itr["NAME"] + ' - ' + itr["TYPE"]

# lists all remaining players by filtering creatures for 'player' type
def listPlayers():
	print '\nCurrent players:'
	filterByType(creatures, 'player')
	print ''

# lists all remaining monsters by filtering creatures for 'monster' type
def listMonsters():
	print '\nCurrent monsters:'
	filterByType(creatures, 'monster')
	print ''

# lists all remaining creatures as they are ordered by initiative
def listCreatures():
	print '\nCurrent creatures:'
	filterByType(creatures)
	print ''

def removeCreature(targetCreature = None):
	global players
	global currentTurnCreature
	global creatures
	global keepTurn

	listCreatures()
	
	if targetCreature == None:
		name = raw_input("Remove which creature? ") 
		if _isEmptyInput(name):
			return
	else:
		name = targetCreature["NAME"]
	
	toRemIndex = None
	for i, creature in enumerate(creatures):
		if name == creature["NAME"]:
			toRemIndex = i
			break # remove outside of list iteration
	if toRemIndex is not None:
		currentTurnCreature = creatures[i-1] # set to previous so the skip action moves to next automatically
		keepTurn = name != creatures.pop(toRemIndex)["NAME"]
	
# TODO: addMonster coming later
def addMonster():
	print 'Add monster functionality is still being implemented.'

# This loops until no more players are desired to be added
def getPlayerInitiatives():
	keepLoop = True
	while keepLoop:
		keepLoop = addPlayer()
		
# This loops through all the added monsters and requests their rolled initiatives
def getMonsterInitiatives():
	global monsters
	for monster in monsters:
		monster["INITIATIVE"] = _getNonEmptyIntInput(monster["NAME"] + '\'s initiative: ')

# returns an unsorted set of creatures based on original players / monsters
def resetCreatures():
	_creatures = []
	_creatures.extend(monsters)
	_creatures.extend(players)
	return _creatures

# determines the battle order amongst players and monsters (or npcs)
def determineOrder():
	_creatures = resetCreatures()

	# highest first
	def creatureCompare(c1, c2):
		c1Init = c1["INITIATIVE"]
		c2Init = c2["INITIATIVE"]
		if c1Init == c2Init: #first tie goes to DEX mod
			c1Init = getSecondaryInit(c1)
			c2Init = getSecondaryInit(c2)
			
			while c1Init == c2Init: #second+ tie(s) go to re-rolls
				c1Init = getNthInit(c1)
				c2Init = getNthInit(c2)
		return int(c2Init) - int(c1Init)

	return sorted(_creatures, cmp=creatureCompare)

def listCommands():
	global commands

	print 'Commands: '
	for index, cmd in enumerate(commands):
		print str(index + 1) + ': ' + cmd["text"]
	print ''

# searches for a target given the target name
def determineValidTarget(givenTargetName):
	global monsters
	global players
	global creatures

	monsterItr = 0
	for monster in monsters:
		if givenTargetName == monster["NAME"] or int(givenTargetName) == (monsterItr + 1):
			return monster
		monsterItr = monsterItr + 1
	print 'searching players'
	for player in players:
		if givenTargetName == player["NAME"]:
			print 'Attacking players is not yet supported. Please verbally notify player of their damage.'
			return None
	print 'Creature with name: ' + givenTargetName + ' was not found amongst existing creatures'
	print creatures
	return None

#tracking attacks on players coming later
def attack():
	global currentTurnCreature
	global monsters

	targets = []
	_type = currentTurnCreature["TYPE"]
	if _type == "player":
		targets = monsters
	printTargets(targets)
	monster = None
	while monster is None:
		target = raw_input("Who is getting attacked? ")
		if target == '':
			break
		monster = determineValidTarget(target)		
		if monster is not None:
			monsterName = monster["NAME"]
			if not monster.has_key('currentHP'):
				monster['currentHP'] = monster["HP"]
			health = int(monster['currentHP'])
			damage = int(raw_input("How much was " + monsterName + " hit for? "))
			monster['currentHP'] = health - damage

			if monster['currentHP'] <= 0: # dead
				print monsterName + " was slain."
				removeCreature(monster)

	print BREAK_LINE

#TODO: make for creatures instead of monsters
def applyDamage():
	global keepTurn
	global monsters
	global currentTurnCreature

	target = raw_input("To whom is damage being applied?\n")
	amount = raw_input("How much damage is being applied?\n")

	if target != '':
		damage = int(amount)
		targetMonster = None
		for monster in monsters:
			print 'monster: ' + monster["NAME"]
			if monster["NAME"] == target:
				targetMonster = monster
		if targetMonster == None:
			print 'target monster not found'
			return
		if not targetMonster.has_key('currentHP'):
			targetMonster["currentHP"] = targetMonster["HP"]
		health = int(targetMonster["currentHP"])
		targetMonster["currentHP"] = health - damage
		
		if targetMonster["currentHP"] <= 0:
			print target + " was slain."
			removeCreature(targetMonster)
			if currentTurnCreature["NAME"] == target:
				keepTurn = False # do not keep turn if monster was slain...
				return


def commandSwitch(commandText):
	global monsters
	global players
	global commands
	global keepTurn

	commandLoop = True
	while commandLoop: # loop if user entered invalid command
		for i in range(0, len(commands)):
			command = commands[i]
			if commandText.lower() == command["text"].lower() or int(commandText) == (i + 1):
				commandLoop = False
				# executed prior to function execution in the event the function wishes to override the keepTurn
				keepTurn = command["action"] != True # if not an action, keep turn
				if command.has_key('function'):
					globals()[command["function"]]()
		if commandLoop:
			print 'Invalid command: ' + commandText + '\n'
			listCommands()
			commandText = _getNonEmptyInput("What would you like to do? ")

	return len(monsters) > 0 and len(players) > 0 # if there are both monsters and players remaining

def printTargets(targets):
	print BREAK_LINE
	targetItr = 0
	for target in targets:
		name = target["NAME"]
		armorClass = target["AC"] if target.has_key("AC") else '--'
		if target.has_key('currentHP'):
			remainingHealth = target["currentHP"]
		elif target.has_key("HP"):
			remainingHealth = target["HP"]
		else:
			remainingHealth = '--'

		if (remainingHealth != '--' and int(remainingHealth) <= 0): # do not print target if somehow present with no active health
			continue

		print str(targetItr + 1) + ". name: " + name + " ac: " + str(armorClass) + " health: " + str(remainingHealth)
		targetItr = targetItr + 1
	print BREAK_LINE

def determineTurn(previousCreatureTurn):
	global creatures

	if previousCreatureTurn is None:
		return creatures[0] #should always be sorted, highest init first
	else:
		for i in range(0, len(creatures)):
			if previousCreatureTurn["NAME"] == creatures[i]["NAME"]:
				return creatures[(i+1) % len(creatures)] #python lists should be cyclic
		print 'Could not find next creature'
		print 'Creature list:'
		print creatures
		print 'Previous creature\'s turn: '
		print previousCreatureTurn
		return -1

# Equivalent to a game's main event loop, when this ends, the battle should be over and the program will exit
def battleLoop():
	global currentTurnCreature
	global creatures
	global keepTurn	

	keepLoop = True
	creatures = determineOrder()
	while keepLoop:
		if keepTurn == False:
			currentTurnCreature = determineTurn(currentTurnCreature)
		keepTurn = False # done after the check so any preserved turn isn't ignored
		print '------------' + currentTurnCreature["NAME"] + '\'s turn ------------'
		listCommands()
		command = _getNonEmptyInput("What would you like to do? ")
		keepLoop = commandSwitch(command)
	
	exitMsg = 'All enemies have been defeated' if len(players) > 0 else 'All players have been defeated.'
	print 'Battle has ended -- ' + exitMsg

def main(argv):
	battleFile = ''
	try:
		opts, args = getopt.getopt(argv, "b:s:", ["battle=", "sample="])
	except getopt.GetoptError as err:
		print err
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-b', "--battle"):
			battleFile = arg
		elif opt in ('-s', '--sample'):
			battleFile = 'sample-battles/sample-battle-' + arg + '.json'
		else:
			assert False, "unhandled option"

	#monsters read in for battle
	readBattleFile(battleFile)

	#player name and initiatives read in
	getPlayerInitiatives()

	#monster initiatives
	getMonsterInitiatives()

	global creatures
	creatures = []


	global currentTurnCreature 
	currentTurnCreature = None

	# begins main event loop
	battleLoop()


if __name__ == "__main__":
	main(sys.argv[1:])


