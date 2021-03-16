from grammar import ParseTreeNode, Grammar, SyntaxRule, LexicalRule
from tok import CommandInputToken, ConjunctorToken

from queue import Queue
from collections import defaultdict

import subprocess
import random


class Context: # helper class representing a "context", or what Alfred remembers
    def __init__(self):
        self.last_path = None
        # self.last_cmd = None


class Command:
    # base class for all commands
    def exec(self) -> subprocess.CompletedProcess:
        return subprocess.run(str(self), shell=True, capture_output=True, text=True)

    def is_valid(self) -> bool:
        return NotImplemented

    def general_error_message(self) -> str:
        responses = [
            "Something [Verb], but I'm not sure what happened",
            'Unfortunately that command failed for an unknown reason',
            "I couldn't quite figure out why that [Verb]"
        ]

        verb = random.choice(['failed', 'went wrong', 'crashed', "didn't work"])

        return random.choice(responses).replace('[Verb]', verb)

    def from_parse_tree(tree: ParseTreeNode, context: Context, include_group=True) -> 'Command':
        cmd_types = [ListCommand, MoveCommand, CopyCommand, RemoveCommand, RawCommand]

        if include_group:
            cmd_types.append(CommandGroup)

        for cmd_type in cmd_types:
            cmd = cmd_type(tree, context)

            if cmd.is_valid():
                return cmd

        return None

class ListCommand(Command):
    def __init__(self, tree: ParseTreeNode, context: Context):
        self.dir = None # default before reading parse
        self._read_parse_tree(tree, defaultdict(set), context)

        if self.is_valid():
            context.last_path = self.dir

    def __str__(self) -> str:
        return f'ls {self.dir.content}' if self.is_valid() else 'invalid command'

    def is_valid(self) -> bool:
        return self.dir != None

    def exec(self) -> str:
        result = Command.exec(self)

        # first, check for error
        if result.returncode != 0: # assumed to be error
            stderr = result.stderr

            if 'No such file or directory' in stderr: # yes, this could technically be broken, but it'll do for now
                responses = [
                    "I couldn't [Verb] `dir`",
                    "`dir` doesn't seem to exist"
                ]

                words = ['find', 'locate', 'see']

                response = random.choice(responses)
                word = random.choice(words)

                response = response.replace('[Verb]', word).replace('dir', self.dir.content)
            else:
                # generic error
                response = self.general_error_message()
        else:
            stdout = result.stdout

            if stdout == '': # assume directory is empty
                responses = [
                    "`dir` seems to be empty",
                    "`dir` doesn't have anything inside it",
                    "There's nothing inside `dir`"
                ]

                response = random.choice(responses).replace('dir', self.dir.content) + '\n' + stdout
            else:
                responses = [
                    "`dir` contains:",
                    "Inside `dir` is:",
                    "I [Verb] the following in/inside `dir`:",
                    "Here's what I found/saw/got:"
                ]

                verbs = ['found', 'saw']

                response = random.choice(responses)
                verb = random.choice(verbs)

                response = response.replace('[Verb]', verb).replace('dir', self.dir.content) + '\n' + stdout

        return response

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}, context: Context) -> bool:
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

                        if not self._read_parse_tree(node.left, lexicon, context):
                            return False # if parse fails, return failure

                        if node.right != None:
                            if node.right.cat == 'NP':
                                lexicon = defaultdict(set, {
                                    'Noun' : {'contents', 'everything', 'there', CommandInputToken.placeholder()},
                                    'Article' : {'the'},
                                    'Preposition' : {'of', 'in', 'inside'},
                                })

                                return self._read_parse_tree(node.right, lexicon, context) # result of right parse is the ultimate result
                    elif node.left.cat == 'Pronoun':
                        lexicon = defaultdict(set, {
                            'Pronoun' : {'what'}
                        })

                        if not self._read_parse_tree(node.left, lexicon, context):
                            return False # if parse fails, return failure

                        if node.right != None:
                            if node.right.cat == 'VP':
                                lexicon = defaultdict(set, {
                                    'Verb' : {'is'},
                                    'Preposition' : {'in', 'inside'},
                                    'Noun' : {'there', CommandInputToken.placeholder()},
                                })

                                return self._read_parse_tree(node.right, lexicon, context) # result of right parse is the ultimate result
            elif node.cat == 'VP':
                # assume lexicon was appropriately configured previously
                if node.left != None and node.right != None:
                    return self._read_parse_tree(node.left, lexicon, context) and self._read_parse_tree(node.right, lexicon, context)
            elif node.cat == 'NP':
                if node.left != None and node.right != None:
                    if node.left.cat == 'NP' and node.right.cat == 'PP':
                        if not self._read_parse_tree(node.left, lexicon, context):
                            return False

                        lexicon['Noun'] = {'there', CommandInputToken.placeholder()}

                        return self._read_parse_tree(node.right, lexicon, context)
                    elif node.left.cat == 'Article' and node.right.cat == 'Noun':
                        return self._read_parse_tree(node.left, lexicon, context) and self._read_parse_tree(node.right, lexicon, context)
            elif node.cat == 'PP':
                if node.left != None and node.right != None:
                    return self._read_parse_tree(node.left, lexicon, context) and self._read_parse_tree(node.right, lexicon, context)

            return False # indicate failure if success isn't found above
        # if root is lexical, make sure word matches remaining lexicon
        else:
            if node.cat == 'Noun':
                if type(node.data) == CommandInputToken:
                    self.dir = node.data
                elif node.data == 'there':
                    self.dir = context.last_path
                elif node.data == 'contents':
                    lexicon['Noun'] = {'contents'}
                    lexicon['Preposition'] = {'of'}
                elif node.data == 'everything':
                    lexicon['Noun'] = {'everything'}
                    lexicon['Preposition'] = {'in', 'inside'}
                    lexicon['Article'] = set()

            return node.data in lexicon[node.cat]


