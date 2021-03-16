from grammar import ParseTreeNode
from tok import CommandInputToken, ConjunctorToken

from queue import Queue
from collections import defaultdict

import subprocess


class Command:
    # (mostly) empty base class
    def exec(self):
        return subprocess.run(str(self), shell=True, capture_output=True, text=True)

    def is_valid(self) -> bool:
        return NotImplemented

    def from_parse_tree(tree: ParseTreeNode, include_group=True) -> 'Command':
        cmd_types = [ListCommand, MoveCommand, CopyCommand, RemoveCommand, RawCommand, CommandGroup]

        if include_group:
            cmd_types.append(CommandGroup)

        for cmd_type in cmd_types:
            cmd = cmd_type(tree)

            if cmd.is_valid():
                return cmd

        return None

class ListCommand(Command):
    def __init__(self, tree: ParseTreeNode):
        self.dir = None # default before reading parse
        self._read_parse_tree(tree, defaultdict(set))

    def __str__(self) -> str:
        return f'ls {self.dir.content}' if self.is_valid() else 'invalid command'

    def is_valid(self) -> bool:
        return self.dir != None

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}) -> bool:
        # if root is syntactic, parse children recursively with remaining lexicon
        if node.data == None:
            if node.cat == 'S':
                if node.left != None:
                    if node.left.cat == 'VP' or node.left.cat == 'Verb':
                        if node.left.cat == 'VP':
                            lexicon = defaultdict(set, {
                                'Verb' : {'show', 'tell'},
                                'Pronoun' : {'me'},
                            })
                        else:
                            lexicon = defaultdict(set, {
                                'Verb' : {'list', 'display', 'find'}
                            })

                        if not self._read_parse_tree(node.left, lexicon):
                            return False # if parse fails, return failure

                        if node.right != None:
                            if node.right.cat == 'NP':
                                lexicon = defaultdict(set, {
                                    'Noun' : {'contents', 'everything', CommandInputToken.placeholder()},
                                    'Article' : {'the'},
                                    'Preposition' : {'of', 'in', 'inside'},
                                })

                                return self._read_parse_tree(node.right, lexicon) # result of right parse is the ultimate result
                    elif node.left.cat == 'Pronoun':
                        lexicon = defaultdict(set, {
                            'Pronoun' : {'what'}
                        })

                        if not self._read_parse_tree(node.left, lexicon):
                            return False # if parse fails, return failure

                        if node.right != None:
                            if node.right.cat == 'VP':
                                lexicon = defaultdict(set, {
                                    'Verb' : {'is'},
                                    'Preposition' : {'in', 'inside'},
                                    'Noun' : {CommandInputToken.placeholder()},
                                })

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

        self._read_parse_tree(tree, defaultdict(set))

    def __str__(self) -> str:
        return f'mv {self.src_path.content} {self.dest_path.content}' if self.is_valid() else 'invalid command'

    def is_valid(self) -> bool:
        return self.src_path != None and self.dest_path != None

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}) -> bool:
        # print(node.cat, node.data)
        if node.data == None:
            if node.cat == 'S':
                if node.left != None and node.right != None:
                    # print(node.left.cat, node.right.cat)
                    if node.left.cat == 'Verb' and node.right.cat == 'NP':
                        # this is the only possible syntax -- lexicon varies
                        full_lexicon = defaultdict(set, {
                            'Verb' : {'move', 'rename', 'put', 'place'},
                            'Noun' : {'everything', CommandInputToken.placeholder()},
                            'Preposition' : {'to', 'in', 'inside', 'from'},
                        })

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

        self._read_parse_tree(tree, defaultdict(set))

    def __str__(self) -> str:
        return f'cp {self.src_path.content} {self.dest_path.content}' if self.is_valid() else 'invalid command'

    def is_valid(self) -> bool:
        return self.src_path != None and self.dest_path != None

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}) -> bool:
        if node.data == None:
            if node.cat == 'S':
                if node.left != None and node.right != None:
                    # print(node.left.cat, node.right.cat)
                    if node.left.cat == 'Verb' and node.right.cat == 'NP':
                        # this is the only possible syntax -- lexicon varies
                        full_lexicon = defaultdict(set, {
                            'Verb' : {'copy', 'duplicate'},
                            'Noun' : {'everything', CommandInputToken.placeholder()},
                            'Preposition' : {'to', 'in', 'inside', 'from'},
                        })

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
    def __init__(self, tree: ParseTreeNode):
        # defaults before reading parse
        self.path = None
        self.is_recursive = False

        self._read_parse_tree(tree, defaultdict(set))

    def __str__(self) -> str:
        recursive = '-rf ' if self.is_recursive else ''

        return f'rm {recursive}{self.path.content}' if self.is_valid() else 'invalid command'

    def is_valid(self) -> bool:
        return self.path != None

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}) -> bool:
        if node.data == None:
            if node.cat == 'S':
                if node.left != None and node.right != None:
                    lexicon = defaultdict(set, {
                        'Verb' : {'delete', 'remove'} # purge, trash, scrap,
                    })

                    if node.left.cat == 'VP':
                        lexicon['Adverb'] = {'recursively'}
                    elif node.left.cat != 'Verb':
                        return False

                    if not self._read_parse_tree(node.left, lexicon):
                        return False

                    lexicon = defaultdict(set, {
                        'Noun' : {CommandInputToken.placeholder()}
                    })

                    if node.right.cat == 'NP':
                        lexicon['Noun'].add('everything')
                        lexicon['Preposition'] = {'in', 'inside'}
                    elif node.right.cat != 'Noun':
                        return False

                    return self._read_parse_tree(node.right, lexicon)
            elif node.cat == 'NP':
                if node.left != None and node.right != None:
                    if node.left.cat == 'Noun' and node.right.cat == 'PP':
                        lexicon['Noun'] = {'everything'}

                        if not self._read_parse_tree(node.left, lexicon):
                            return False

                        lexicon['Noun'] = {CommandInputToken.placeholder()}

                        return self._read_parse_tree(node.right, lexicon)
            elif node.cat == 'PP':
                if node.left != None and node.right != None:
                    if node.left.cat == 'Preposition' and node.right.cat == 'Noun':
                        return self._read_parse_tree(node.left, lexicon) and self._read_parse_tree(node.right, lexicon)
            elif node.cat == 'VP':
                if node.left != None and node.right != None:
                    if node.left.cat == 'Adverb' and node.right.cat == 'Verb':
                        return self._read_parse_tree(node.left, lexicon) and self._read_parse_tree(node.right, lexicon)

            return False
        else:
            if node.cat == 'Noun':
                if type(node.data) == CommandInputToken:
                    self.path = node.data
                elif node.data == 'everything':
                    self.is_recursive = True
            elif node.cat == 'Adverb' and node.data == 'recursively':
                self.is_recursive = True

            return node.data in lexicon[node.cat]


