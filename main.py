from lark import Lark
import lark
import sys

try:
	fil=sys.argv[1]
except:
	fil = "test.stacc"

with open(fil, "r") as f:
	staccfile = f.read()

parser = Lark(open('stacclang.lark'))

tree = parser.parse(staccfile)

stacks = [[]]
stackptr = 0

reg = 0

def getArity(op):
	if   op == "q": return 0
	elif op == "s": return 0
	elif op == "d": return 0 # due to implementation-specific details, duplicating the top of the stack doesn't need any arguments
	elif op == "l": return 0

	elif op == "p": return 1
	elif op == "t": return 1
	elif op == "c": return 1
	elif op == "r": return 1

	elif op == "_": return 1
	elif op == "!": return 1

	elif op == "o": return 2

	elif op == "+": return 2
	elif op == "-": return 2
	elif op == "*": return 2
	elif op == "/": return 2
	elif op == "%": return 2
	elif op == "@": return 2
	elif op == "|": return 2
	elif op == "&": return 2
	elif op == "^": return 2
	elif op == "=": return 2
	elif op == "<": return 2
	elif op == ">": return 2

def evalAsBool(arg):
	"""returns false if 0 or empty string, else true"""
	if arg == 0 or arg == "":
		return False
	else:
		return True

def apply(op):
	global stacks, stackptr, reg
	"""handles applying operators to the stack"""
	stack = stacks[stackptr]
	args = []
	for _ in range(getArity(op)):
		args.insert(0, stack.pop())
	
	try:
		if   op == "q":
			inp = input()
			try:
				stack.append(eval(inp))
			except NameError:
				stack.append(inp)

		elif op == "p": print(args[0], end="")

		elif op == "d": stack.append(stack[-1])
		elif op == "o":
			stack.append(args[1])
			stack.append(args[0])

		elif op == "t": stackptr = args[0]
		elif op == "c": stackptr += args[0]
		elif op == "s": stack.append(stackptr)

		elif op == "r":
			reg = args[0]
		elif op == "l":
			stack.append(reg)

		elif op == "_": stack.append(-args[0])
		elif op == "!": stack.append(1 if evalAsBool(args[0]) else 0)

		elif op == "+": stack.append(args[0]+args[1])
		elif op == "-": stack.append(args[0]-args[1])
		elif op == "*": stack.append(args[0]*args[1])
		elif op == "/": stack.append(args[0]/args[1])
		elif op == "%": stack.append(args[0]%args[1])
		elif op == "@": stack.append(args[0]**args[1])
		elif op == "|": stack.append(1 if (evalAsBool(args[0]) or evalAsBool(args[1])) else 0)
		elif op == "&": stack.append(1 if (evalAsBool(args[0]) and evalAsBool(args[1])) else 0)
		elif op == "^": stack.append(1 if (evalAsBool(args[0]) ^ evalAsBool(args[1])) else 0)
		elif op == "=": stack.append(1 if (args[0] == args[1]) else 0)
		elif op == "<": stack.append(1 if (args[0] < args[1]) else 0)
		elif op == ">": stack.append(1 if (args[0] > args[1]) else 0)
	except IndexError:
		stacks.extend(((stackptr + 1) - len(stacks)) * [[]])
		apply(op)

def execute(tree):
	global stacks, stackptr, reg
	for child in tree.children:
		if isinstance(child, lark.lexer.Token):
			# print(child)
			if child.type == "NUMBER":
				try:
					stacks[stackptr].append(int(child))
				except IndexError:
					stacks.extend(((stackptr + 1) - len(stacks)) * [[]])
					stacks[stackptr].append(int(child))

			elif child.type == "STRING":
				try:
					stacks[stackptr].append(eval(str(child)))
				except IndexError:
					stacks.extend(((stackptr + 1) - len(stacks)) * [[]])
					stacks[stackptr].append(eval(int(child)))

			elif child.type == "OPERATOR":
				apply(child)

		else:
			if child.data == "if_statement":
				condition = stacks[stackptr].pop()
				if evalAsBool(condition):
					for grandchild in child.children[0].children:
						execute(grandchild)
				else:
					for grandchild in child.children[1].children[0].children:
						execute(grandchild)
			elif child.data == "while_statement":
				condition = stacks[stackptr].pop()
				while evalAsBool(condition):
					for grandchild in child.children[0].children:
						execute(grandchild)
					condition = stacks[stackptr].pop()

if len(sys.argv) == 1:
	while True:
		inp = input("> ")
		tree = parser.parse(inp)
		for child in tree.children:
			execute(child)
	exit()

for child in tree.children:
	execute(child)
