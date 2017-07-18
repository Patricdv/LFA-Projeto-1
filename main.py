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

noTerminals = []
terminals = []
automaton = []
finals = []
especialNoTerminalUsed = 0

determinizedAutomaton = []

reachableNoTerminals = []
alreadyViewed = []

livableNoTerminals = []
noTerminalsReachs = []

def makeAutomaton(model):
	iteration = 0
	global especialNoTerminalUsed
	for line in model:
		line = line.replace(" ", "")

		if line[0] != '<' or line[2] != '>':
			print 'error on no terminal declaration'
			return 0

		automaton.append(AutomatonLine('', [], {}))

		actualNoTerminal = line[1]
		noTerminals.append(actualNoTerminal)
		automaton[iteration].noTerminalName = actualNoTerminal
		automaton[iteration].composition.append(actualNoTerminal)

		if line[3] != ':' or line[4] != ':' or line[5] != '=':
			print 'error on atribuition declaration'
			return 0

		position = 6;

		while line[position] != ';':
			if line[position].isalpha():
				# Testa se eh o terminal especial 'se'
				if line[position] == 's' and line[position + 1] == 'e':
					position += 1
					actualTerminal = "se"

					# Testa se eh o terminal especial 'senao'
					if line[position + 1] == 'n' and line[position + 2] == 'a' and line[position + 3] == 'o':
						position += 3
						actualTerminal = "senao"

				# Testa se eh o terminal especial 'entao'
				elif line[position] == 'e' and line[position + 1] == 'n' and line[position + 2] == 't'  and line[position + 3] == 'a' and line[position + 4] == 'o':
					position += 4
					actualTerminal = "entao"

				else:
					actualTerminal = line[position]

				# Atribui o terminal lido para a lista de terminais caso ele nao tenha sido colocado ainda
				if actualTerminal not in terminals:
					terminals.append(actualTerminal)

				# Cria o vetor vazio de productions, para armazenar os nao-terminais
				if actualTerminal not in automaton[iteration].productions:
					automaton[iteration].productions[actualTerminal] = []

				# Testa se eh um terminal sozinho, pois precisa levar a um estado reservado
				if line[position + 1] == '|':
					automaton[iteration].productions[actualTerminal].append(0)
					especialNoTerminalUsed += 1

				# Testa se apos o terminal ha um nao-terminal e coloca ele na lista do automato
				if line[position + 1] == '<':
					position += 2
					automaton[iteration].productions[actualTerminal].append(line[position])
					position += 1

			elif line[position] == '&':
				finals.append(actualNoTerminal)

			position += 1

		iteration += 1

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

## Main
file = open("base", "r");
model = file.readlines();
makeAutomaton(model)
file.close();

## Making Basic CSV:
finiteAutomaton = open("finite-automaton.csv", "wb")
finiteAutomaton.write("")

## Making Determinized CSV:
determinizedAutomatonFile = open("determinized-automaton.csv", "wb")
determinizedAutomatonFile.write("")

## Making without useless states CSV:
withoutUselessStatesAutomatonFile = open("without-useless-states-automaton.csv", "wb")
withoutUselessStatesAutomatonFile.write("")

## Making without dead states CSV:
withoutDeadStatesAutomatonFile = open("without-dead-states-automaton.csv", "wb")
withoutDeadStatesAutomatonFile.write("")

# Coloca as colunas de terminais no topo
for terminal in terminals:
	finiteAutomaton.write(";" + str(terminal))

finiteAutomaton.write("\n")

# Comeca as linhas do automato
for automatonLine in automaton:
	# Testa se o nao-terminal eh um estado final
	if (automatonLine.noTerminalName in finals):
		finiteAutomaton.write("*")

	# Escreve o nao-terminal
	finiteAutomaton.write(str(automatonLine.noTerminalName))

	# Produz as colunas de producoes dos terminais
	for terminal in terminals:
		if terminal not in automatonLine.productions.keys():
			finiteAutomaton.write("; X")
		else:
			finiteAutomaton.write("; ")
			count = 0
			for target in automatonLine.productions[terminal]:
				count += 1
				if count > 1 :
					finiteAutomaton.write(', ')
				finiteAutomaton.write(str(target))
	finiteAutomaton.write("\n")

# Caso o nao-terminal especial de terminal sozinho tenha sido usado, ele eh impresso depois
if especialNoTerminalUsed > 0:
	finiteAutomaton.write("0")
	for terminal in terminals:
		finiteAutomaton.write("; X")
	finiteAutomaton.write("\n")

# Por fim eh imprimido o estado de erro
finiteAutomaton.write("X")
for terminal in terminals:
	finiteAutomaton.write("; X")
finiteAutomaton.write("\n")

makeDeterminization(automaton)

for automatonLine in automaton:
	# Testa se o nao-terminal eh um estado final
	if (automatonLine.noTerminalName in finals):
		determinizedAutomatonFile.write("*")

	# Escreve o nao-terminal
	determinizedAutomatonFile.write(str(automatonLine.noTerminalName))

	# Produz as colunas de producoes dos terminais
	for terminal in terminals:
		if terminal not in automatonLine.productions.keys():
			determinizedAutomatonFile.write("; X")
		else:
			determinizedAutomatonFile.write("; ")
			count = 0
			for target in automatonLine.productions[terminal]:
				count += 1
				if count > 1 :
					determinizedAutomatonFile.write(', ')
				determinizedAutomatonFile.write(str(target))
	determinizedAutomatonFile.write("\n")

removeUnusedStates(automaton)

for automatonLine in automaton:
	# Testa se o nao-terminal eh um estado final
	if (automatonLine.noTerminalName in finals):
		withoutUselessStatesAutomatonFile.write("*")

	# Escreve o nao-terminal
	withoutUselessStatesAutomatonFile.write(str(automatonLine.noTerminalName))

	# Produz as colunas de producoes dos terminais
	for terminal in terminals:
		if terminal not in automatonLine.productions.keys():
			withoutUselessStatesAutomatonFile.write("; X")
		else:
			withoutUselessStatesAutomatonFile.write("; ")
			count = 0
			for target in automatonLine.productions[terminal]:
				count += 1
				if count > 1 :
					withoutUselessStatesAutomatonFile.write(', ')
				withoutUselessStatesAutomatonFile.write(str(target))
	withoutUselessStatesAutomatonFile.write("\n")

removeDeadStates(automaton)

for automatonLine in automaton:
	# Testa se o nao-terminal eh um estado final
	if (automatonLine.noTerminalName in finals):
		withoutDeadStatesAutomatonFile.write("*")

	# Escreve o nao-terminal
	withoutDeadStatesAutomatonFile.write(str(automatonLine.noTerminalName))

	# Produz as colunas de producoes dos terminais
	for terminal in terminals:
		if terminal not in automatonLine.productions.keys():
			withoutDeadStatesAutomatonFile.write("; X")
		else:
			withoutDeadStatesAutomatonFile.write("; ")
			count = 0
			for target in automatonLine.productions[terminal]:
				count += 1
				if count > 1 :
					withoutDeadStatesAutomatonFile.write(', ')
				withoutDeadStatesAutomatonFile.write(str(target))
	withoutDeadStatesAutomatonFile.write("\n")

withoutDeadStatesAutomatonFile.write("X")
for terminal in terminals:
	withoutDeadStatesAutomatonFile.write("; X")
withoutDeadStatesAutomatonFile.write("\n")
