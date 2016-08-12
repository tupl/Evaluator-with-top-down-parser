# Evaluate expression with top-down parser, allow for substitutes #

This is a Python project that built a recursive top-down parser on the
non-left recursive grammar. It first constructs a parse tree and then recursive
evaluates each node. When it sees a variable, it looks up for that variable
from a substitutes table.

Example:

(x+y)-16/z^2 = 5.0

Parse Tree

{'type': 'substract', 'value': '-'}
  {'type': 'addition', 'value': '+'}
    {'type': 'variable', 'value': 'x'}
    {'type': 'variable', 'value': 'y'}
  {'type': 'division', 'value': '/'}
    {'type': 'number', 'value': '16'}
    {'type': 'power', 'value': '^'}
      {'type': 'variable', 'value': 'z'}
      {'type': 'number', 'value': '2'}
