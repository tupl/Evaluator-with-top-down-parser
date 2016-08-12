import re
import sys
import math

definitions = [
    ("paren_open", "\("),
    ("paren_close", "\)"),
    ("multiply", "\*"),
    ("substract", "\-"),
    ("addition", "\+"),
    ("division", "\/"),
    ("number", "\d+"),
    ("assignment", "="),
    ("power", "\^"),
    ("variable", "[A-Za-z]+[A-Za-z0-9]*")
]

class Lexer(object):
    def __init__(self, definitions):
        self.definitions = definitions
        parts = []
        for name, part in definitions:
            parts.append("(?P<%s>%s)" % (name, part))
        self.regexpString = "|".join(parts)
        self.regexp = re.compile(self.regexpString, re.MULTILINE)

    def parse(self, text):
        for match in self.regexp.finditer(text):
            found = False
            for name, rexp in self.definitions:
                m = match.group(name)
                if m is not None:
                    yield (name, m)
                    break

class ParseNode(object):

    def __init__(self, val=None):
        self.val = val
        self.left = None
        self.right = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        tmpstr = ""
        if self.left is not None:
            tmpstr += "(" + str(self.left) + ")"
        tmpstr += str(self.val)
        if self.right is not None:
            tmpstr += "(" + str(self.right) + ")"
        return tmpstr

class ExpressionParser(object):

    def _merge(self, pos, alist):
        node = ParseNode()
        if pos == len(alist) - 1:
            return alist[-1] # last element
        else:
            node.val = alist[pos + 1]
            node.left = alist[pos]
            node.right = self._merge(pos + 2, alist)
        return node

    def T(self):
        alist = []
        alist.append(self.S())
        while self.check('multiply') or self.check('division'):
            alist.append({
                "type": self.nextToken[0],
                "value": self.nextToken[1]
            })
            self.advance()
            alist.append(self.S())
        return alist[0] if (len(alist) == 1) else self._merge(0, alist)

    def E(self):
        alist = []
        alist.append(self.T())
        while self.check('addition') or self.check('substract'):
            alist.append({
                "type": self.nextToken[0],
                "value": self.nextToken[1]
            })
            self.advance()
            alist.append(self.T())
        return alist[0] if len(alist) == 1 else self._merge(0, alist)

    def parse(self, text):
        lexer = Lexer(definitions)
        self.tokens = list(lexer.parse(text))
        self.idx = -1
        self.level = 0
        self.advance()
        return self.E()

    def enter(self, mystr):
        self.printToken(mystr)
        self.level += 1

    def leave(self, mystr):
        self.level -= 1
        self.printToken(mystr)

    def printToken(self, mystr):
        i = 0
        while(i < 4 * self.level):
            sys.stdout.write(" ")
            sys.stdout.flush()
            i += 1
        print(mystr)

    def advance(self):
        self.idx += 1
        if self.idx < len(self.tokens):
            self.nextToken = self.tokens[self.idx]
        else:
            self.nextToken = None

    def check(self, r_type):
        return (self.nextToken[0] == r_type) if self.nextToken else False

    def F(self):
        node = ParseNode()
        if self.check('number') or self.check('variable'):
            node.val = {
                "type": self.nextToken[0],
                "value": self.nextToken[1]
            }
            self.advance()
        elif self.check("paren_open"):
            self.advance()
            node = self.E()
            self.advance()
        return node

    def S(self):
        node = self.F()
        if self.check('power'):
            newNode = ParseNode()

            newNode.left = node
            newNode.val = {
                "type": self.nextToken[0],
                "value": self.nextToken[1]
            }
            self.advance()
            newNode.right = self.S()
            return newNode
        return node

def printPNode(pnode, level):
    if pnode is None: return
    i = 0
    while(i < 2 * level):
        sys.stdout.write(" ")
        sys.stdout.flush()
        i += 1
    print(pnode.val)
    printPNode(pnode.left, level + 1)
    printPNode(pnode.right, level + 1)


def evaluate(pnode, substitutes=None):
    if pnode is not None:
        if pnode.left is None and pnode.right is None:
            if pnode.val['type'] == 'variable':
                lookup = str(pnode.val['value'])
                return substitutes[lookup]
            return int(pnode.val['value'])
        if pnode.val['type'] == "addition":
            return evaluate(pnode.left, substitutes) + \
                evaluate(pnode.right, substitutes)
        elif pnode.val['type'] == "substract":
            return evaluate(pnode.left, substitutes) - \
                evaluate(pnode.right, substitutes)
        elif pnode.val['type'] == "multiply":
            return evaluate(pnode.left, substitutes) * \
                evaluate(pnode.right, substitutes)
        elif pnode.val['type'] == "division":
            return evaluate(pnode.left, substitutes) / \
                evaluate(pnode.right, substitutes)
        elif pnode.val['type'] == "power":
            return math.pow(evaluate(pnode.left, substitutes),
                evaluate(pnode.right, substitutes))
    return None

mytable = {
    'x': 4,
    'y': 5,
    'z': 2
}
myExp = "(x+y)-16/z^2"
parser = ExpressionParser()
pnode = parser.parse(myExp)
result = evaluate(pnode, substitutes=mytable)
print("%s = %s" % (myExp, str(result)) )
print
print("Parse Tree")
print
printPNode(pnode, 0)
