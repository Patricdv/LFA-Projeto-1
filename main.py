class AutomatonLine(object):
	def __init__(self, noTerminalName = "", productions = {}):
		self.noTerminalName = noTerminalName
		self.productions = productions

noTerminals = []
terminals = []
automaton = []
finals = []
especialNoTerminalUsed = 0

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

## Main
file = open("base", "r");
model = file.readlines();
makeAutomaton(model)
file.close();

## Making Basic CSV:
finiteAutomaton = open("finite-automaton.csv", "wb")
finiteAutomaton.write(" ")

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
