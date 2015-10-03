import re

from evebot.plugin import Plugin
from evebot.dispatcher import SubscriberType

class CommandsPlugin(Plugin):
    NAME = 'Commands'
    HELP = [
        '`@{me} !help`',
        '`@{me} !cleanup` - Clean up bot messages (last few)',
    ]

    SUBSCRIBES_TO = {SubscriberType.text_direct, SubscriberType.text_mentioned}

    def __init__(self, client, plugins):
        Plugin.__init__(self, client, plugins)

        self.command_re = re.compile(r'^<@' + self._me.id + '>\s+!(?P<command>\w+)$')

    def on_event(self, event):
        match = self.command_re.match(event.text.strip())

        if not match:
            return

        command = match.group('command').strip()

        if command == 'help':
            help_texts = self._plugins.get_help_text(event.channel.is_naughty)
            self._client.send_message(event.channel, '_I can serve you in many ways:_\n' + help_texts)
        elif command == 'cleanup':
            msgs = self._client.get_channel_history(event.channel)

            if msgs:
                for msg in msgs:
                    if msg['user'] == self._me.id:
                        self._client.delete_message(event.channel, msg['ts'])
        else:
            self._client.send_message(event.channel, 'Sorry, I don\'t know command *%s*.' % command)

