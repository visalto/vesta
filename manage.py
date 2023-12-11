import argparse
import fnmatch
import logging
import os
from pathlib import Path
from typing import List, Union

import click

from __platform__.vesta_mgmt_internal.service_model import Vesta

logging.basicConfig(level='INFO')
# todo: Automatically create external network if it doesnt exist

logger = logging.getLogger(__name__)
VESTA = 'vesta'
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR.joinpath('.env')
platform = Vesta(BASE_DIR)
parser = argparse.ArgumentParser(description='Vesta management')
parser.add_argument('--env', '-e', help='environment file', default=ENV_FILE)
parser.add_argument('command', choices=[
                    'start', 'stop', 'init'], help='Commands to interact with the system')


def run_init():
    vesta_init = platform.service('vesta-init')
    vesta_init.start()


def start():
    platform.start_services()


def stop():
    platform.stop_services()


def main():
    args = parser.parse_args()
    if args.command == 'init':
        run_init()
    if args.command == 'start':
        start()
    if args.command == 'stop':
        stop()


if __name__ == '__main__':
    main()