class MoveCommand(Command):
    def __init__(self, tree: ParseTreeNode, context: Context):
        # defaults before reading parse
        self.src_path = None
        self.dest_path = None
        self.is_glob = False
        self.request = None

        self._read_parse_tree(tree, defaultdict(set), context)

        if self.is_valid():
            context.last_path = self.dest_path

    def __str__(self) -> str:
        glob = '/*' if self.is_glob else ''

        return f'mv {self.src_path.content}{glob} {self.dest_path.content}' if self.is_valid() else 'invalid command'

    def is_valid(self) -> bool:
        return self.src_path != None and self.dest_path != None

    def exec(self) -> str:
        result = Command.exec(self)

        # first, check for error
        if result.returncode != 0: # assumed to be error
            stderr = result.stderr

            if 'No such file or directory' in stderr: # yes, this could technically be broken, but it'll do for now
                responses = [
                    "Sorry, I couldn't [Verb] `src`",
                    "`src` doesn't seem to exist, so I couldn't [InputVerb] it"
                ]

                words = ['find', 'locate', 'see']

                response = random.choice(responses)
                word = random.choice(words)

                response = response.replace('[Verb]', word).replace('[InputVerb]', self.request).replace('src', self.src_path.content)
            else:
                # generic error
                response = self.general_error_message()
        else:
            stdout = result.stdout

            if self.is_glob:
                responses = [
                    'Everything in `src` has been moved to `dest`',
                    "I moved everything in `src` to `dest`"
                ]
            else:
                responses = [
                    "`src` is now located at `dest`",
                    "I've successfully [InputVerbPast] `src` to `dest`",
                ]

            response = random.choice(responses)
            verb = self.request + 'd'

            response = response.replace('[InputVerbPast]', verb).replace('`src`', f'`{self.src_path.content}`').replace('`dest`', f'`{self.dest_path.content}`')

        return response

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}, context: Context) -> bool:
        if node.data == None:
            if node.cat == 'S':
                if node.left != None and node.right != None:
                    # print(node.left.cat, node.right.cat)
                    if node.left.cat == 'Verb' and node.right.cat == 'NP':
                        # this is the only possible syntax -- lexicon varies
                        full_lexicon = defaultdict(set, {
                            'Verb' : {'move', 'rename', 'put', 'place'},
                            'Noun' : {'everything', 'there', CommandInputToken.placeholder()},
                            'Preposition' : {'to', 'in', 'inside', 'from'},
                        })

                        return self._read_parse_tree(node.left, full_lexicon, context) and self._read_parse_tree(node.right, full_lexicon, context)
            elif node.cat == 'NP':
                if node.left != None and node.right != None:
                    return node.left.cat == 'Noun' and self._read_parse_tree(node.left, lexicon, context) and self._read_parse_tree(node.right, lexicon, context)
            elif node.cat == 'PP':
                if node.left != None and node.right != None:
                    if node.left.cat == 'Preposition' and node.right.cat in {'Noun', 'NP'}:
                        return self._read_parse_tree(node.left, lexicon, context) and self._read_parse_tree(node.right, lexicon, context)

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
                elif node.data == 'there':
                    if self.src_path == None:
                        self.src_path = context.last_path
                    else:
                        self.dest_path = context.last_path
            elif node.cat == 'Verb':
                if node.data == 'rename':
                    lexicon['Preposition'] = {'to'}
                elif node.data in {'put', 'place'}:
                    lexicon['Preposition'] = {'in', 'inside'}

                if node.data != 'move' and 'everything' in lexicon['Noun']:
                    lexicon['Noun'].remove('everything')

                self.request = node.data.word

            return node.data in lexicon[node.cat]

