import unittest
import unlambda
from io import StringIO

class TestAAAParsing(unittest.TestCase):
	"""This test *has* to be run first, because we want to make sure we have a sane environment first"""
	def test_primitives(self):
		self.assertEqual(unlambda.I, unlambda._parse('i'))
		self.assertEqual(unlambda.S, unlambda._parse('s'))
		self.assertEqual(unlambda.K, unlambda._parse('k'))
		self.assertEqual(unlambda.V, unlambda._parse('v'))
		self.assertEqual(unlambda.D, unlambda._parse('d'))
		self.assertEqual(unlambda.Dot('*'), unlambda._parse('.*'))
		self.assertEqual(unlambda.R, unlambda._parse('r'))
		self.assertEqual(unlambda.E, unlambda._parse('e'))

		self.assertNotEqual(unlambda.I, unlambda._parse('.*'))
		self.assertNotEqual(unlambda.R, unlambda._parse('.\n'))
		self.assertRaises(IndexError, unlambda._parse, '.')
		self.assertRaises(ValueError, unlambda._parse, 'f')
		
		self.assertEqual(unlambda.C, unlambda._parse('c'))
		self.assertEqual(unlambda.At, unlambda._parse('@'))
		self.assertEqual(unlambda.Pipe, unlambda._parse('|'))
		self.assertEqual(unlambda.QuestionMark('x'), unlambda._parse('?x'))

	def test_simple_applications(self):
		exp = unlambda.Application(unlambda.S, unlambda.K)
		self.assertEqual(exp, unlambda._parse('`sk'))

		exp = unlambda.Application(unlambda.Dot('*'), unlambda.C)
		self.assertEqual(exp, unlambda._parse('`.*c'))
		
		exp = unlambda.Application(unlambda.C, unlambda.Dot('s'))
		self.assertEqual(exp, unlambda._parse('`c.s'))

		exp = unlambda.Application(unlambda.D, unlambda.D)
		self.assertEqual(exp, unlambda._parse('`dd'))

		self.assertNotEqual(unlambda._parse('`ik'), unlambda._parse('`ki'))

		self.assertRaises(IndexError, unlambda._parse, '`k')
		self.assertRaises(ValueError, unlambda._parse, '`kf')

	def test_nested_applications(self):
		exp = unlambda.Application(unlambda.Application(unlambda.S, unlambda.K), unlambda.I)
		self.assertEqual(exp, unlambda._parse('``ski'))

		exp = unlambda.Application(unlambda.Application(unlambda.Dot('s'), unlambda.Dot('k')), unlambda.Application(unlambda.Dot('i'), unlambda.Dot('v')))
		self.assertEqual(exp, unlambda._parse('``.s.k`.i.v'))

		exp = unlambda.Application(
			unlambda.Application(
				unlambda.D,
				unlambda.Application(unlambda.Dot('*'), unlambda.I)),
			unlambda.Application(unlambda.Dot('+'), unlambda.I))
		self.assertEqual(exp, unlambda._parse('``d`.*i`.+i'))

		self.assertNotEqual(unlambda._parse('``skk'), unlambda._parse('`s`kk'))

	def test_whitespace(self):
		"""whitespace and comments are the same thing as we all know"""

		exp = unlambda.Dot(' ')
		self.assertEqual(exp, unlambda._parse('. '))

		exp = unlambda.Dot('#')
		self.assertEqual(exp, unlambda._parse('.#'))

		self.assertRaises(IndexError, unlambda._parse, '`. #')

		self.assertEqual(unlambda._parse('``skk'), unlambda._parse('`  \t \t ` \ns\n\nk\t k    '))

		self.assertEqual(unlambda._parse('``skk'), unlambda._parse('\t #hello world ``ee\r\n`#lorem\r\n  #ipsum\r\n ` # do # lor \r\n#skk\r\nskk'))



