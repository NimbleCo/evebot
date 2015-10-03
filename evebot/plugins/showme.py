import re

from evebot.plugin import Plugin
from evebot.dispatcher import SubscriberType
import random
import requests

class ShowmePlugin(Plugin):
    NAME = 'Show Me'
    HELP = [
        '`@{me} (image|show|gimme|give)(\s+me)?\s+((some|da|an?)\s+)? <something>`',
    ]

    SUBSCRIBES_TO = {SubscriberType.text_direct, SubscriberType.text_mentioned}

    command_re = re.compile(r'(image|show|gimme|give)(\s+me)?\s+((some|da|an?)\s+)?(?P<command>[^@$<\s]+)', re.IGNORECASE)

    def on_event(self, event):
        match = self.command_re.search(event.text)

        if not match:
            self._logger.debug('Message text "%s" does not match re.' % event.text)
            return

        command = match.group('command').strip().lower()
        self.on_command(command, event.channel, event.user)

    def on_command(self, command, channel, user):
        pass


class ShowmeNiceStuffPlugin(ShowmePlugin):
    NAME = 'Show me nice stuff'
    HELP = ShowmePlugin.HELP + [
        '',
        '_Known stuff_:',
        '*cat* - shows a random cat',
        '*ryan (gosling)|programmer* - guess who'
    ]

    cat_responses = [
        'Somebody mentioned a cat, huh? \n {url}',
        'Kitten coming your way. \n {url}',
        '{url} \n Kittymageddon.',
        'Come on {name}, you know you like cats! \n {url}',
        'Cat-o-matic at your service {name}! \n {url}',
    ]

    ryan_responses = [
        '{url}'
    ]


    def on_command(self, command, channel, user):
        if re.match(r'(cat|kitten|kitty|puss|pussy(ies)?|pussycat)s?', command, re.IGNORECASE):
            response = requests.head('http://thecatapi.com/api/images/get')

            if response.status_code != 302 or not 'location' in response.headers:
                self.send_message(channel, 'No kittens this time. :cry:')

            self.send_message(channel, random.choice(self.cat_responses).format(
                url=response.headers['location'],
                name=user.get_first_name()
            ))
        elif re.match(r'(ryan(\s+gosling)?|programmer|love)s?', command, re.IGNORECASE):
            response = requests.head('http://programmerryangosling.tumblr.com/random')

            if response.status_code != 302 or not 'location' in response.headers:
                self.send_message(channel, 'No gosling this time. :cry:')

            self.send_message(channel, random.choice(self.ryan_responses).format(
                url=response.headers['location'],
            ))
