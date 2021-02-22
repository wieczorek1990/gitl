#!/usr/bin/env python3

import functools
import glob
import os
import gnureadline as readline
import shlex
import signal
import subprocess
import sys
import time

VERSION = '1.2.1.4'

CACHE = {}
CACHE_TTL = 0.1


def run(args, stdout=subprocess.PIPE, env=None):
    output = subprocess.run(args, stdout=stdout, env=env).stdout
    if output is not None:
        return output.decode('utf-8')


def cache(function):
    @functools.wraps(function)
    def inner(text):
        now = time.time()
        key = '{}:{}'.format(function.__name__, text)
        if key in CACHE:
            last_time, last_result = CACHE[key]
            if now - last_time < CACHE_TTL:
                return last_result
        result = function(text)
        CACHE[key] = (now, result)
        return result

    return inner


@cache
def complete_branches(text):
    output = run(['git', 'branch'])
    branches = (line[2:]
                for line in output.splitlines())
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
        self.interrupt_counter = 0
        self.anchor = Anchor()
        self.history = self.init_history()
        self.init_readline()
        self.init_signal()

    def init_history(self):
        return os.path.expanduser('~/.gitl_history')

    def init_history_file(self):
        if not os.path.exists(self.history):
            with open(self.history, 'a'):
                pass

    def init_readline(self):
        readline.parse_and_bind('tab: complete')
        readline.set_completer(complete)
        readline.set_completer_delims(' \t')
        self.init_history_file()
        readline.read_history_file(self.history)

    def init_signal(self):
        signal.signal(signal.SIGINT, self.interrupt)

    def exit(self):
        readline.write_history_file(self.history)

    def interrupt(self, signum, frame):
        self.interrupt_counter += 1
        if self.interrupt_counter == 1:
            raise KeyboardInterrupt
        elif self.interrupt_counter == 2:
            self.exit()
            sys.exit(0)

    def execute(self, input_data):
        commands = input_data.split(';')
        for command in commands:
            try:
                subcommand = shlex.split(command)
                run(['git'] + subcommand, stdout=None)
            except ValueError:
                pass

    def run(self):
        while True:
            try:
                input_data = input(self.anchor)
                self.interrupt_counter = 0
                if input_data == '':
                    continue
                self.execute(input_data)
            except KeyboardInterrupt:
                print('^C')
            except EOFError:
                break
        self.exit()


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
    args_parser = ArgsParser(sys.argv)
    if args_parser.is_version():
        Command.version()
    elif args_parser.is_help():
        Command.help()
    else:
        GitLoop().run()


if __name__ == '__main__':
    main()
