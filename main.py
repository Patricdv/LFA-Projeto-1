class AutomatonLine(object):
	def __init__(self, noTerminalName = "", composition = [], productions = {}):
		self.noTerminalName = noTerminalName
		self.composition = composition
		self.productions = productions

class determinizedAutomatonLines(object):
	def __init__(self, noTerminalName = "", composition = []):
		self.noTerminalName = noTerminalName
		self.composition = composition

class automatonReach(object):
	def __init__(self, noTerminalName = "", reachs = [], final = 0):
		self.noTerminalName = noTerminalName
		self.reachs = reachs
		self.final = 0

class tokensUsed(object):
	def __init__(self, letter = "", noTerminalName = ""):
		self.letter = letter;
		self.noTerminalName = noTerminalName;

noTerminals = []
terminals = []
automaton = []
finals = []
especialNoTerminalUsed = 0
determinizedAutomaton = []

tokens = []
tokenCount = 0

reachableNoTerminals = []
alreadyViewed = []

livableNoTerminals = []
noTerminalsReachs = []

def makeAutomaton(model):
	global especialNoTerminalUsed
	for line in model:
		line = line.replace(" ", "").replace("\r", "").replace("\n", "").split("::=")

		lineAutomaton = line[0]
		lineArguments = line[1].split("|")

		if lineAutomaton[0] != '<' or lineAutomaton[2] != '>':
			print 'error on no terminal declaration'
			return 0

		automaton.append(AutomatonLine('', [], {}))
		iteration = len(automaton) - 1

		actualNoTerminal = lineAutomaton[1]
		noTerminals.append(actualNoTerminal)
		automaton[iteration].noTerminalName = actualNoTerminal
		automaton[iteration].composition.append(actualNoTerminal)

		for argument in lineArguments:
			if argument == '&':
				finals.append(actualNoTerminal)

			else:
				if ((len(argument) == 1) or ('<' in argument and '>' in argument)):
					if len(argument) == 1:
						actualTerminal = argument
						production = 0
						especialNoTerminalUsed += 1

					if '<' in argument and '>' in argument:
						argument = argument.replace(">", "").split("<")
						actualTerminal = argument[0]
						production = argument[1]

					if actualTerminal not in terminals:
						terminals.append(actualTerminal)

					if actualTerminal not in automaton[iteration].productions:
						automaton[iteration].productions[actualTerminal] = []

					automaton[iteration].productions[actualTerminal].append(production)

				else:
					# Is here that build tokens porra!
					makeTokenTree(argument, iteration)

		iteration += 1

def makeTokenTree(argument, localIteration):
	position = 0
	length = len(argument)
	global tokenCount

	for letter in argument:
		position += 1
		createToken = 0
		automatonNoTerminal = 0

		if letter not in terminals:
			terminals.append(letter)

		if letter not in automaton[localIteration].productions:
			automaton[localIteration].productions[letter] = []

		if not tokens:
			createToken = 1
		else:
			for token in tokens:
				createToken = 1
				if letter == token.letter:
					createToken = 0
					automatonNoTerminal = token.noTerminalName
					break

		if createToken == 1:
			tokenCount += 1

			tokens.append(tokensUsed(letter, tokenCount))
			noTerminals.append(tokenCount)
			automaton[localIteration].productions[letter].append(tokenCount)

			automaton.append(AutomatonLine(tokenCount, [], {}))
			localIteration = len(automaton) - 1
			if position == length:
				finals.append(tokenCount)
		else:
			if automatonNoTerminal not in automaton[localIteration].productions[letter]:
				automaton[localIteration].productions[letter].append(automatonNoTerminal)

			count = 0
			for line in automaton:
				if automatonNoTerminal == line.noTerminalName:
					localIteration = count
				count += 1

def agroupNoTerminals(AutomatonLines, determinizedAutomaton):
	for index in determinizedAutomaton:
		if index.noTerminalName in noTerminals:
			continue

		noTerminals.append(index.noTerminalName)
		automaton.append(AutomatonLine(index.noTerminalName, index.composition, {}))
		automatonPosition = len(automaton) - 1

		for part in index.composition:
			if part in finals:
				finals.append(index.noTerminalName)
				break

		for element in automaton:
			if element.noTerminalName in index.composition:
				for production in element.productions.keys():
					if production not in automaton[automatonPosition].productions:
						automaton[automatonPosition].productions[production] = []

					for value in element.productions[production]:
						if value not in automaton[automatonPosition].productions[production]:
							automaton[automatonPosition].productions[production].append(value)

def makeDeterminization(AutomatonLines):
	indeterminizedTerminals = 0

	for automatonLine in AutomatonLines:
		for terminal in automatonLine.productions:
			if len(automatonLine.productions[terminal]) > 1:
				indeterminizedTerminals = 1
				newNoTerminal = '[' + ''.join(sorted(automatonLine.productions[terminal])) + ']'
				determinizedAutomaton.append(determinizedAutomatonLines(newNoTerminal, automatonLine.productions[terminal]))
				automatonLine.productions[terminal] = [newNoTerminal]

	if indeterminizedTerminals == 1:
		agroupNoTerminals(AutomatonLines, determinizedAutomaton)
		makeDeterminization(AutomatonLines)

