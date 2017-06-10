class AutomatonLine(object):
	def __init__(self, noTerminalName = "", productions = {}):
		self.noTerminalName = noTerminalName
		self.productions = productions

noTerminals = []
terminals = []
automaton = []
finals = []

def makeAutomaton(model):
	iteration = 0
	for line in model:
		line = line.replace(" ", "")

		if line[0] != '<' or line[2] != '>':
			print 'error on no terminal declaration'
			return 0

		automaton.append(AutomatonLine('', {}))

		actualNoTerminal = line[1]
		noTerminals.append(actualNoTerminal)
		automaton[iteration].noTerminalName = actualNoTerminal

		if line[3] != ':' or line[4] != ':' or line[5] != '=':
			print 'error on atribuition declaration'
			return 0

		position = 6;

		while line[position] != ';':
			if line[position].isalpha():
				if line[position] not in terminals:
					terminals.append(line[position])

				actualTerminal = line[position]
				if actualTerminal not in automaton[iteration].productions:
					automaton[iteration].productions[actualTerminal] = []

				# Testa se eh um terminal sozinho, pois precisa levar a um estado reservado
				if line[position + 1] == '|':
					automaton[iteration].productions[actualTerminal].append(0)

				# Testa se apos o terminal ha um nao-terminal e coloca ele na lista do automato
				if line[position + 1] == '<':
					position += 2
					automaton[iteration].productions[actualTerminal].append(line[position])
					position += 1

			elif line[position] == '&':
				finals.append(actualNoTerminal)

			position += 1

		iteration += 1

## Main
file = open("base", "r");
model = file.readlines();
makeAutomaton(model)
file.close();

## Making Basic CSV:
finiteAutomaton = open("finite-automaton.csv", "wb")
finiteAutomaton.write(" ")

for terminal in terminals:
	finiteAutomaton.write(";" + str(terminal))

finiteAutomaton.write("\n")

for automatonLine in automaton:
	if (automatonLine.noTerminalName in finals):
			finiteAutomaton.write("*")
	finiteAutomaton.write(str(automatonLine.noTerminalName))
	for terminal in terminals:
		if terminal not in automatonLine.productions.keys():
			finiteAutomaton.write("; x")
		else:
			finiteAutomaton.write("; ")
			count = 0
			for target in automatonLine.productions[terminal]:
				count += 1
				if count > 1 :
					finiteAutomaton.write(', ')
				finiteAutomaton.write(str(target))
	finiteAutomaton.write("\n")