class CopyCommand(Command):
    def __init__(self, tree: ParseTreeNode, context: Context):
        # defaults before reading parse
        self.src_path = None
        self.dest_path = None

        self._read_parse_tree(tree, defaultdict(set), context)

        if self.is_valid():
            context.last_path = self.dest_path

    def __str__(self) -> str:
        return f'cp {self.src_path.content} {self.dest_path.content}' if self.is_valid() else 'invalid command'

    def is_valid(self) -> bool:
        return self.src_path != None and self.dest_path != None

    def exec(self) -> str:
        result = Command.exec(self)

        # first, check for error
        if result.returncode != 0: # assumed to be error
            stderr = result.stderr

            if 'No such file or directory' in stderr: # yes, this could technically be broken, but it'll do for now
                responses = [
                    "Sorry, I couldn't [Verb] `src`",
                    "`src` doesn't seem to exist, so I couldn't [InputVerb] it"
                ]

                words = ['find', 'locate', 'see']
                input_verbs = ['copy', 'duplicate']

                response = random.choice(responses)
                word = random.choice(words)
                input_verb = random.choice(input_verbs)

                response = response.replace('[Verb]', word).replace('[InputVerb]', input_verb).replace('src', self.src_path.content)
            else:
                # generic error
                response = self.general_error_message()
        else:
            stdout = result.stdout

            responses = [
                "`src` has been [VerbPast] to `dest`",
                "I've successfully [VerbPast] `src` to `dest`",
            ]

            response = random.choice(responses)
            verb = random.choice(['copied', 'duplicated'])

            response = response.replace('[VerbPast]', verb).replace('`src`', f'`{self.src_path.content}`').replace('`dest`', f'`{self.dest_path.content}`')

        return response

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}, context: Context) -> bool:
        if node.data == None:
            if node.cat == 'S':
                if node.left != None and node.right != None:
                    if node.left.cat == 'Verb' and node.right.cat == 'NP':
                        # this is the only possible syntax -- lexicon varies
                        full_lexicon = defaultdict(set, {
                            'Verb' : {'copy', 'duplicate'},
                            'Noun' : {'there', CommandInputToken.placeholder()},
                            'Preposition' : {'to'},
                        })

                        return self._read_parse_tree(node.left, full_lexicon, context) and self._read_parse_tree(node.right, full_lexicon, context)
            elif node.cat == 'NP':
                if node.left != None and node.right != None:
                    return node.left.cat == 'Noun' and self._read_parse_tree(node.left, lexicon, context) and self._read_parse_tree(node.right, lexicon, context)
            elif node.cat == 'PP':
                if node.left != None and node.right != None:
                    if node.left.cat == 'Preposition' and node.right.cat in {'Noun', 'NP'}:
                        return self._read_parse_tree(node.left, lexicon, context) and self._read_parse_tree(node.right, lexicon, context)

            return False
        else:
            if node.cat == 'Noun':
                if type(node.data) == CommandInputToken:
                    if self.src_path == None:
                        self.src_path = node.data
                    else:
                        self.dest_path = node.data
                elif node.data == 'there':
                    if self.src_path == None:
                        self.src_path = context.last_path
                    else:
                        self.dest_path = context.last_path

            return node.data in lexicon[node.cat]

