# -*- coding: utf-8 -*-
import websocket
import time
import json
import utils
import threading

class WebSocketClient():

    def __init__(self, server_url, callback_list):
        self.callback = callback_list
        self.server_url = server_url
        self.websocket = None
        self.close_requested = False

    def connect(self):

        while not self.close_requested:

            try:

                self.websocket = websocket.WebSocketApp(self.server_url, on_message=self.on_message)
                self.websocket.run_forever()
            
            except Exception as e:
                utils.error_log(e)
                pass

    def on_message(self, ws, message):

        try:
                     
            if not message == None:

                if message == "ping":

                    self.websocket.send("pong")

                else:

                    json_data = json.loads(message)

                    if json_data is not None and 'type' in json_data:

                        message_type = json_data['type']

                        if message_type in self.callback:
                            callback_function = self.callback[message_type]
                            callback_function(json_data)

                    else:

                        utils.error_log(f"Mensagem inválida ou ausente de tipo / {json_data}")

        except Exception as e:
            utils.error_log(e)
            
    def send(self, message):

        try:
            if self.websocket and self.websocket.sock and self.websocket.sock.connected:
                self.websocket.send(message)

        except Exception as e:
            utils.error_log(e)

    def close(self):

        try:
            if self.websocket:
                self.close_requested = True
                self.websocket.close()

        except Exception as e:
            utils.error_log(f"Erro ao encerrar a conexão WebSocket: {e}")

    def run(self):
        threading.Thread(target=self.connect, args=()).start()


