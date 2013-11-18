#!/usr/bin/env python3

from functools import reduce
import operator, sys

class Applicable:
	"""Basic interface for all Unlambda expressions"""

	def apply(self, argument):
		"""Returns the result of applying this Unlambda expression to another"""
		return Applicable()

	def value(self):
		"""Returns the result of evaluating the Unlambda expression"""
		return self

	def __call__(self, argument):
		"""Shorthand for creating an Application object"""
		return Application(self, argument)

	def __repr__(self):
		return "<Unlambda: {0}>".format(str(self))

class Function(Applicable):
	"""Builtins

	All Unlambda builtins are instances of this class.

	The class returns the result of running a lambda against its arguments,
	once enough have been applied to it. A function is represented (usually)
	by a single letter, and has a list of previous arguments, should it be
	an intermediate of a multi-argument function's applications.

	When a single-argument function is applied, it simply returns the result
	of its lambda applied to the argument (preceeded by the previous
	arguments, if any). A multi-argument function instead creates a Function
	instance with the same letter and the same lambda, but taking one
	argument less than it, and with a list of the previous arguments to pass
	on to the lambda eventually.

	"""

	def __init__(self, letter, arg_count, to_execute, *previous_arguments):
		self.letter = letter
		self.arg_count = arg_count
		self.to_execute = to_execute
		self.previous_arguments = previous_arguments


	def apply(self, argument):
		if self.arg_count < 2:
			return self.to_execute(*(self.previous_arguments + (argument,)))
		else:
			return Function(
				self.letter, self.arg_count - 1, self.to_execute, *(self.previous_arguments + (argument,)))

	def __str__(self):
		result = self.letter
		for p in self.previous_arguments:
			result = '!' + result + str(p)
		return result

	def __eq__(self, other):
		if type(other) != Function:
			return NotImplemented

		if self.letter is not other.letter or \
			self.arg_count is not other.arg_count or \
			len(self.previous_arguments) != len(other.previous_arguments):
			return False
		for x, y in zip(self.previous_arguments, other.previous_arguments):
			if x != y:
				return False
		return True

class Application(Applicable):
	"""An application of one Applicable to another.

	`<left><right>

	"""
	def __init__(self, left, right):
		self.left = left
		self.right = right

	def apply(self, argument):
		return Application(self, argument)

	def value(self):
		# Evaluates exactly one step, because continuations and shit.
		if type(self.left) is Application:
			return Application(self.left.value(), self.right)
		elif type(self.right) is Application and self.left != D:
			return Application(self.left, self.right.value())
		else:
			return self.left.apply(self.right)

	def replace_call_cc(self, argument):
		"""Recursively look for the place where the C function was applied, and replace its application with argument"""
		if self.left == C:
			return argument
		else:
			if type(self.left) is Application:
				return Application(self.left.replace_call_cc(argument), self.right)
			else:
				return Application(self.left, self.right.replace_call_cc(argument))

	def __str__(self):
		return "`{0}{1}".format(self.left, self.right)

	def __eq__(self, other):
		if type(other) != Application:
			return NotImplemented
		else:
			return self.left == other.left and self.right == other.right

stdout = sys.stdout
stdin = sys.stdin

class Dot(Function):
	"""Printing function"""
	def __init__(self, letter):
		global stdout
		Function.__init__(self, '.' + letter, 1, lambda x: ([stdout.write(letter), x])[1])

	def __eq__(self, other):
		return (self.letter == other.letter) if type(other) == Dot else NotImplemented


class Continuation(Applicable):
	"""A continuation object. Raises its program and argument when applied."""
	def __init__(self, program):
		self.program = program

	def apply(self, argument):
		raise ContinuationApplied(self.program, argument)

	def __eq__(self, other):
		return (self.program == other.program) if type(other) == Continuation else NotImplemented

	def __str__(self):
		return "<continuation {0}>".format(self.program)

class ContinuationCreated(Exception):
	def __init__(self, argument):
		self.argument = argument