class _ProgramTestCase(unittest.TestCase):
	def _assertPrints(self, code, output, input=''):
		out = StringIO()
		in_ = StringIO(input)
		unlambda._run(unlambda._parse(code), output=out, input_=in_)
		self.assertEqual(out.getvalue(), output)

	def _assertYields(self, code, value, input=''):
		in_ = StringIO(input)
		self.assertEqual(unlambda.run_program(code, input_=in_), unlambda._parse(value))

	def _assertNotYields(self, code, value, input=''):
		in_ = StringIO(input)
		self.assertNotEqual(unlambda.run_program(code, input_=in_), unlambda._parse(value))

class TestEvaluationOrder(_ProgramTestCase):
	def test_simple_prints(self):
		self._assertPrints('`.*i', '*')
		self._assertPrints('`.*r', '*')
		self._assertPrints('`.`i', '`')
		self._assertPrints('`rr', '\n')
		self._assertPrints('`i.*', '')

	def test_complex_prints(self):
		self._assertPrints('``.*ri', '*\n')
		self._assertPrints('```.U.n.li', 'Unl')

	def test_delays(self):
		self._assertPrints('`````kkd.*.+i', '*')
		self._assertPrints('``kd`.*i', '*')
		self._assertPrints('```kdi`ri', '')

class TestContinuations(_ProgramTestCase):
	def test_ifthenelse(self):
		"""This tests the classic if-then-else function as described in the Bible, section #howto_bool"""
		self._assertYields('``` ``s`kc``s`k`s`k`k`ki``ss`k`kk v s k', 'k')
		self._assertPrints('` ``` ``s`kc``s`k`s`k`k`ki``ss`k`kk v .T .F i', 'F')

	def test_church_nonezero(self):
		"""This tests the <test> function, as described in the Bible, section #howto_num."""
		self._assertYields('` ``s`kc``s`k`sv``ss`k`ki ``s``s`ksk``s``s`kski', 'i')

	def test_ingoing(self):
		"""*in*going continuations -- this is where it gets complicated and might fail.

		Continuations are usually implemented as Exceptions, but this won't do when
		the `ci expression is used. This expression, as you may have noticed, actually
		*is* a continuation. So whenever it is applied to anything, the program needs
		*to go back in time* to when the appropriate `ci was evaluated, and replaces it
		with whatever the continuation was applied to.

		In the following program, what happens is that first, `ci is evaluated, yielding:
			`<cont>.*
		Which then makes to program go back in time to
			` `ci .*
		And replaces the `ci with what the continuation was applied to: .*
			`.*.*
		Which prints an asterisk.

		"""
		self._assertPrints('` `ci .*', '*')

class TestInput(_ProgramTestCase):
	def test_reprint(self):
		"""Tries to supply a single character and reprint it"""
		self._assertPrints('` ``@`ki| ``si`ki', '#', '#')

	def test_input_based_flow_control(self):
		"""Tries to decide whether to print one string or another, based on the user's input"""

		# See input_notes.txt for the function's construction
		prog = """	``@
	   ``s``s``s
	            `k ``s`kc``s`k`s`k`k`ki``ss`k`kk # If...
	            i # Condition ($x)
	            `k``s
	                 ``s``s``s # Iftrue (<decide>)
	                          `k ``s`kc``s`k`s`k`k`ki``ss`k`kk # If...
	                          `d`?Yi # Condition (currchar == 'Y')
	                          `k.1 # Iftrue (.1)
	                          `d
	                            ``` ``s`kc``s`k`s`k`k`ki``ss`k`kk
	                                           `d`?Ni
	                                           `k.0
	                                           `k.e
	                 i
	            `k.E # Iffalse (<error1>)
	   i"""
		self._assertPrints(prog, '1', 'Y')
		self._assertPrints(prog, '0', 'N')
		self._assertPrints(prog, 'E', '')
		self._assertPrints(prog, 'e', 'f')

	def test_cat(self):
		prog = "```sii``s``s`kk ``s``s`k@`k ``s``s``s `k``s`kc``s`k`s`k`k`ki``ss`k`kk i `d`|i `k`d`ei `ki ``sii"
		self._assertPrints(prog, 'hello, world!', 'hello, world!')
		self._assertPrints(prog, 'the quick brown fox', 'the quick brown fox')
		self._assertPrints(prog, 'lorem\nipsum\n', 'lorem\nipsum\n')
if __name__ == '__main__':
	unittest.main()
