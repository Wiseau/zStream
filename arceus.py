import requests
import config
import json
import logging


class Arceus:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.s = requests.session()

    def __getattr__(self, name):
        def function(*args):
            self.send([name] + list(args))

        return function

    def send(self, data):
        headers = {'X-PL-Token': config.arceus_token, 'content-type': 'application/json'}
        payload = {'action': 'raw', 'data': data}
        self.s.post(config.arceus_url, data=json.dumps(payload), headers=headers)
        self.logger.debug("Sent %s to Arceus" % data)