class RawCommand(Command):
    def __init__(self, tree: ParseTreeNode):
        self.cmd = None
        self._read_parse_tree(tree, defaultdict(set))

    def __str__(self) -> str:
        return self.cmd.content if self.is_valid() else 'invalid command'

    def is_valid(self) -> bool:
        return self.cmd != None

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}) -> bool:
        if node.data == None:
            if node.left != None and node.right != None:
                if node.cat == 'S':
                    if node.left.cat == 'Verb' and node.right.cat == 'Noun':
                        lexicon = defaultdict(set, {
                            'Verb' : {'run', 'do', 'execute'},
                            'Noun' : {CommandInputToken.placeholder()},
                        })

                        return self._read_parse_tree(node.left, lexicon) and self._read_parse_tree(node.right, lexicon)

            return False
        else:
            if node.cat == 'Noun':
                if type(node.data) == CommandInputToken:
                    self.cmd = node.data

            return node.data in lexicon[node.cat]


class CommandGroup(Command):
    def __init__(self, tree: ParseTreeNode):
        self.cmds = []
        self._read_parse_tree(tree, defaultdict(set))

    def __str__(self) -> str:
        return ' && '.join([str(cmd) for cmd in self.cmds])

    def is_valid(self) -> bool:
        return len(self.cmds) > 0

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}) -> bool:
        # print(node.cat, node.traverse())
        if node.data == None:
            if node.left != None and node.right != None:
                if node.cat == 'S':
                    if node.left.cat == 'S' and node.right.cat == 'ConjClause':
                        lexicon = defaultdict(set, {
                            'Conj' : {'and', ConjunctorToken(), 'then'}
                        })

                        return self._read_parse_tree(node.left, lexicon) and self._read_parse_tree(node.right, lexicon)
                    else:
                        cmd = Command.from_parse_tree(node, include_group=False)

                        if cmd != None:
                            self.cmds.append(cmd)
                            return True
                        else:
                            self.cmds = []
                            return False
                elif node.cat == 'ConjClause':
                    return self._read_parse_tree(node.left, lexicon) and self._read_parse_tree(node.right, lexicon)

            return False
        else:
            return node.data in lexicon[node.cat]

if __name__ == '__main__':
    from main import grammar

    sentence = 'execute `python main.py` then list the contents of `dir` and move `dir/file1` to `dir2/file1`'
    tree = grammar.parse(sentence)
    cmd = Command.from_parse_tree(tree)
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
