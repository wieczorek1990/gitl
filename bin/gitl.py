#!/usr/bin/python3.5

import os
import readline
import shlex
import subprocess
import sys


class Anchor:
    def __init__(self):
        self.name = os.getcwd().split('/')[-1] + ': '


anchor = Anchor()
while True:
    input_ = input(anchor.name)
    if input_ == '':
        continue
    subcommand = shlex.split(input_)
    subprocess.call(['git'] + subcommand)
