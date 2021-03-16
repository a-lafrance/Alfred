from collections import defaultdict
from tok import Token, tokenize

class SyntaxRule:
    def __init__(self, lhs: str, rhs1: str, rhs2: str, p: float):
        self.lhs = lhs
        self.rhs1 = rhs1
        self.rhs2 = rhs2
        self.p = p

    def as_list(self) -> list:
        return [self.lhs, self.rhs1, self.rhs2, self.p]


class LexicalRule:
    def __init__(self, lhs: str, rhs: Token, p: float):
        self.lhs = lhs
        self.rhs = rhs
        self.p = p

    def as_list(self) -> list:
        return [self.lhs, self.rhs, self.p]


class ParseTreeNode:
    def __init__(self, data: Token, cat: str, left: 'ParseTreeNode' = None, right: 'ParseTreeNode' = None):
        self.left = left
        self.right = right
        self.data = data
        self.cat = cat

    def __repr__(self) -> str:
        return self.traverse()

    def traverse(self) -> str:
        if self.left == None and self.right == None:
            return repr(self.data)
        else:
            return f'{self.left.traverse()} {self.right.traverse()}'


class Grammar:
    def __init__(self, syntax: [SyntaxRule], lexicon: [LexicalRule]):
        self.syntax = syntax
        self.lexicon = lexicon

    def as_dict(self) -> dict:
        return {
            'syntax' : [rule.as_list() for rule in self.syntax],
            'lexicon' : [rule.as_list() for rule in self.lexicon]
        }

    def lexical_rules(self) -> 'yields lists':
        for rule in self.lexicon:
            yield rule.as_list()

    def syntax_rules(self) -> 'yields lists':
        for rule in self.syntax:
            yield rule.as_list()

    def parse(self, sentence: str) -> ParseTreeNode:
        '''Implementation of CYK Parse to parse (tokenized) input sentences'''

        tokens = tokenize(sentence.lower())
        l = len(tokens)

        trees = {}
        probabilities = defaultdict(int)

        for i, tok in enumerate(tokens):
            for x, y, p in self.lexical_rules():
                if y == tok:
                    probabilities[x, i, i] = p
                    trees[x, i, i] = ParseTreeNode(tok, x)

        for i, j, k in self.subspans(l):
            for x, y, z, p in self.syntax_rules():
                p_yz = probabilities[y, i, j] * probabilities[z, j + 1, k] * p

                if p_yz > probabilities[x, i, k]:
                    probabilities[x, i, k] = p_yz
                    trees[x, i, k] = ParseTreeNode(None, x, trees[y, i, j], trees[z, j + 1, k])

        for data, tree in trees.items():
            x, i, j = data

            if i == 0 and j == l - 1 and x == 'S':
                return tree

        return None

    def subspans(self, n: int) -> (int, int, int):
        for l in range(2, n + 1):
            for i in range(n + 1 - l):
                k = i + l - 1

                for j in range(i, k):
                    yield (i, j, k)
