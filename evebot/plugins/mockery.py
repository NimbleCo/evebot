import requests
import re
import random

from evebot.dispatcher import SubscriberType
from evebot.plugin import Plugin

class MockDelete(Plugin):
    NAME = 'Mock delete'
    HELP = 'Mocks users that delete their msgs.'
    IS_NAUGHTY = True
    SUBSCRIBES_TO = {SubscriberType.msg_deleted}

    probability = 2

    mock_texts = [
        '<@{user_id}>: You should have left this for posterity!',
        'And nothing of value was lost, {first_name}.',
        'Do you have something to hide {first_name}?',
        '<@{user_id}>: Here, I got it back for you:\n>{text}',
        'Honey, look what I found in the trash bin!\n*{full_name}*:\n>{text}',
        'Watch out! {first_name} is covering his tracks!',
        'And it rose from its grave.\n*{full_name}*:\n>{text}',
    ]

    def on_event(self, event):
        if not event.original:
            # buffer was not long enough
            return

        if random.randrange(1, self.probability) > 1:
            return

        self.send_message(event.channel, random.choice(self.mock_texts).format(
            text=event.original.text,
            user_id=event.original.user.id,
            first_name=event.original.user.get_first_name(),
            full_name=event.original.user.get_full_name()
        ))

class MockChange(Plugin):
    NAME = 'Mock change'
    HELP = 'Mocks users that edit their messages.'
    IS_NAUGHTY = True
    SUBSCRIBES_TO = {SubscriberType.msg_changed}

    probability = 3

    mock_texts = [
        'Did you make a mistake {first_name}?',
        'You cannot hide your mistakes from me {first_name}, you originally said `{text}`.',
        'Don\'t worry {first_name}, everybody makes mistakes.',
        'Alert! <@{user_id}> is trying to hide something.',
        'Here you go, I have fixed that for you!\n*{full_name}*:\n>{text}',

    ]

    def on_event(self, event):
        if not event.old:
            # buffer was not long enough
            return

        if random.randrange(1, self.probability) > 1:
            return

        self.send_message(event.channel, random.choice(self.mock_texts).format(
            text=event.old.text,
            user_id=event.old.user.id,
            first_name=event.old.user.get_first_name(),
            full_name=event.old.user.get_full_name()
        ))