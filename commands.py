from grammar import ParseTreeNode
from tok import CommandInputToken

from queue import Queue


class Command:
    # empty base class
    def exec(self):
        return NotImplemented

class ListCommand(Command):
    def __init__(self, tree: ParseTreeNode):
        self.dir = None # default before reading parse
        self._read_parse_tree(tree, {})

    def __str__(self) -> str:
        return f'`ls {self.dir.content}`' if self.dir != None else 'invalid command'

    def exec(self):
        pass

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}) -> bool:
        # if root is syntactic, parse children recursively with remaining lexicon
        if node.data == None:
            if node.cat == 'S':
                if node.left != None:
                    if node.left.cat == 'VP' or node.left.cat == 'Verb':
                        if node.left.cat == 'VP':
                            lexicon = {
                                'Verb' : {'show', 'tell'},
                                'Pronoun' : {'me'},
                            }
                        else:
                            lexicon = {
                                'Verb' : {'list', 'display', 'find'}
                            }

                        if not self._read_parse_tree(node.left, lexicon):
                            return False # if parse fails, return failure

                        if node.right != None:
                            if node.right.cat == 'NP':
                                lexicon = {
                                    'Noun' : {'contents', 'everything', CommandInputToken.placeholder()},
                                    'Article' : {'the'},
                                    'Preposition' : {'of', 'in', 'inside'},
                                }

                                return self._read_parse_tree(node.right, lexicon) # result of right parse is the ultimate result
                    elif node.left.cat == 'Pronoun':
                        lexicon = {
                            'Pronoun' : {'what'}
                        }

                        if not self._read_parse_tree(node.left, lexicon):
                            return False # if parse fails, return failure

                        if node.right != None:
                            if node.right.cat == 'VP':
                                lexicon = {
                                    'Verb' : {'is'},
                                    'Preposition' : {'in', 'inside'},
                                    'Noun' : {CommandInputToken.placeholder()},
                                }

                                return self._read_parse_tree(node.right, lexicon) # result of right parse is the ultimate result
            elif node.cat == 'VP':
                # assume lexicon was appropriately configured previously
                if node.left != None and node.right != None:
                    return self._read_parse_tree(node.left, lexicon) and self._read_parse_tree(node.right, lexicon)
            elif node.cat == 'NP':
                if node.left != None and node.right != None:
                    if node.left.cat == 'NP' and node.right.cat == 'PP':
                        if not self._read_parse_tree(node.left, lexicon):
                            return False

                        lexicon['Noun'] = {CommandInputToken.placeholder()}

                        return self._read_parse_tree(node.right, lexicon)
                    elif node.left.cat == 'Article' and node.right.cat == 'Noun':
                        return self._read_parse_tree(node.left, lexicon) and self._read_parse_tree(node.right, lexicon)
            elif node.cat == 'PP':
                if node.left != None and node.right != None:
                    return self._read_parse_tree(node.left, lexicon) and self._read_parse_tree(node.right, lexicon)

            return False # indicate failure if success isn't found above
        # if root is lexical, make sure word matches remaining lexicon
        else:
            if node.cat == 'Noun':
                if type(node.data) == CommandInputToken:
                    self.dir = node.data
                elif node.data == 'contents':
                    lexicon['Noun'] = {'contents'}
                    lexicon['Preposition'] = {'of'}
                elif node.data == 'everything':
                    lexicon['Noun'] = {'everything'}
                    lexicon['Preposition'] = {'in', 'inside'}
                    lexicon['Article'] = set()

            return node.data in lexicon[node.cat]


