import time
import threading
import json
import utils
from datetime import datetime
import socket
import hashlib
import base64

class WebSocketServer:

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.started = False
        self.server_closed = False
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections_by_type = {
            'music': {},
            'likes': {},
            'gift': {},
            'share': {},
            'diamonds': {},
            'max_viewer': {},
            'follow': {},
            'event': {},
            'tiktok': {},
            'alert' : {},
            'rank_likes': {},
            'rank_gifts': {},
            'rank_shares': {},
            'rank_points': {}
        }

    def error_log(self, ex):

        now = datetime.now()
        time_error = now.strftime("%d/%m/%Y %H:%M:%S")

        trace = []
        error_type = "Unknown"
        error_message = ""

        if isinstance(ex, BaseException):
            tb = ex.__traceback__

            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next

            error_type = type(ex).__name__
            error_message = str(ex)
        else:
            error_message = ex

        error = str(f'Erro = type: {error_type} | message: {error_message} | trace: {trace} | time: {time_error} \n\n')

        print(error)

    def on_client_disconnected(self, client_socket):

        client_id = str(client_socket.fileno())

        for type_conn, clients in self.connections_by_type.items():
            if client_id in clients:

                print(f"Disconectado - {type_conn}")

                if clients[client_id]['socket'] == client_socket:
                    del clients[client_id]

    def broadcast_message(self, message):

        message_loads = json.loads(message)
        
        if 'type_goal' in message_loads:
            connection_type = message_loads['type_goal']
        elif 'type' in message_loads:
            connection_type = message_loads['type']

        if connection_type in self.connections_by_type:

            connections_copy = self.connections_by_type[connection_type].copy()

            for client_id, client_info in connections_copy.items():
                
                client_socket = client_info["socket"]

                try:

                    client_socket.send(self.encode_websocket_frame(message))

                except ConnectionAbortedError as e:

                    self.on_client_disconnected(client_socket)

                except Exception as e:
                    
                    self.error_log(e)

    def add_client_to_type(self, connection_type, client_socket):


        print(f"Conectado - {connection_type}")

        client_id = str(client_socket.fileno())

        self.connections_by_type[connection_type][client_id] = {
            "socket": client_socket,
            "pong": time.time()
        }

    def create_goal_data(self, type_goal, current_value, goal_value):
        data_goal = {
            'type': 'update_goal',
            'type_goal': type_goal,
            'html': utils.update_goal({'type_id': 'update_goal', 'type_goal': type_goal}),
            'current': current_value,
            'goal': goal_value
        }
        return data_goal

    def message_received(self, client, message):

        json_data = json.loads(message.replace('\x00', ''))

        message_type = json_data['type']

        if message_type == 'likes':

            self.add_client_to_type('likes', client)

            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

            goal = goal_data['likes']['goal']
            total = goal_data['likes']['total_likes']

            data_goal = self.create_goal_data('likes', int(total), int(goal))

            self.broadcast_message(json.dumps(data_goal))
            
        elif message_type == 'gift':

            self.add_client_to_type('gift', client)

            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

            goal = goal_data['gift']['goal']
            total = goal_data['gift']['total_gifts']

            data_goal = self.create_goal_data('gift', int(total), int(goal))

            self.broadcast_message(json.dumps(data_goal))
            
        elif message_type == 'share':

            self.add_client_to_type('share', client)

            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

            goal = goal_data['share']['goal']
            total = goal_data['share']['total_share']

            data_goal = self.create_goal_data('share', int(total), int(goal))

            self.broadcast_message(json.dumps(data_goal))
            
        elif message_type == 'diamonds':

            self.add_client_to_type('diamonds', client)

            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

            goal = goal_data['diamonds']['goal']
            total = goal_data['diamonds']['total_diamonds']

            data_goal = self.create_goal_data('diamonds', int(total), int(goal))

            self.broadcast_message(json.dumps(data_goal))

        elif message_type == 'max_viewer':

            self.add_client_to_type('max_viewer', client)

            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

            goal = goal_data['max_viewer']['goal']
            total = goal_data['max_viewer']['total_viewer']

            data_goal = self.create_goal_data('max_viewer', int(total), int(goal))

            self.broadcast_message(json.dumps(data_goal))

        elif message_type == 'follow':

            self.add_client_to_type('follow', client)

            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

            goal = goal_data['follow']['goal']
            total = goal_data['follow']['total_follow']

            data_goal = self.create_goal_data('follow', int(total), int(goal))

            self.broadcast_message(json.dumps(data_goal))

        elif message_type == 'music':

            self.add_client_to_type('music', client)

        elif message_type == 'event':

            self.add_client_to_type('event', client)

        elif message_type == 'alert':

            self.add_client_to_type('alert', client)

        elif message_type == 'rank_likes':

            self.add_client_to_type('rank_likes', client)
        
        elif message_type == 'rank_gifts':

            self.add_client_to_type('rank_gifts', client)

        elif message_type == 'rank_shares':

            self.add_client_to_type('rank_shares', client)

        elif message_type == 'rank_points':

            self.add_client_to_type('rank_points', client)

        elif message_type == 'pong':

            client_id = str(client.fileno())

            for type_conn, clients in self.connections_by_type.items():

                if client_id in clients:

                    clients[client_id]['pong'] = time.time()

    def decode_websocket_frame(self, data):

        payload_length = data[1] & 127
        if payload_length <= 125:
            payload_start = 2
            mask = data[2:6]
        elif payload_length == 126:
            payload_start = 4
            mask = data[4:8]
        elif payload_length == 127:
            payload_start = 10
            mask = data[10:14]

        decoded = bytearray()

        for i in range(payload_start, len(data)):
            decoded.append(data[i] ^ mask[(i - payload_start) % 4])

        return decoded.decode('utf-8')

    def encode_websocket_frame(self, data):

        payload = data.encode()
        length = len(payload)
        encoded = bytearray()

        if length <= 125:
            encoded.append(129)
            encoded.append(length)
        elif length >= 126 and length <= 65535:
            encoded.append(129)
            encoded.append(126)
            encoded.extend(length.to_bytes(2, byteorder='big'))
        else:
            encoded.append(129)
            encoded.append(127)
            encoded.extend(length.to_bytes(8, byteorder='big'))

        encoded.extend(payload)

        return encoded

    def ping_clients(self):

        while self.server_closed == False:

            for connection_type, clients in self.connections_by_type.items():

                for client_id, client_info in list(clients.items()):

                    client_socket = client_info["socket"]

                    try:

                        client_socket.send(self.encode_websocket_frame('ping'))

                        pong_time = client_info['pong']
                        ping_time = time.time()

                        interval =  ping_time - pong_time

                        if int(interval) > 30:
                            self.on_client_disconnected(client_socket)

                    except ConnectionAbortedError as e:

                        self.on_client_disconnected(client_socket)

                    except Exception as e:

                        self.error_log(e)
                        self.on_client_disconnected(client_socket)

            time.sleep(30)

    def handshake(self, client_socket):

        data = client_socket.recv(1024).decode()

        key = ''
        for line in data.split('\r\n'):
            if 'Sec-WebSocket-Key:' in line:
                key = line.split(':')[1].strip()

        response = (
            'HTTP/1.1 101 Switching Protocols\r\n'
            'Upgrade: websocket\r\n'
            'Connection: Upgrade\r\n'
            'Sec-WebSocket-Accept: {accept_key}\r\n'
            'Access-Control-Allow-Origin: *\r\n'
            '\r\n'
        ).format(accept_key=self.generate_accept_key(key))

        client_socket.send(response.encode())

    def generate_accept_key(self, key):

        magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        concatenated = key + magic_string
        sha1 = hashlib.sha1(concatenated.encode())
        encoded = base64.b64encode(sha1.digest()).strip()

        return encoded.decode()
    
    def close_servers(self):
        
        self.server_closed = True
        for connection_type, clients in self.connections_by_type.items():

            for client_id, client_info in list(clients.items()):

                client_socket = client_info["socket"]
                
                client_socket.close()

                self.on_client_disconnected(client_socket)

        self.server.close()

    def handle_client(self, client_socket):

        self.handshake(client_socket)

        while True:
            
            try:
                
                data = client_socket.recv(1024)
                self.message_received(client_socket, self.decode_websocket_frame(data))

            except UnicodeDecodeError as e:
                    
                    if str(e) == "'utf-8' codec can't decode byte 0xe9 in position 5: unexpected end of data":
                        self.on_client_disconnected(client_socket)
                        break
            
            except ConnectionAbortedError as e:
                    
                    self.on_client_disconnected(client_socket)
                    break

            except Exception as e:
                    
                    self.error_log(e)
                    self.on_client_disconnected(client_socket)
                    break

    def start_server(self):

        th_ping = threading.Thread(target=self.ping_clients, args=())
        th_ping.start()

        self.server.bind((self.host, self.port))
        self.server.listen()

        self.started = True

        while True:

            try:

                if self.server.fileno() != -1 and self.server_closed == False:
                    
                    client_socket, client_address = self.server.accept()
                    threading.Thread(target= self.handle_client, args=(client_socket,)).start()

                else:
                    break
                
            except OSError as e:
                break

    def run(self):
        threading.Thread(target=self.start_server, args=(), daemon=True).start()