class RemoveCommand(Command):
    def __init__(self, tree: ParseTreeNode, context: Context):
        # defaults before reading parse
        self.path = None
        self.is_recursive = False

        self._read_parse_tree(tree, defaultdict(set), context)

        if self.is_valid():
            context.last_path = self.path

    def __str__(self) -> str:
        recursive = '-rf ' if self.is_recursive else ''

        return f'rm {recursive}{self.path.content}' if self.is_valid() else 'invalid command'

    def is_valid(self) -> bool:
        return self.path != None

    def exec(self) -> str:
        result = Command.exec(self)

        # first, check for error
        if result.returncode != 0: # assumed to be error
            stderr = result.stderr

            if 'No such file or directory' in stderr: # yes, this could technically be broken, but it'll do for now
                responses = [
                    "Sorry, I couldn't [Verb] `path`",
                    "`path` doesn't seem to exist, so I couldn't [InputVerb] it"
                ]

                words = ['find', 'locate', 'see']
                input_verbs = ['delete', 'remove']

                response = random.choice(responses)
                word = random.choice(words)
                input_verb = random.choice(input_verbs)

                response = response.replace('[Verb]', word).replace('[InputVerb]', input_verb).replace('path', self.path.content)
            elif 'is a directory' in stderr:
                response = "Sorry, I couldn't [Verb] `path` because it's a directory; did you mean to [Verb] it recursively?"

                input_verb = random.choice(['delete', 'remove'])
                response = response.replace('[Verb]', input_verb).replace('path', self.path.content)
            else:
                # generic error
                response = self.general_error_message()
        else:
            stdout = result.stdout

            responses = [
                "I've successfully [VerbPast] [Everything] `path` [Recursive]",
                "`path` has been [VerbPast] [Recursive]",
            ]

            if self.is_recursive:
                everything = random.choice(['', 'everything in'])
                recursive = random.choice(['', 'recursively'])
            else:
                everything = recursive = ''

            response = random.choice(responses)
            verb = random.choice(['deleted', 'removed'])

            response = response \
                .replace('[VerbPast]', verb) \
                .replace('[Everything]', everything) \
                .replace('[Recursive]', recursive) \
                .replace('`path`', f'`{self.path.content}`')

        return response

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}, context: Context) -> bool:
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

                    if not self._read_parse_tree(node.left, lexicon, context):
                        return False

                    lexicon = defaultdict(set, {
                        'Noun' : {'there', CommandInputToken.placeholder()},
                    })

                    if node.right.cat == 'NP':
                        lexicon['Noun'].add('everything')
                        lexicon['Preposition'] = {'in', 'inside'}
                    elif node.right.cat != 'Noun':
                        return False

                    return self._read_parse_tree(node.right, lexicon, context)
            elif node.cat == 'NP':
                if node.left != None and node.right != None:
                    if node.left.cat == 'Noun' and node.right.cat == 'PP':
                        lexicon['Noun'] = {'everything'}

                        if not self._read_parse_tree(node.left, lexicon, context):
                            return False

                        lexicon['Noun'] = {'there', CommandInputToken.placeholder()}
                        lexicon['Pronoun'] = {'there'}

                        return self._read_parse_tree(node.right, lexicon, context)
            elif node.cat == 'PP':
                if node.left != None and node.right != None:
                    if node.left.cat == 'Preposition' and node.right.cat == 'Noun':
                        return self._read_parse_tree(node.left, lexicon, context) and self._read_parse_tree(node.right, lexicon, context)
            elif node.cat == 'VP':
                if node.left != None and node.right != None:
                    if node.left.cat == 'Adverb' and node.right.cat == 'Verb':
                        return self._read_parse_tree(node.left, lexicon, context) and self._read_parse_tree(node.right, lexicon, context)

            return False
        else:
            if node.cat == 'Noun':
                if type(node.data) == CommandInputToken:
                    self.path = node.data
                elif node.data == 'everything':
                    self.is_recursive = True
                elif node.data == 'there':
                    self.path = context.last_path
            elif node.cat == 'Adverb' and node.data == 'recursively':
                self.is_recursive = True

            return node.data in lexicon[node.cat]


