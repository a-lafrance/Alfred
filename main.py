from grammar import SyntaxRule, LexicalRule, Grammar
from tok import WordToken, CommandInputToken, ConjunctorToken
from commands import Command

syntax = [
    SyntaxRule('S', 'VP', 'NP', 0.125),
    SyntaxRule('S', 'VP', 'Noun', 0.125),
    SyntaxRule('S', 'Verb', 'NP', 0.125),
    SyntaxRule('S', 'Verb', 'Noun', 0.125),
    SyntaxRule('S', 'NP', 'VP', 0.125),
    SyntaxRule('S', 'Noun', 'VP', 0.125),
    SyntaxRule('S', 'Pronoun', 'VP', 0.125),
    SyntaxRule('S', 'S', 'ConjClause', 0.125),

    SyntaxRule('ConjClause', 'Conj', 'S', 1),

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
    LexicalRule('Preposition', 'to', 0.2),
    LexicalRule('Preposition', 'inside', 0.2),
    LexicalRule('Preposition', 'in', 0.2),
    LexicalRule('Preposition', 'from', 0.2),
    LexicalRule('Preposition', 'of', 0.2),

    LexicalRule('Article', 'the', 1),

    LexicalRule('Noun', 'contents', 1/3),
    LexicalRule('Noun', 'everything', 1/3),
    LexicalRule('Noun', CommandInputToken.placeholder(), 1/3),

    LexicalRule('Pronoun', 'me', 0.5),
    LexicalRule('Pronoun', 'what', 0.5),

    LexicalRule('Adverb', 'recursively', 1),

    LexicalRule('Verb', 'run', 1/17),
    LexicalRule('Verb', 'execute', 1/17),
    LexicalRule('Verb', 'do', 1/17),
    LexicalRule('Verb', 'show', 1/17),
    LexicalRule('Verb', 'list', 1/17),
    LexicalRule('Verb', 'tell', 1/17),
    LexicalRule('Verb', 'move', 1/17),
    LexicalRule('Verb', 'rename', 1/17),
    LexicalRule('Verb', 'place', 1/17),
    LexicalRule('Verb', 'copy', 1/17),
    LexicalRule('Verb', 'duplicate', 1/17),
    LexicalRule('Verb', 'delete', 1/17),
    LexicalRule('Verb', 'remove', 1/17),
    LexicalRule('Verb', 'is', 1/17),
    LexicalRule('Verb', 'put', 1/17),
    LexicalRule('Verb', 'display', 1/17),
    LexicalRule('Verb', 'find', 1/17),

    LexicalRule('Conj', 'and', 1/3),
    LexicalRule('Conj', 'then', 1/3),
    LexicalRule('Conj', ConjunctorToken(), 1/3),
]

grammar = Grammar(syntax, lexicon)
if __name__ == '__main__':
    # TODO: put grammar back here

    while True:
        sentence = input('> ')

        if sentence == '\q':
            break

        tree = grammar.parse(sentence)

        if tree != None:
            cmd = Command.from_parse_tree(tree)
            print(cmd.exec().stdout)
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
