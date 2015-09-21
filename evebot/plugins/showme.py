import re

from evebot.plugin import Plugin
from evebot.dispatcher import SubscriberType

class ShowmePlugin(Plugin):
    NAME = 'Show Me'
    HELP = [
        '`@{me} show me (some|da) <something>`',
        '`@{me} gimme (some|da) <something>`',
        '`@{me} give me (some|da) <something>`',
    ]

    SUBSCRIBES_TO = {SubscriberType.text_direct, SubscriberType.text_mentioned}

    command_re = re.compile(r'(image|show|gimme|give)(\s+me)?\s+((some|da)\s+)?([^@$<\s]+)', re.IGNORECASE)

    def on_event(self, event):
        match = self.command_re.search(event.text)

        if not match:
            self._logger.debug('Message text "%s" does not match re.' % event.text)
            return

        command = match.group(5).strip().lower()
        self.on_command(command, event.channel, event.user)

    def on_command(self, command, channel, user):
        pass