class ContinuationApplied(Exception):
	def __init__(self, program, argument):
		self.program = program
		self.argument = argument

	def __repr__(self):
		return '<Application of Continuation at {0} to {1}>'.format(repr(self.program), repr(self.argument))

	def __str__(self):
		return repr(self)

class ProgramExit(Exception):
	def __init__(self, argument):
		self.argument = argument

def _raise_(e):
	raise e

current_character = ''
def _getchar(x):
	global current_character
	try:
		current_character = stdin.read(1)
	except KeyboardInterrupt:
		current_character = ''
	finally:
		return x(I if len(current_character) > 0 else V)

class QuestionMark(Function):
	"""The ?x function"""
	def __init__(self, character):
		self.character = character
		Function.__init__(self, '?' + character, 1, lambda x: I if current_character == self.character else V)

	def __eq__(self, other):
		return (self.character == other.character) if type(other) == QuestionMark else NotImplemented


I = Function('i', 1, lambda x: x)
K = Function('k', 2, lambda x, y: x)
S = Function('s', 3, lambda x, y, z: x(z)(y(z)))
V = Function('v', 1, lambda x: V)
D = Function('d', 2, lambda x, y: x(y))
C = Function('c', 1, lambda x: _raise_(ContinuationCreated(x)))
R = Function('r', 1, Dot('\n').to_execute)
E = Function('e', 1, lambda x: _raise_(ProgramExit(x)))
At = Function('@', 1, lambda x: _getchar(x))
Pipe = Function('|', 1, lambda x: x(V if len(current_character) == 0 else Dot(current_character)))

Primitives = {str(x): x for x in [I, K, S, V, D, C, R, E, At, Pipe]}

def _recursive_parse_string(string):
	"""Recursively parse Unlambda code.

	This function retuns the parsed expression, as well as the number of characters it came to.

	"""

	# Measure its current length, and its length after skipping whitespace
	old_length = len(string)
	string = string.lstrip()
	skipped = old_length - len(string)

	# Next, skip all comments
	while string[0] == '#':
		try:
			len_ = string.index('\n') # Our new formula assures nondysfunctionality even under Windows
			string = string[len_:]
			skipped += len_
		except ValueError:
			skipped += len(string)
			string = ''

		# Strip all whitespace in next line
		old_length = len(string)
		string = string.lstrip()
		skipped += old_length - len(string)

	if string[0] in Primitives.keys():
		return [Primitives[string[0]], 1 + skipped]
	elif string[0] is '.':
		return[Dot(string[1]), 2 + skipped]
	elif string[0] is '?':
		return[QuestionMark(string[1]), 2 + skipped]
	elif string[0] is '`':
		left, left_skip = _recursive_parse_string(string[1:])
		right, right_skip = _recursive_parse_string(string[1 + left_skip:])
		return [Application(left, right), 1 + left_skip + right_skip + skipped]
	else:
		raise ValueError("Unparsable code: {0}".format(string))

def _parse(string):
	return _recursive_parse_string(string)[0]

def _run(applicable, verbose=False, output=sys.stdout, input_=sys.stdin):
	global stdout, stdin
	stdout = output
	stdin = input_

	result = None
	while type(applicable) is Application:
		try:
			applicable = applicable.value()
		except ProgramExit as e:
			applicable = e.argument
		except ContinuationCreated as e:
			# The C Function was applied to an argument!
			applicable = applicable.replace_call_cc(Application(e.argument, Continuation(applicable)))
		except ContinuationApplied as e:
			# A continuation has been applied to an argument!
			applicable = e.program.replace_call_cc(e.argument)
		finally:
			# If using verbose mode, append the current result
			if verbose:
				result = (result or []) + [applicable]
				print(applicable)
	return result or applicable

def run_program(program, **kargs):
	return _run(_parse(program), **kargs)

if __name__ == '__main__':
	code = ""
	while True:
		try:
			code += (input('$' if code is '' else '> ') + '\n').lstrip()
		except (KeyboardInterrupt, EOFError):
			sys.exit(0)


		try:
			parsed = _parse(code)
			code = ''
			_run(parsed)
		except IndexError:
			pass
		except ValueError as e:
			print("Error parsing code: {0}".format(str(e)))
			code = ''
