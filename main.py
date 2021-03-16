from grammar import SyntaxRule, LexicalRule, Grammar
from tok import WordToken, CommandInputToken, ConjunctorToken
from commands import Command, Context

import random


class Alfred:
    def __init__(self):
        self.context = Context()

        self.grammar = Grammar([
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
        ], [
            LexicalRule('Preposition', 'to', 0.2),
            LexicalRule('Preposition', 'inside', 0.2),
            LexicalRule('Preposition', 'in', 0.2),
            LexicalRule('Preposition', 'from', 0.2),
            LexicalRule('Preposition', 'of', 0.2),

            LexicalRule('Article', 'the', 1),

            LexicalRule('Noun', 'contents', 0.25),
            LexicalRule('Noun', 'everything', 0.25),
            LexicalRule('Noun', CommandInputToken.placeholder(), 0.25),
            LexicalRule('Noun', 'there', 0.25),

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
        ])


    def bad_grammar_error(self) -> str:
        responses = [
            "I'm not sure what you said",
            "I couldn't understand what you said",
            "I didn't get that"
        ]

        return 'Sorry, ' + random.choice(responses)


    def invalid_command_error(self) -> str:
        responses = [
            "I'm not sure what to do",
            "I don't know how to do that",
            "that's not a valid command"
        ]

        noun = random.choice(['what you said', 'that'])

        return f'I understood {noun}, but ' + random.choice(responses)


    def serve(self):
        while True:
            sentence = input('How can I help you?  ')

            if sentence.lower() in {'\q', 'quit', 'bye', 'goodbye', 'i want out'}:
                print('Bye!')
                return

            tree = self.grammar.parse(sentence)

            if tree != None:
                cmd = Command.from_parse_tree(tree, self.context)
                print()

                if cmd != None:
                    print(cmd.exec())
                else:
                    print(self.invalid_command_error())
            else:
                print(self.bad_grammar_error())

            print()


if __name__ == '__main__':
    alfred = Alfred()
    alfred.serve()
