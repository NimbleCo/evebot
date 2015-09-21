import time
import logging
import threading
import signal
import sys

from evebot.logging import init_logging
from evebot.settings import config
from evebot.client import Client
from evebot.dispatcher import Dispatcher


class Bot(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        init_logging()

        self.logger = logging.getLogger(__name__)

        token = config.get_api_token()

        if not token:
            self.logger.critical('Slack API Token is not set. Please set it in config file or EVEBOT_API_TOKEN env var.')
            sys.exit(2)

        self.client = Client(token)

        self.plugins = Dispatcher(self.client)
        self.me = self.client.get_me()
        self.serve = True

        self.plugins.start()

        self.logger.info('Connecting...')
        self.client.connect()
        self.logger.info('Logged in as "@%s".' % self.me.name)
        self.last_ping = 0

        signal.signal(signal.SIGINT, self.handle_interrupt)

    def shutdown(self):
        self.logger.info('Attempting graceful shutdown...')
        self.serve = False
        self.join(config.get('core.thread_join_timeout'))
        self.plugins.shutdown()

        sys.exit()

    def handle_interrupt(self, signum, frame):
        self.shutdown()

    def ping(self):
        now = int(time.time())

        if now - self.last_ping > config.get('core.ping_interval'):
            self.logger.debug('Ping...')
            self.client.ping()
            self.last_ping = now

    def run(self):
        while self.serve:
            try:
                events = self.client.read_events()
            except Exception as e:
                self.logger.exception(e)

            if len(events):
                for event in events:
                    if event.user == self.me:
                        self.logger.debug('Skipping message from myself.')

                        continue

                    self.plugins.dispatch(event)

            time.sleep(config.get('core.thread_sleep_time'))
            self.ping()

