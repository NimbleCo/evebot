import json
import logging

from slackclient import SlackClient

from evebot.event import Event, Message
from evebot.user import User
from evebot.channel import Channel
from evebot.settings import config


class Client:
    METHOD_GET_USER_INFO = 'users.info'
    METHOD_AUTH_TEST = 'auth.test'
    METHOD_DELETE_MSG = 'chat.delete'

    METHOD_GET_CHANNEL_INFO = {
        Channel.TYPE_CHANNEL: 'channels.info',
        Channel.TYPE_GROUP: 'groups.info'
    }

    METHOD_GET_HISTORY = {
        Channel.TYPE_CHANNEL: 'channels.history',
        Channel.TYPE_GROUP: 'groups.history',
        Channel.TYPE_DIRECT: 'im.history',
    }

    users = {}
    channels = {}

    def __init__(self, api_key):
        self._client = SlackClient(api_key)
        self._logger = logging.getLogger(__name__)
        self._me = None

    def connect(self):
        self._client.rtm_connect()

    def send_message(self, channel, text):
        self._logger.debug('Sent message "%s" to channel "%s"' % (text, channel))

        self._client.rtm_send_message(channel.id, text)

    def ping(self):
        self._client.server.ping()

    def get_user(self, id, force = False):
        if not id in self.users or force:
            response = self.call_method(Client.METHOD_GET_USER_INFO, user = id)

            if response:
                self.users[id] = User(response['user'])
            else:
                self._logger.warn('Could not fetch info for user "%s".' % id)
                return None

        return self.users[id]

    def get_me(self):
        if not self._me:
            response = self.call_method(Client.METHOD_AUTH_TEST)

            if response:
                self._me = self.get_user(response['user_id'])
            else:
                return None

        return self._me

    def get_channel(self, id):
        if id not in self.channels:
            type = Channel.get_channel_type(id)

            if type == Channel.TYPE_DIRECT:
                self.channels[id] = Channel({'id': id})
                return self.channels[id]
            elif type == Channel.TYPE_GROUP:
                data_key = 'group'
            elif type == Channel.TYPE_CHANNEL:
                data_key = 'channel'

            response = self.call_method(self.METHOD_GET_CHANNEL_INFO[type], channel = id)

            if response:
                self.channels[id] = Channel(response[data_key])
            else:
                self._logger.warn('Could not fetch info for channel "%s".' % id)
                return None

        return self.channels[id]

    def get_channel_history(self, channel):
        response = self.call_method(self.METHOD_GET_HISTORY[channel.type], channel=channel.id)

        if not response:
            return None

        return response['messages']

    def delete_message(self, channel, timestamp):
        self.call_method(self.METHOD_DELETE_MSG, channel=channel.id, ts=timestamp)

    def call_method(self, method, **kwargs):
        response = json.loads(self._client.api_call(method, **kwargs).decode('utf-8'))

        if not 'ok' in response or not response['ok']:
            if 'error' in response:
                self._logger.warn('API call "%s" failed: %s.' % (method, response['error']))
            else:
                self._logger.warn('API call "%s" failed.' % method)

            return None

        return response

    def process_special_event(self, event):
        if 'user' in event.data and isinstance(event.data['user'], dict):
            new_user = User(event.user)
            event.data['user'] = new_user
            self.users[new_user.id] = new_user

        if 'channel' in event.data and isinstance(event.data['channel'], dict):
            new_channel = Channel(event.channel)
            event.data['channel'] = new_channel
            self.channels[new_channel.id] = new_channel

    def read_events(self):
        events = []

        try:
            event_datas = self._client.rtm_read()
        except BlockingIOError:
            self._logger.debug('Socket is blocked (by another thread?)...')
            return []

        for event_data in event_datas:
            self._logger.debug('Read event: ' + str(event_data))

            if not 'type' in event_data:
                continue

            if event_data['type'] == Event.TYPE_MESSAGE:
                event = Message(self, event_data)
            else:
                event = Event(self, event_data)

            self.process_special_event(event)

            self._logger.debug('Event parsed:\n' + str(event))

            events.append(event)

        return events