def reachNoTerminals(AutomatonLines, reachableNoTerminals, alreadyViewed):
	changes = 0

	for automatonLine in AutomatonLines:
		if automatonLine.noTerminalName not in alreadyViewed:
			if automatonLine.noTerminalName in reachableNoTerminals:
			 	alreadyViewed.append(automatonLine.noTerminalName)

				for terminal in automatonLine.productions:
					if automatonLine.productions[terminal][0] not in reachableNoTerminals:
						reachableNoTerminals.append(automatonLine.productions[terminal][0])
						changes = 1

	if changes == 1:
		reachNoTerminals(AutomatonLines, reachableNoTerminals, alreadyViewed)

def removeUnusedStates(AutomatonLines):
	firstState = AutomatonLines[0] # Eh considerado que o primeiro estado do arquivo base e o primeiro estado
	reachableNoTerminals.append(firstState.noTerminalName)
	alreadyViewed.append(firstState.noTerminalName)

	for terminal in firstState.productions:
		if firstState.productions[terminal][0] not in reachableNoTerminals:
			reachableNoTerminals.append(firstState.productions[terminal][0])

	reachNoTerminals(AutomatonLines, reachableNoTerminals, alreadyViewed)

	for automatonLine in AutomatonLines[:]:
		if automatonLine.noTerminalName not in reachableNoTerminals:
			AutomatonLines.remove(automatonLine)

def findEndStates(AutomatonLines, noTerminalsReachs, livableNoTerminals):
	changes = 0

	for noTerminal in noTerminalsReachs:
		if noTerminal.final == 0:
			for reach in noTerminal.reachs:
				if reach in livableNoTerminals:
					livableNoTerminals.append(noTerminal.noTerminalName)
					noTerminal.final = 1
					changes = 1
					break

	if changes == 1:
		findEndStates(AutomatonLines, noTerminalsReachs, livableNoTerminals)

def removeDeadStates(AutomatonLines):
	for automatonLine in AutomatonLines:
		if automatonLine.noTerminalName not in finals:
			stateNoTerminals = []
			for terminal in automatonLine.productions:
				if automatonLine.productions[terminal][0] not in stateNoTerminals:
					stateNoTerminals.append(automatonLine.productions[terminal][0])
			noTerminalsReachs.append(automatonReach(automatonLine.noTerminalName, stateNoTerminals, 0))
		else:
			livableNoTerminals.append(automatonLine.noTerminalName)

	findEndStates(AutomatonLines, noTerminalsReachs, livableNoTerminals)

	for automatonLine in AutomatonLines[:]:
		if automatonLine.noTerminalName not in livableNoTerminals:
			AutomatonLines.remove(automatonLine)

def makeAutomatonCsvFile(fileName, automaton):
	## Making without dead states CSV:
	automatonFile = open(fileName, "wb")
	automatonFile.write("")

	# Coloca as colunas de terminais no topo
	for terminal in terminals:
		automatonFile.write(";" + str(terminal))

	automatonFile.write("\n")

	for automatonLine in automaton:
		# Testa se o nao-terminal eh um estado final
		if (automatonLine.noTerminalName in finals):
			automatonFile.write("*")

		# Escreve o nao-terminal
		automatonFile.write(str(automatonLine.noTerminalName))

		# Produz as colunas de producoes dos terminais
		for terminal in terminals:
			if terminal not in automatonLine.productions.keys():
				automatonFile.write("; X")
			else:
				automatonFile.write("; ")
				count = 0
				for target in automatonLine.productions[terminal]:
					count += 1
					if count > 1 :
						automatonFile.write(', ')
					automatonFile.write(str(target))
		automatonFile.write("\n")

	# Caso o nao-terminal especial de terminal sozinho tenha sido usado, ele eh impresso depois
	if especialNoTerminalUsed > 0:
		automatonFile.write("0")
		for terminal in terminals:
			automatonFile.write("; X")
		automatonFile.write("\n")

	# Por fim eh imprimido o estado de erro
	automatonFile.write("X")
	for terminal in terminals:
		automatonFile.write("; X")
	automatonFile.write("\n")

## Main
print "Starting..."

print "Reading File"
file = open("base", "r");
model = file.readlines();

print "Making Automaton From File"
makeAutomaton(model)
file.close();

print "Determinizing..."
makeDeterminization(automaton)

print "Removing unused states..."
removeUnusedStates(automaton)

print "Removind dead states..."
removeDeadStates(automaton)

makeAutomatonCsvFile("final-determinized-automaton.csv", automaton)
print "Automaton generated and ready!"
