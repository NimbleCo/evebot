import threading
import logging
import queue
import traceback

from evebot.settings import config
from evebot.dispatcher import SubscriberType

class Plugin(threading.Thread):
    NAME = 'Base'
    HELP = 'Don\'t do this.'
    IS_NAUGHTY = False
    SUBSCRIBES_TO = {SubscriberType.all}

    def __init__(self, client, plugins):
        threading.Thread.__init__(self)
        self._logger = logging.getLogger('%s.%s' % (self.__module__, self.__class__.__name__))
        self._client = client
        self._plugins = plugins
        self._me = self._client.get_me()
        self._q = queue.Queue()
        self._serve = True

    def send_message(self, channel, text):
        self._client.send_message(channel, text)

    def on_event(self, event):
        pass

    def process_event(self, event):
        self._q.put(event)

    def run(self):
        while self._serve:
            try:
                event = self._q.get(True, config.get('core.thread_sleep_time'))
            except queue.Empty:
                continue

            try:
                self.on_event(event)
            except Exception as e:
                if event.channel:
                    self._client.send_message(event.channel, ':angry: *You broke me (_but I live on_):* \n```' + traceback.format_exc() + '```')
                self._logger.exception(e)

        self.on_shutdown()

    def on_shutdown(self):
        self._logger.debug('Shutting down...')

    def shutdown(self):
        self._serve = False

    def __str__(self):
        return self.NAME
