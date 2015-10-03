import logging
import re

from datetime import datetime

class Event:
    TYPE_HELLO = 'hello'
    TYPE_MESSAGE = 'message'
    TYPE_PRESENCE_CHANGE = 'presence_change'
    TYPE_GROUP_JOINED = 'group_joined'
    TYPE_USER_TYPING = 'user_typing'
    TYPE_USER_CHANGE = 'user_change'
    TYPE_CHANNEL_CREATED = 'channel_created'

    def __init__(self, client, data):
        self._client = client
        self._logger = logging.getLogger(__name__)
        self.data = data

        if 'channel' in self.data and isinstance(self.data['channel'], str):
            self.data['channel'] = self._client.get_channel(self.data['channel'])

        if 'user' in self.data and isinstance(self.data['user'], str):
            self.data['user'] = self._client.get_user(self.data['user'])

        if 'ts' in self.data:
            self.time = datetime.fromtimestamp(int(float(self.data['ts'])))

    def __getattr__(self, name):
        if not name in self.data:
            return None

        return self.data[name]

    def __str__(self):
        s = 'Event(%s):' % self.type

        for k, v in self.data.items():
            if k != 'type':
                s += '\n    %s: %s' % (k, v)

        return s

    @staticmethod
    def create(client, data):
        if data['type'] == Event.TYPE_MESSAGE:
            return Message.create(client, data)

        return Event(client, data)

    def is_hidden(self):
        return 'hidden' in self.data and self.data['hidden']

    def is_message(self):
        return self.type == Event.TYPE_MESSAGE

    def is_presence_change(self):
        return self.type == Event.TYPE_PRESENCE_CHANGE

    def is_group_joined(self):
        return self.type == Event.TYPE_GROUP_JOINED

    def is_user_typing(self):
        return self.type == Event.TYPE_USER_TYPING


class Message(Event):
    SUBTYPE_ME_MESSAGE = 'me_message'
    SUBTYPE_BOT_MESSAGE = 'bot_message'
    SUBTYPE_MESSAGE_CHANGED = 'message_changed'
    SUBTYPE_MESSAGE_DELETED = 'message_deleted'
    SUBTYPE_CHANNEL_JOIN = 'channel_join'
    SUBTYPE_CHANNEL_LEAVE = 'channel_leave'
    SUBTYPE_CHANNEL_TOPIC = 'channel_topic'
    SUBTYPE_CHANNEL_PURPOSE = 'channel_purpose'

    mention_re = re.compile(r'<@(\w+)(?:\|([^>]+))?>:?([^<$]+)?')

    def __init__(self, client, data):
        Event.__init__(self, client, data)

        self.mentions = {}

        if 'text' in self.data:
            matches = Message.mention_re.findall(self.data['text'])

            for user_id, name, text in matches:
                self.mentions[user_id] = {'user': self._client.get_user(user_id), 'text': text}

    @staticmethod
    def create(client, data):
        if 'subtype' in data:
            if data['subtype'] == Message.SUBTYPE_MESSAGE_DELETED:
                return MessageDeleted(client, data)

            if data['subtype'] == Message.SUBTYPE_MESSAGE_CHANGED:
                return MessageChanged(client, data)

        return Message(client, data)

    def am_i_mentioned(self):
        return self.is_mentioned(self._client.get_me())

    def is_mentioned(self, user):
        return user.id in self.mentions

    def is_me_message(self):
        return self.data['subtype'] == Message.SUBTYPE_ME_MESSAGE

    def is_plain(self):
        return not 'subtype' in self.data


class MessageDeleted(Message):
    def __init__(self, client, data):
        Message.__init__(self, client, data)
        self.original = self.channel.find_message(self.deleted_ts)

class MessageChanged(Message):
    def __init__(self, client, data):
        Message.__init__(self, client, data)

        self.new = Message.create(client, {
            'text': data['message']['text'],
            'channel': self.channel,
            'user': self._client.get_user(data['message']['user']),
            'ts': data['message']['edited']['ts'],
        })

        self.old = self.channel.find_message(data['message']['ts'])