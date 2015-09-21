#!/usr/bin/env python

import time
import argparse

import evebot
import evebot.bot
import evebot.settings

parser = argparse.ArgumentParser(description='Evebot the Slack bot', formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--debug', '-d', action='store_true', help='Enables debug (verbose) mode')
parser.add_argument('--version', action='version', version='Evebot v%s at your service.' % evebot.__version__)
parser.add_argument('--config', '-c', type=str, help='Yaml configuration filename')

args = parser.parse_args()

if args.debug:
    evebot.settings.config.enable_debug_mode()

if args.config:
    evebot.settings.config.load_yaml(args.config)

bot = evebot.bot.Bot()
bot.start()

while True:
    time.sleep(60)