class RawCommand(Command):
    def __init__(self, tree: ParseTreeNode, context: Context):
        self.cmd = None
        self._read_parse_tree(tree, defaultdict(set), context)

    def __str__(self) -> str:
        return self.cmd.content if self.is_valid() else 'invalid command'

    def is_valid(self) -> bool:
        return self.cmd != None

    def exec(self) -> str:
        result = Command.exec(self)

        # first, check for error
        if result.returncode != 0: # assumed to be error
            response = self.general_error_message()
        else:
            stdout = result.stdout

            if stdout == '':
                response = 'I did it; nothing happened, but it was successful.'
            else:
                response = "Done; here's [Content]:" + '\n' + stdout

            content = random.choice(['what happened', 'what I got back', 'the results'])

        return response.replace('[Content]', content)

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}, context: Context) -> bool:
        if node.data == None:
            if node.left != None and node.right != None:
                if node.cat == 'S':
                    if node.left.cat == 'Verb' and node.right.cat == 'Noun':
                        lexicon = defaultdict(set, {
                            'Verb' : {'run', 'do', 'execute'},
                            'Noun' : {CommandInputToken.placeholder()},
                        })

                        return self._read_parse_tree(node.left, lexicon, context) and self._read_parse_tree(node.right, lexicon, context)

            return False
        else:
            if node.cat == 'Noun':
                if type(node.data) == CommandInputToken:
                    self.cmd = node.data

            return node.data in lexicon[node.cat]


class CommandGroup(Command):
    def __init__(self, tree: ParseTreeNode, context: Context):
        self.cmds = []
        self._read_parse_tree(tree, defaultdict(set), context)

    def __str__(self) -> str:
        return ' && '.join([str(cmd) for cmd in self.cmds])

    def is_valid(self) -> bool:
        return len(self.cmds) > 0

    def exec(self) -> str:
        return '\n'.join([cmd.exec() for cmd in self.cmds])

    def _read_parse_tree(self, node: ParseTreeNode, lexicon: {str : set}, context: Context) -> bool:
        if node.data == None:
            if node.left != None and node.right != None:
                if node.cat == 'S':
                    if node.left.cat == 'S' and node.right.cat == 'ConjClause':
                        lexicon = defaultdict(set, {
                            'Conj' : {'and', ConjunctorToken(), 'then'}
                        })

                        return self._read_parse_tree(node.left, lexicon, context) and self._read_parse_tree(node.right, lexicon, context)
                    else:
                        cmd = Command.from_parse_tree(node, context, include_group=False)

                        if cmd != None:
                            self.cmds.append(cmd)
                            return True
                        else:
                            self.cmds = []
                            return False
                elif node.cat == 'ConjClause':
                    return self._read_parse_tree(node.left, lexicon, context) and self._read_parse_tree(node.right, lexicon, context)

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
