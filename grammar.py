from collections import defaultdict

class SyntaxRule:
    def __init__(self, lhs: str, rhs1: str, rhs2: str, p: float):
        self.lhs = lhs
        self.rhs1 = rhs1
        self.rhs2 = rhs2
        self.p = p

    def as_list(self) -> list:
        return [self.lhs, self.rhs1, self.rhs2, self.p]


class LexicalRule:
    def __init__(self, lhs: str, rhs: str, p: float):
        self.lhs = lhs
        self.rhs = rhs
        self.p = p

    def as_list(self) -> list:
        return [self.lhs, self.rhs, self.p]


class ParseTreeNode:
    def __init__(self, data: str, left: 'ParseTreeNode' = None, right: 'ParseTreeNode' = None):
        self.left = left
        self.right = right
        self.data = data

    def __repr__(self) -> str:
        return self.traverse()

    def traverse(self) -> str:
        if self.left == None and self.right == None:
            return self.data
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
        '''Implementation of CYK Parse to parse input sentences'''

        # TODO: contraction expansion
        # TODO: don't auto-lowercase commands
        # TODO: tokenization
        tokens = sentence.lower().split()
        l = len(tokens)

        trees = {}
        probabilities = defaultdict(int)

        for i, word in enumerate(tokens):
            for x, y, p in self.lexical_rules():
                if y == word:
                    probabilities[x, i, i] = p
                    trees[x, i, i] = ParseTreeNode(word)

        for i, j, k in self.subspans(l):
            for x, y, z, p in self.syntax_rules():
                p_yz = probabilities[y, i, j] * probabilities[z, j + 1, k] * p

                # if i == 0 and k == l - 1:
                #     print(x, y, z, p, trees)

                if p_yz > probabilities[x, i, k]:
                    probabilities[x, i, k] = p_yz
                    trees[x, i, k] = ParseTreeNode('', trees[y, i, j], trees[z, j + 1, k])

        # print(trees)
        # print()
        # print()

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


if __name__ == '__main__':
    syntax = [
        SyntaxRule('S', 'Imperative', 'NP', 1/7),
        SyntaxRule('S', 'NP', 'VP', 1/7),
        SyntaxRule('S', 'NP', 'Verb', 1/7),
        SyntaxRule('S', 'Noun', 'Verb', 1/7),
        SyntaxRule('S', 'Noun', 'VP', 1/7),
        SyntaxRule('S', 'Pronoun', 'VP', 1/7),
        SyntaxRule('S', 'Pronoun', 'Verb', 1/7),

        SyntaxRule('VP', 'VP', 'NP', 1/7),
        SyntaxRule('VP', 'Verb', 'NP', 1/7),
        SyntaxRule('VP', 'Verb', 'Noun', 1/7),
        SyntaxRule('VP', 'Verb', 'Pronoun', 1/7),
        SyntaxRule('VP', 'VP', 'Pronoun', 1/7),
        SyntaxRule('VP', 'VP', 'Adverb', 1/7),
        SyntaxRule('VP', 'VP', 'PP', 1/7),

        SyntaxRule('NP', 'Article', 'Noun', 0.5),
        SyntaxRule('NP', 'NP', 'PP', 0.5),

        SyntaxRule('PP', 'Preposition', 'NP', 1),

        SyntaxRule('Imperative', 'Verb', 'NP', 1),
    ]

    lexicon = [
        LexicalRule('Preposition', 'to', 0.333),
        LexicalRule('Preposition', 'inside', 0.333),
        LexicalRule('Preposition', 'in', 0.333),

        LexicalRule('Article', 'the', 1),

        LexicalRule('Noun', 'contents', 0.333),
        LexicalRule('Noun', 'everything', 0.333),
        LexicalRule('Noun', 'dir', 0.333), # placeholder for testing without semantics

        LexicalRule('Pronoun', 'me', 0.5),
        LexicalRule('Pronoun', 'what', 0.5),

        LexicalRule('Adverb', 'recursively', 1),

        LexicalRule('Verb', 'run', 1/15),
        LexicalRule('Verb', 'execute', 1/15),
        LexicalRule('Verb', 'do', 1/15),
        LexicalRule('Verb', 'show', 1/15),
        LexicalRule('Verb', 'list', 1/15),
        LexicalRule('Verb', 'tell', 1/15),
        LexicalRule('Verb', 'move', 1/15),
        LexicalRule('Verb', 'rename', 1/15),
        LexicalRule('Verb', 'place', 1/15),
        LexicalRule('Verb', 'copy', 1/15),
        LexicalRule('Verb', 'duplicate', 1/15),
        LexicalRule('Verb', 'delete', 1/15),
        LexicalRule('Verb', 'remove', 1/15),
        LexicalRule('Verb', 'is', 1/15),
        LexicalRule('Verb', 'put', 1/15),
    ]

    grammar = Grammar(syntax, lexicon)

    phrase = 'Show me the contents'
    tree = grammar.parse(phrase)

    if tree != None:
        print(tree.traverse())
    else:
        print('no parse tree found')
