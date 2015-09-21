import re
import random

from evebot.plugin import Plugin
from evebot import helpers
from evebot.dispatcher import SubscriberType

class FortunePlugin(Plugin):
    NAME = 'Fortunes'
    HELP = [
        '`@{me} fortune (cow)`',
        '`@{me} what does cow say`',
    ]

    SUBSCRIBES_TO = {SubscriberType.text_direct, SubscriberType.text_mentioned}

    trigger_re = re.compile(r'fortune', re.IGNORECASE)
    cow_re = re.compile(r'what\s+(does\s+)?cow\s+say', re.IGNORECASE)

    cows = 'beavis.zen bong bud-frogs bunny cheese cower daemon default dragon dragon-and-cow elephant elephant-in-snake eyes flaming-sheep ghostbusters head-in hellokitty kiss kitty koala kosh luke-koala mech-and-cow meow milk moofasa moose mutilated ren satanic sheep skeleton small sodomized stegosaurus stimpy supermilker surgery telebears three-eyes turkey turtle tux udder vader vader-koala www'

    def on_event(self, event):
        if self.trigger_re.search(event.text):
            self.send_message(event.channel, self.create_response())
        elif self.cow_re.search(event.text):
            self.send_message(event.channel, self.create_cow_response())

    def create_response(self):
        out, err, code = helpers.run_command(['/usr/bin/fortune', '-s'])

        if code != 0:
            self._logger.error(err)
            return 'Sorry, could not get fortune.'

        return '>' + out.replace('\n', '\n>')

    def create_cow_response(self):
        cow = random.choice(self.cows.split(' '))
        out, err, code = helpers.run_command(['/usr/bin/bash', '-c', '/usr/bin/fortune -s | /usr/bin/cowsay -f %s' % cow])

        if code != 0:
            self._logger.error(err)
            return 'Sorry, could not get fortune.'

        return '```\n' + out + '\n```'

