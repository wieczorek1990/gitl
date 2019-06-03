#!/usr/bin/env python3

import functools
import glob
import os
import readline
import shlex
import subprocess
import sys
import time


CACHE = {}
CACHE_TTL = 0.1
VERSION = '0.1.0'


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


read_input = input
readline.parse_and_bind('tab: complete')
readline.set_completer(complete)
readline.set_completer_delims(' \t')


class Anchor:
    def __init__(self):
        self.root = os.getcwd().split('/')[-1] + ': '

    def __str__(self):
        return self.root


class GitLoop:
    def __init__(self):
        self.anchor = Anchor()

    def run(self):
        try:
            while True:
                input = read_input(self.anchor)
                if input == '':
                    continue
                commands = input.split(';')
                for command in commands:
                    try:
                        subcommand = shlex.split(command)
                        subprocess.call(['git'] + subcommand)
                    except ValueError:
                        pass
        except (EOFError, KeyboardInterrupt):
            pass

    def version(self):
        print('gitl version {}'.format(VERSION))

if __name__ == '__main__':
    git_loop = GitLoop()
    if len(sys.argv) == 2 and sys.argv[1] == '--version':
        git_loop.version()
    else:
        git_loop.run()
