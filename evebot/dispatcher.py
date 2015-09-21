import importlib
import logging

from evebot.settings import config
from enum import Enum

class SubscriberType(Enum):
    all = 1                 # all events
    text = 2                # plain text message events
    text_mentioned = 3      # plain text messages where bot is mentioned
    text_direct = 4         # plain text messages in direct channel with bot

class Dispatcher:
    def __init__(self, client):
        self._logger = logging.getLogger(__name__)
        self._client = client
        self._plugins = []

        for plugin_path in config.get_enabled_plugins():
            cls = self.get_class(plugin_path)
            plugin = cls(self._client, self)
            self._plugins.append(plugin)
            self._logger.info('Loaded plugin "%s" (%s).', plugin.NAME, plugin_path)

    def start(self):
        for plugin in self._plugins:
            plugin.start()

    def get_help_text(self, include_naughty = True):
        text = ''

        for plugin in self._plugins:
            if not include_naughty and plugin.IS_NAUGHTY:
                continue

            icon = ''

            if plugin.IS_NAUGHTY:
                icon = ':suspect:'

            plugin_text = plugin.HELP

            if isinstance(plugin_text, list):
                plugin_text = '\n> '.join(plugin_text)

            plugin_text = '\n*{name}* {icon} \n> ' + plugin_text
            plugin_text = plugin_text.format(me=self._client.get_me().name, name=plugin.NAME, icon=icon)
            text += plugin_text

        return text

    def filter_plugins(self, subscriber_type):
        return set(filter(lambda plugin: subscriber_type in plugin.SUBSCRIBES_TO, self._plugins))

    def dispatch(self, event):
        plugins = self.filter_plugins(SubscriberType.all)

        if event.is_plain_message():
            plugins |= self.filter_plugins(SubscriberType.text)

            if event.channel and event.channel.is_direct:
                plugins |= self.filter_plugins(SubscriberType.text_direct)

            if event.am_i_mentioned():
                plugins |= self.filter_plugins(SubscriberType.text_mentioned)

        if event.channel and not event.channel.is_naughty:
            plugins = filter(lambda plugin: not plugin.IS_NAUGHTY, plugins)

        for plugin in plugins:
            plugin.process_event(event)

    def shutdown(self):
        for plugin in self._plugins:
            plugin.shutdown()

        for plugin in self._plugins:
            plugin.join(config.get('core.thread_join_timeout'))

    def get_class(self, class_path):
        module_name, class_name = class_path.rsplit(".", 1)
        return getattr(importlib.import_module(module_name), class_name)