class MoveCommand(Command):
    def __init__(self, tree: ParseTreeNode):
        # defaults before reading parse
        self.src_path = None
        self.dest_path = None
        self.is_glob = False

        self._read_parse_tree(tree, {})

    def __str__(self) -> str:
        return f'`mv {self.src_path.content} {self.dest_path.content}`' if self.src_path != None and self.dest_path != None else 'invalid command'

    def exec(self):
        pass

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}) -> bool:
        # print(node.cat, node.data)
        if node.data == None:
            if node.cat == 'S':
                if node.left != None and node.right != None:
                    # print(node.left.cat, node.right.cat)
                    if node.left.cat == 'Verb' and node.right.cat == 'NP':
                        # this is the only possible syntax -- lexicon varies
                        full_lexicon = {
                            'Verb' : {'move', 'rename', 'put', 'place'},
                            'Noun' : {'everything', CommandInputToken.placeholder()},
                            'Preposition' : {'to', 'in', 'inside', 'from'},
                        }

                        return self._read_parse_tree(node.left, full_lexicon) and self._read_parse_tree(node.right, full_lexicon)
            elif node.cat == 'NP':
                if node.left != None and node.right != None:
                    return node.left.cat == 'Noun' and self._read_parse_tree(node.left, lexicon) and self._read_parse_tree(node.right, lexicon)
            elif node.cat == 'PP':
                if node.left != None and node.right != None:
                    if node.left.cat == 'Preposition' and node.right.cat in {'Noun', 'NP'}:
                        return self._read_parse_tree(node.left, lexicon) and self._read_parse_tree(node.right, lexicon)

            return False
        else:
            if node.cat == 'Noun':
                if type(node.data) == CommandInputToken:
                    if self.src_path == None:
                        self.src_path = node.data
                    else:
                        self.dest_path = node.data
                elif node.data == 'everything':
                    self.is_glob = True
            elif node.cat == 'Verb':
                if node.data == 'rename':
                    lexicon['Preposition'] = {'to'}
                elif node.data in {'put', 'place'}:
                    lexicon['Preposition'] = {'in', 'inside'}

                if node.data != 'move' and 'everything' in lexicon['Noun']:
                    lexicon['Noun'].remove('everything')

            return node.data in lexicon[node.cat]

class CopyCommand(Command):
    def __init__(self, tree: ParseTreeNode):
        # defaults before reading parse
        self.src_path = None
        self.dest_path = None
        self.is_glob = False

        self._read_parse_tree(tree, {})

    def __str__(self) -> str:
        return f'`cp {self.src_path.content} {self.dest_path.content}`' if self.src_path != None and self.dest_path != None else 'invalid command'

    def exec(self):
        pass

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}) -> bool:
        # print(node.cat, node.data)
        if node.data == None:
            if node.cat == 'S':
                if node.left != None and node.right != None:
                    # print(node.left.cat, node.right.cat)
                    if node.left.cat == 'Verb' and node.right.cat == 'NP':
                        # this is the only possible syntax -- lexicon varies
                        full_lexicon = {
                            'Verb' : {'copy', 'duplicate'},
                            'Noun' : {'everything', CommandInputToken.placeholder()},
                            'Preposition' : {'to', 'in', 'inside', 'from'},
                        }

                        return self._read_parse_tree(node.left, full_lexicon) and self._read_parse_tree(node.right, full_lexicon)
            elif node.cat == 'NP':
                if node.left != None and node.right != None:
                    return node.left.cat == 'Noun' and self._read_parse_tree(node.left, lexicon) and self._read_parse_tree(node.right, lexicon)
            elif node.cat == 'PP':
                if node.left != None and node.right != None:
                    if node.left.cat == 'Preposition' and node.right.cat in {'Noun', 'NP'}:
                        return self._read_parse_tree(node.left, lexicon) and self._read_parse_tree(node.right, lexicon)

            return False
        else:
            if node.cat == 'Noun':
                if type(node.data) == CommandInputToken:
                    if self.src_path == None:
                        self.src_path = node.data
                    else:
                        self.dest_path = node.data
                elif node.data == 'everything':
                    self.is_glob = True

            return node.data in lexicon[node.cat]

class RemoveCommand(Command):
    pass

class CommandGroup(Command):
    pass


if __name__ == '__main__':
    from main import grammar

    sentence = 'copy `src` to `dest`'
    tree = grammar.parse(sentence)
    cmd = CopyCommand(tree)
    print(sentence, '->', cmd)

    # while True:
    #     phrase = input('> ')
    #     root = grammar.parse(phrase)
    #
    #     if phrase == '\q':
    #         break
    #
    #     if tree != None:
    #         cmd = MoveCommand(root)
    #         print(cmd)
    #     else:
    #         print('no parse tree found')
    #
    # print('done')
