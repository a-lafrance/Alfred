from grammar import SyntaxRule, LexicalRule, Grammar
from tok import WordToken, CommandInputToken, ConjunctorToken

if __name__ == '__main__':
    syntax = [
        SyntaxRule('S', 'VP', 'NP', 1/6),
        SyntaxRule('S', 'Verb', 'NP', 1/6),
        SyntaxRule('S', 'Verb', 'Noun', 1/6),
        SyntaxRule('S', 'NP', 'VP', 1/6),
        SyntaxRule('S', 'Noun', 'VP', 1/6),
        SyntaxRule('S', 'Pronoun', 'VP', 1/6),

        SyntaxRule('VP', 'Verb', 'Pronoun', 0.2),
        SyntaxRule('VP', 'Verb', 'PP', 0.2),
        SyntaxRule('VP', 'VP', 'PP', 0.2),
        SyntaxRule('VP', 'Adverb', 'Verb', 0.2),
        SyntaxRule('VP', 'Adverb', 'VP', 0.2),

        SyntaxRule('NP', 'NP', 'PP', 1/3),
        SyntaxRule('NP', 'Noun', 'PP', 1/3),
        SyntaxRule('NP', 'Article', 'Noun', 1/3),

        SyntaxRule('PP', 'Preposition', 'NP', 1/3),
        SyntaxRule('PP', 'Preposition', 'Noun', 1/3),
        SyntaxRule('PP', 'Preposition', 'Pronoun', 1/3),
    ]

    lexicon = [
        LexicalRule('Preposition', WordToken('to'), 0.2),
        LexicalRule('Preposition', WordToken('inside'), 0.2),
        LexicalRule('Preposition', WordToken('in'), 0.2),
        LexicalRule('Preposition', WordToken('from'), 0.2),
        LexicalRule('Preposition', WordToken('of'), 0.2),

        LexicalRule('Article', WordToken('the'), 1),

        LexicalRule('Noun', WordToken('contents'), 1/3),
        LexicalRule('Noun', WordToken('everything'), 1/3),
        LexicalRule('Noun', CommandInputToken.placeholder(), 1/3),

        LexicalRule('Pronoun', WordToken('me'), 0.5),
        LexicalRule('Pronoun', WordToken('what'), 0.5),

        LexicalRule('Adverb', WordToken('recursively'), 1),

        LexicalRule('Verb', WordToken('run'), 1/17),
        LexicalRule('Verb', WordToken('execute'), 1/17),
        LexicalRule('Verb', WordToken('do'), 1/17),
        LexicalRule('Verb', WordToken('show'), 1/17),
        LexicalRule('Verb', WordToken('list'), 1/17),
        LexicalRule('Verb', WordToken('tell'), 1/17),
        LexicalRule('Verb', WordToken('move'), 1/17),
        LexicalRule('Verb', WordToken('rename'), 1/17),
        LexicalRule('Verb', WordToken('place'), 1/17),
        LexicalRule('Verb', WordToken('copy'), 1/17),
        LexicalRule('Verb', WordToken('duplicate'), 1/17),
        LexicalRule('Verb', WordToken('delete'), 1/17),
        LexicalRule('Verb', WordToken('remove'), 1/17),
        LexicalRule('Verb', WordToken('is'), 1/17),
        LexicalRule('Verb', WordToken('put'), 1/17),
        LexicalRule('Verb', WordToken('display'), 1/17),
        LexicalRule('Verb', WordToken('find'), 1/17),
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








# GRAMMAR DESIGN:

# --- Syntax ---
# S -> VP NP
#    | Verb NP
#    | Verb Noun
#    | NP VP
#    | Noun VP
#    | Pronoun VP
#
# VP -> Verb Pronoun
#     | Verb PP
#     | VP PP
#     | Adverb Verb
#     | Adverb VP
#
# NP -> NP PP
#     | Article Noun
#
# PP -> Preposition NP
#     | Preposition Noun
#     | Preposition Pronoun


# --- Lexicon ---
# Noun -> contents | everything | path
# Verb -> run | do | execute
#       | show | list | tell | display | find
#       | put | place | move | rename
#       | copy | duplicate
#       | delete | remove
# Pronoun -> me | what
# Adverb -> recursively
# Article -> the
# Preposition -> inside | in | to | from
