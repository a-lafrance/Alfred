# 4 kinds of tokens:
    # word
    # command input
    # conjunctor (comma)
    # end of sentence (period, optional)

class WordToken:
    def __init__(self, word: str):
        self.word = word

    def __repr__(self) -> str:
        return f'"{self.word}"'

class CommandInputToken:
    def __init__(self, content: str):
        self.content = content

    def __repr__(self) -> str:
        return f'`{self.content}`'

class ConjunctorToken:
    def __repr__(self) -> str:
        return f','

class EndOfSentenceToken:
    def __repr__(self) -> str:
        return f'.'

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
        elif c == '.':
            # end of sentence
            tokens.append(EndOfSentenceToken())
            i += 1
        elif c != ' ':
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
        else:
            i += 1

    return tokens

if __name__ == '__main__':
    while True:
        sentence = input('> ')

        if sentence == '\q':
            break

        tokens = tokenize(sentence)
        print(tokens)

    print('done')
