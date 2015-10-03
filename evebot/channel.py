import collections

from evebot.settings import config

class MessageBuffer:
    def __init__(self):
        self._messages = {}
        self._timestamps = collections.deque([])
        self._size = config.get('core.channel_message_buffer_size')

    def store(self, msg):
        if not msg.user in self._messages:
            self._messages[msg.user] = {}

        self._messages[msg.user][msg.ts] = msg
        self._timestamps.append((msg.ts, msg.user))

        if len(self._timestamps) > self._size:
            ts, user = self._timestamps.popleft()
            del self._messages[user][ts]

        print (self._timestamps)

    def find(self, ts, user):
        if user in self._messages:
            if ts in self._messages[user]:
                return self._messages[user][ts]

        return None

class Channel:
    TYPE_CHANNEL = 'CHANNEL'
    TYPE_GROUP = 'GROUP'
    TYPE_DIRECT = 'DIRECT'

    type_mapping = {
        'C': 'CHANNEL',
        'G': 'GROUP',
        'D': 'DIRECT'
    }

    def __init__(self, data):
        self.data = data
        self.messages = MessageBuffer()

        self.type = self.get_channel_type(data['id'])
        self.is_group = self.type == self.TYPE_GROUP
        self.is_direct = self.type == self.TYPE_DIRECT
        self.is_channel = self.type == self.TYPE_CHANNEL

        self.is_naughty = (
            (self.id in config.get_naughty_channels() or self.name in config.get_naughty_channels()) or
            (config.are_ims_naughty() and self.is_direct)
        )

    def __eq__(self, other):
        return isinstance(other, Channel) and self.id == other.id

    def __getattr__(self, name):
        if name not in self.data:
            return None

        return self.data[name]

    def __str__(self):
        return 'Channel("%s" [%s])' % (self.name, self.id)

    def store_message(self, msg):
        self.messages.store(msg)

    def find_message(self, ts, user):
        return self.messages.find(ts, user)

    @staticmethod
    def get_channel_type(id):
        return Channel.type_mapping[id[:1]]

    def get_type(self):
        return self.type_mapping[self.id[:1]]

