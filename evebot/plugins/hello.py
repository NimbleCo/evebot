import re
import random

from evebot.plugin import Plugin

class HelloPlugin(Plugin):
    NAME = 'Hello'
    HELP = [
        '`@{me} hello`',
        '`@{me} what\'s up`',
        '`@{me} what\'s cookin`',
        '`@{me} howdy`',
        '`@{me} good morning`',
    ]

    hello_re = re.compile(r'hello|what\'?s\s+(up|cookin)|howdy|good\s*morning|hey', re.IGNORECASE)
    answers = [
        '<@{user_id}> Hello {first_name}!',
        'Looking good today, <@{user_id}>!',
        'What\'s up, {first_name}?',
        'How can I help you today?',
        'Ahh, Mr {first_name} {last_name}! How nice it is to see you.'
    ]

    def on_event(self, event):
        if not event.is_plain_message():
            return

        if not event.am_i_mentioned() and not event.channel.is_direct:
            return

        if not HelloPlugin.hello_re.search(event.text):
            return

        self.send_message(event.channel, self.create_response(event))

    def create_response(self, event):
        return random.choice(HelloPlugin.answers).format(
            user_id = event.user.id,
            first_name = event.user.first_name,
            last_name = event.user.last_name
        )
