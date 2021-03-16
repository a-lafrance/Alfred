# 4 kinds of tokens:
    # word
    # command input
    # conjunctor (comma)
    # end of sentence (period, optional & ignored)

class Token: # empty base class
    pass

class WordToken(Token):
    def __init__(self, word: str):
        self.word = word

    def __repr__(self) -> str:
        return f'"{self.word}"'

    def __eq__(self, tok: 'any') -> bool:
        if type(tok) == WordToken:
            return self.word == tok.word
        elif type(tok) == str:
            return self.word == tok
        elif isinstance(tok, Token):
            return False
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.word)

class CommandInputToken(Token):
    def __init__(self, content: str):
        self.content = content

    def __repr__(self) -> str:
        return f'`{self.content}`'

    def __eq__(self, tok: 'any') -> bool:
        if type(tok) == CommandInputToken:
            # "catch-all" cmd input when content is None
            return self.content == tok.content if self.content != None else True
        elif isinstance(tok, Token):
            return False
        else:
            return NotImplemented

    def __hash__(self):
        return hash('cmd')

    def placeholder() -> 'CommandInputToken':
        return CommandInputToken(None)

class ConjunctorToken(Token):
    def __repr__(self) -> str:
        return f','

    def __eq__(self, tok: 'any') -> bool:
        if type(tok) == WordToken:
            return tok.word == 'and'
        elif isinstance(tok, Token):
            return type(tok) == ConjunctorToken
        else:
            return NotImplemented

    def __hash__(self):
        return hash(',')

def tokenize(sentence: str) -> 'list of tokens':
    tokens = []
    i = 0
    chars = len(sentence)

    while i < chars:
        c = sentence[i]

        if c == '`':
            # command input
            cmd_input = ''
            i += 1
            c = sentence[i]

            while i < chars and c != '`':
                cmd_input += c
                i += 1

                if i < chars:
                    c = sentence[i]
                else:
                    break

            token = CommandInputToken(cmd_input)
            tokens.append(token)

            i += 1
        elif c == ',':
            # conjunctor
            tokens.append(ConjunctorToken())
            i += 1
        elif c in {'.', ' ', '?'}:
            # basically ignore appropriate end-of-sentence indicators and spaces
            i += 1
        else:
            # word
            word = ''

            while c != ' ':
                word += c
                i += 1

                if i < chars:
                    c = sentence[i]
                else:
                    break

            token = WordToken(word)
            tokens.append(token)

    return tokens
