#!/usr/bin/env python3

import functools
import glob
import os
import readline
import shlex
import subprocess
import sys
import time

VERSION = '2.0.2'

CACHE = {}
CACHE_TTL = 0.1
HISTORY = os.path.expanduser('~/.gitl_history')


def setup_environ():
    os.environ['GIT_DISCOVERY_ACROSS_FILESYSTEM'] = '1'


def setup_home():
    home = subprocess.run(['LC_ALL=C', 'perl', '-we', 'print((getpwuid $>)[7])'],
                          stdout=subprocess.PIPE)\
                     .stdout.decode('utf-8')
    os.environ['HOME'] = home


def cache(func):
    @functools.wraps(func)
    def inner(text):
        now = time.time()
        key = '{}:{}'.format(func.__name__, text)
        if key in CACHE:
            last_time, last_result = CACHE[key]
            if now - last_time < CACHE_TTL:
                return last_result
        result = func(text)
        CACHE[key] = (now, result)
        return result

    return inner


@cache
def complete_branches(text):
    with subprocess.Popen(['git', 'branch'],
                          stdout=subprocess.PIPE) as proc:
        branches = (line[2:-1].decode()
                    for line in proc.stdout.readlines())
        valid_branches = filter(lambda branch:
                                branch.startswith(text),
                                branches)
        return list(valid_branches)


@cache
def complete_paths(text):
    return glob.glob(text + '*')


def complete(text, state):
    completions = complete_branches(text) + complete_paths(text)
    return completions[state]


class Anchor:
    def __init__(self):
        self.root = os.getcwd().split('/')[-1] + ': '

    def __str__(self):
        return self.root


class GitLoop:
    def __init__(self):
        self.anchor = Anchor()
        self.init_readline()

    def init_readline(self):
        readline.parse_and_bind('tab: complete')
        readline.set_completer(complete)
        readline.set_completer_delims(' \t')
        self.init_history_file()
        readline.read_history_file(HISTORY)

    def run(self):
        try:
            while True:
                input_data = input(self.anchor)
                if input_data == '':
                    continue
                commands = input_data.split(';')
                for command in commands:
                    try:
                        subcommand = shlex.split(command)
                        subprocess.call(['git'] + subcommand)
                    except ValueError:
                        pass
        except (EOFError, KeyboardInterrupt):
            pass
        self.exit()

    def init_history_file(self):
        if not os.path.exists(HISTORY):
            with open(HISTORY, 'a'):
                pass

    def exit(self):
        readline.write_history_file(HISTORY)


class ArgsParser:
    def __init__(self, argv):
        self.argv = argv

    def two(self):
        return len(self.argv) == 2

    def first(self, option):
        return self.argv[1] == '--{}'.format(option)

    def is_version(self):
        return self.two() and self.first('version')

    def is_help(self):
        return self.two() and self.first('help')


class Command:
    @staticmethod
    def version():
        print('gitl version {}'.format(VERSION))

    @staticmethod
    def help():
        print('SYNOPSIS\n'
              '\tgitl\n\n'
              'OPTIONS\n'
              '\t--help     Print help\n'
              '\t--version  Print version\n')


def main():
    setup_environ()
    setup_home()
    args_parser = ArgsParser(sys.argv)
    if args_parser.is_version():
        Command.version()
    elif args_parser.is_help():
        Command.help()
    else:
        GitLoop().run()


if __name__ == '__main__':
    main()