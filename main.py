from grammar import SyntaxRule, LexicalRule, Grammar

if __name__ == '__main__':
    syntax = [
        SyntaxRule('S', 'Imperative', 'NP', 0.25),
        SyntaxRule('S', 'NP', 'VP', 0.25),
        SyntaxRule('S', 'Noun', 'VP', 0.25),
        SyntaxRule('S', 'Pronoun', 'VP', 0.25),

        SyntaxRule('VP', 'VP', 'NP', 1/7),
        SyntaxRule('VP', 'Verb', 'NP', 1/7),
        SyntaxRule('VP', 'Verb', 'Noun', 1/7),
        SyntaxRule('VP', 'Verb', 'Pronoun', 1/7),
        SyntaxRule('VP', 'VP', 'Pronoun', 1/7),
        SyntaxRule('VP', 'VP', 'Adverb', 1/7),
        SyntaxRule('VP', 'VP', 'PP', 1/7),

        SyntaxRule('NP', 'Article', 'Noun', 0.5),
        SyntaxRule('NP', 'NP', 'PP', 0.5),

        SyntaxRule('PP', 'Preposition', 'NP', 0.333),
        SyntaxRule('PP', 'Preposition', 'Noun', 0.333),
        SyntaxRule('PP', 'Preposition', 'Pronoun', 0.333),

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

        LexicalRule('Pronoun', 'me', 0.333),
        LexicalRule('Pronoun', 'what', 0.333),
        LexicalRule('Pronoun', 'i', 0.333),

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

    while True:
        sentence = input('> ')

        if sentence == '\q':
            break

        tree = grammar.parse(sentence)

        if tree != None:
            print(tree.traverse())
        else:
            print('no parse tree found')

    print('done')
