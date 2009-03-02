#!/usr/bin/python

import shlex
import math

class CalcError(Exception):
	pass

class Calc(object):

	operator_rassoc = ['^']
	operator_prec = {
		'('   : 0,
		')'   : 0,
		'<<'  : 1,
		'>>'  : 1,
		'+'   : 2,
		'-'   : 2,
		'*'   : 3,
		'/'   : 3,
		'^'   : 4,
		'%'   : 4,
		'mod' : 4,
	}
	constants = {
		'pi' : math.pi,
		'e'  : math.e,
	}
	functions = [
		'sqrt', 'floor', 'ceil',
	]
	op_fn = {
		'*'    : (2, lambda x, y: x*y),
		'/'    : (2, lambda x, y: x/y),
		'+'    : (2, lambda x, y: x+y),
		'-'    : (2, lambda x, y: x-y),
		'mod'  : (2, lambda x, y: x%y),
		'%'    : (2, lambda x, y: x%y),
		'^'    : (2, lambda x, y: x**y),
		'<<'   : (2, lambda x, y: int(x)<<int(y)),
		'>>'   : (2, lambda x, y: int(x)>>int(y)),
		'sqrt' : (1, math.sqrt),
		'floor': (1, math.floor),
		'ceil' : (1, math.ceil),
	}

	def __init__(self):

		pass

	def eval(self, expression):
		expression = expression.strip()
		return(self.rpn_eval(self.infix_to_rpn(expression)))

	def infix_to_rpn(self, s):
		lex = shlex.shlex(s)
		lex.wordchars += '.<>'
		stack_out = []
		stack_op = []
		
		token = True
		while token:
			prev_token = token
			token = lex.get_token()

			if token == '-' and (prev_token == True or prev_token in self.operator_prec):
				# We're dealing with a negative number
				token += lex.get_token()

			if token == '*':
				peek_token = lex.get_token()
				if peek_token == '*':
					token = '^'
				else:
					lex.push_token(peek_token)

			if token:
				if token in self.constants:
					stack_out.append(self.constants[token])
				elif token in self.functions:
					stack_op.append(token)
				elif token == ',':
					while stack_op and stack_op[-1] != '(':
						stack_out.append(stack_op.pop())
				elif token == '(':
					stack_op.append(token)
				elif token == ')':
					while stack_op and stack_op[-1] != '(':
						stack_out.append(stack_op.pop())
					if not stack_op:
						raise CalcError('Unmatched parenthesis')
					stack_op.pop()
				elif token in self.operator_prec:
					# Operator
					while \
						stack_op and ( \
							stack_op[-1] not in self.operator_prec or \
							( \
								(token not in self.operator_rassoc and self.operator_prec[token] <= self.operator_prec[stack_op[-1]]) or \
								(token in self.operator_rassoc and self.operator_prec[token] < self.operator_prec[stack_op[-1]]) \
							)
						):
						stack_out.append(stack_op.pop())
					stack_op.append(token)
				else:
					# Operand
					try:
						stack_out.append(float(token))
					except ValueError, e:
						raise CalcError('Invalid operand \'%s\'' % (token))
			#print '%-5s %-40s %-40s' % (token, stack_out, stack_op)

		if '(' in stack_op or ')' in stack_op:
			raise CalcError('Unmatched paranthesis')

		stack_op.reverse()
		stack_out += stack_op

		return(stack_out)
			
	def rpn_eval(self, stack):
		stack_out = []
		for token in stack:
			if token in self.op_fn:
				args_nr, func = self.op_fn[token]
				args = []
				try:
					for i in range(-args_nr, 0):
						args.append(stack_out.pop(i))
				except IndexError, e:
					raise CalcError('Insufficient operands for "%s" operator' % (token))
				stack_out.append(func(*args))
			else:
				stack_out.append(token)

		return(stack_out[0])

if __name__ == '__main__':
	calc = Calc()
	tests = [
		('2 + 5 * 10', 52),
		('-2 + 5', 3),
		('-2--5', 3),
		('10 - 1 + 5 * 3 / 2 * 10 + 20 * 10', 284),
		('10-1+5*3/2*10*10', 759),
		('2 * 5 * (2 + 10)', 120),
		('2.6 * 5', 13),
		('10 mod 3 mod 2', 1),
		('2 ^ 2 ^ 3', 256),
		('pi', 3.1415926535897931),
		('2 * (5+1) / 3 * (pi ^ 2)', 39.478417604357432),
		('2 * e', 5.4365636569180902),
		('2 ^ 3 + 2 ^ 3 ^ 4', 2417851639229258349412352.000000),
		('sqrt(9)', 3),
		('2 * sqrt(9)', 6),
		('sqrt(9) + 5 * 2', 13),
		('(sqrt(9) + 5) * 2', 16),
		('floor(pi)', 3),
		('-1 - 1', -2),
		('5 ** 5', 3125),
		('-2 ^ 2', -4),
	]

	for test in tests:
		infix, rslt_correct = test
		rslt = calc.eval(infix)
		if rslt != rslt_correct:
			print 'ERR: "%s". Got "%f", Need "%f"' % (infix, rslt, rslt_correct)
		else:
			print 'OK: "%s" = %s' % (infix, rslt)

#FIXME: ERROR		('-6.2-2^(3*pi)', 0),
#FIXME: ERROR		('-1.001^(-6.2-2^(3*pi))', 0),
