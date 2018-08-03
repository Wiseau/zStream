import time
import websocket
import logging
import json

from killmail import Killmail


class ZSocket:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def start(self):
        self.logger.info("Connected to zkillboard websocket...")
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp("wss://zkillboard.com:2096")
        ws.on_message = self.on_message
        ws.on_open = self.on_open
        ws.on_error = self.on_error
        ws.run_forever()

    def on_message(self, ws, message):
        k = json.loads(message)
        self.on_killmail(ws, Killmail(k))
        self.socket_message(ws, message)

    def on_open(self, ws):
        self.logger.info("Successful connection to zkillboard websocket")
        payload = {"action": "sub", "channel": "killstream"}
        ws.send(json.dumps(payload))
        self.socket_open(ws)

    def on_error(self, ws, err):
        self.logger.error("socket dropped with error: %s" % err)
        self.socket_error(ws, err)
        time.sleep(3)
        self.start()

    def socket_open(self, ws):
        pass

    def socket_error(self, ws, err):
        pass

    def socket_message(self, ws, message):
        pass

    def on_killmail(self, ws, killmail):
        self.logger.info("Received killmail %s" % killmail['killmail_id'])
