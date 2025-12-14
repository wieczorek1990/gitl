#!/usr/bin/env python3

import functools
import glob
import os
import shlex
import signal
import subprocess
import sys
import time

import gnureadline as readline

VERSION = "2.2.0.14"

CACHE = {}
CACHE_TTL = 0.1

TWO_DOTS = ".."
TWO_DOTS_LENGTH = len(TWO_DOTS)


def run(args, stdout=subprocess.PIPE, env=None):
    output = subprocess.run(args, stdout=stdout, env=env).stdout
    if output is not None:
        return output.decode("utf-8")


def cache(function):
    @functools.wraps(function)
    def inner(text, *args, **kwargs):
        now = time.time()

        function_name = function.__name__
        key = f"{function_name}:{text}"

        if key in CACHE:
            last_time, last_result = CACHE[key]
            if now - last_time < CACHE_TTL:
                return last_result

        result = function(text, *args, **kwargs)
        CACHE[key] = (now, result)
        return result

    return inner


def valid_completions(iterable, text):
    valid_completions_iterator = filter(
        lambda entry: entry.startswith(text), iterable
    )
    return list(valid_completions_iterator)


@cache
def complete_branches(text):
    output = run(["git", "branch"])
    if not output:
        return []
    branches = (line[2:] for line in output.splitlines())
    return valid_completions(branches, text)


@cache
def complete_tags(text):
    output = run(["git", "tag"])
    if not output:
        return []
    tags = (line for line in output.splitlines())
    return valid_completions(tags, text)


@cache
def complete_paths(text):
    paths = glob.glob(f"{text}*")
    paths = [f"'{path}'" for path in paths]
    return paths


def split(text):
    try:
        index_of_two_dots = text.index(TWO_DOTS)
    except ValueError:
        return None
    else:
        text_before = text[:index_of_two_dots]
        index_after_two_dots = index_of_two_dots + TWO_DOTS_LENGTH
        text_after = text[index_after_two_dots:]
        return text_before, text_after


def prefix_completions(prefix, completions):
    prefixed_completions = [
        f"{prefix}{completion}" for completion in completions
    ]
    return prefixed_completions


def complete(text, state):
    text_parts = split(text)
    if text_parts is None:
        branches = complete_branches(text)
        tags = complete_tags(text)
    else:
        text_before, text_after = text_parts
        prefix = f"{text_before}{TWO_DOTS}"

        branches_without_prefix = complete_branches(text_after)
        tags_without_prefix = complete_tags(text_after)

        branches = prefix_completions(prefix, branches_without_prefix)
        tags = prefix_completions(prefix, tags_without_prefix)
    paths = complete_paths(text)

    completions = branches + tags + paths
    return completions[state]


class Anchor:
    def __init__(self):
        root = os.getcwd().split("/")[-1]
        self.root = "{}: ".format(root)

    def __str__(self):
        return self.root


class Character:
    SINGLE_QUOTATION_MARK = "'"
    DOUBLE_QUOTATION_MARK = '"'
    SEMICOLON = ";"


class GitLoop:
    def __init__(self):
        self.interrupt_counter = 0
        self.anchor = Anchor()
        self.history = self.init_history()
        self.init_readline()
        self.init_signal()

    @staticmethod
    def init_history():
        return os.path.expanduser("~/.gitl_history")

    def init_history_file(self):
        if not os.path.exists(self.history):
            with open(self.history, "a"):
                pass

    def init_readline(self):
        readline.parse_and_bind("tab: complete")
        readline.set_completer(complete)
        readline.set_completer_delims(" \t")
        self.init_history_file()
        readline.read_history_file(self.history)

    def init_signal(self):
        signal.signal(signal.SIGINT, self.interrupt)

    def exit(self):
        readline.write_history_file(self.history)

    def interrupt(self, signum, frame):  # noqa
        self.interrupt_counter += 1
        if self.interrupt_counter == 1:
            raise KeyboardInterrupt()
        elif self.interrupt_counter == 2:
            self.exit()
            sys.exit(0)

    @staticmethod
    def get_commands(input_data):
        commands = []
        current_command = []
        in_single_quoted_string = False
        in_double_quoted_string = False

        def append():
            original_command = "".join(current_command)
            command = original_command.strip()
            commands.append(command)

        for character in input_data:
            match character:
                case Character.SINGLE_QUOTATION_MARK:
                    if not in_double_quoted_string:
                        in_single_quoted_string = not in_single_quoted_string
                case Character.DOUBLE_QUOTATION_MARK:
                    if not in_single_quoted_string:
                        in_double_quoted_string = not in_double_quoted_string
                case Character.SEMICOLON:
                    ignore_semicolon = (
                        in_single_quoted_string or in_double_quoted_string
                    )
                    if not ignore_semicolon:
                        append()
                        current_command = []
                        continue
            current_command.append(character)
        append()
        return commands

    @classmethod
    def execute_command(cls, command):
        command = shlex.split(command)
        run(["git"] + command, stdout=1)

    @classmethod
    def execute(cls, input_data):
        commands = cls.get_commands(input_data)
        for command in commands:
            # empty command
            if command == "":
                continue
            try:
                # split command by semicolon
                multicommand = command.split(";")

                for subcommand in multicommand:
                    cls.execute_command(subcommand)
            except ValueError:
                pass

    def run(self):
        while True:
            try:
                input_data = input(self.anchor)
                self.interrupt_counter = 0
                self.execute(input_data)
            except KeyboardInterrupt:
                print("^C")
            except EOFError:
                break
        self.exit()


class ArgsParser:
    def __init__(self, argv):
        self.argv = argv

    def two(self):
        return len(self.argv) == 2

    def first(self, option):
        return self.argv[1] == "--{}".format(option)

    def is_version(self):
        return self.two() and self.first("version")

    def is_help(self):
        return self.two() and self.first("help")


class Command:
    @staticmethod
    def version():
        print("gitl version {}".format(VERSION))

    @staticmethod
    def help():
        print(
            "SYNOPSIS\n"
            "\tgitl\n\n"
            "OPTIONS\n"
            "\t--help     Print help\n"
            "\t--version  Print version\n"
        )


def main():
    args_parser = ArgsParser(sys.argv)
    if args_parser.is_version():
        Command.version()
    elif args_parser.is_help():
        Command.help()
    else:
        GitLoop().run()


if __name__ == "__main__":
    main()
