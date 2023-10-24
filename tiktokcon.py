
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import *
from TikTokLive.types.errors import LiveNotFound, FailedFetchRoomInfo, AlreadyConnecting, InitialCursorMissing

import threading
import time
import utils
from auth import auth_data
import sys

class TikTokLiveThread():
    def __init__(self, listener_callbacks):
        super().__init__()

        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

        cookies = {
            "sessionid": authdata.SESSIONID(),
            "sid_guard": authdata.SIDGUARD(),
        }

        self.username = authdata.USERNAME()
        self.cookies = cookies
        self.listener_callbacks = listener_callbacks
        self.client = None
        self.running = False
        self.client_thread = None
        self.callback = None

    def callback_log(self, function):
        self.callback = function

    def run_client_thread(self):

        self.running = True

        while self.running:
            
            try:
                self.client = TikTokLiveClient(
                    unique_id=self.username,
                    enable_detailed_gifts=True,
                    additional_cookies=self.cookies,
                )

                for event, callback in self.listener_callbacks.items():
                    self.client.add_listener(event, callback)
                    
                self.client.run()

            except Exception as e:
                
                if isinstance(e, LiveNotFound):
                    if self.callback:
                        self.callback("Streamer não encontrado ou live offline, Tentando novamente...")

                elif isinstance(e, FailedFetchRoomInfo):

                    if self.callback:
                        self.callback(str(e))

                elif isinstance(e, InitialCursorMissing):

                    if self.callback:
                        self.callback("Erro de conexão com o TikTok, reinicie o programa.")
                else:
                    utils.error_log(e)
                    
                time.sleep(10)

    def run(self):
        self.client_thread = threading.Thread(target=self.run_client_thread)
        self.client_thread.start()
    
    def is_running(self):
        return self.running
    
    def close(self):
        self.running = False
        if self.client:
            self.client.stop()
            return
