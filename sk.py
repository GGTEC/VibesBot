import socket
import threading
import hashlib
import base64
import os
import time
from datetime import datetime
import utils
import json

clients = []
ping_interval = 5

appdata_path = os.getenv('APPDATA')

def error_log(ex):
    now = datetime.now()
    time_error = now.strftime("%d/%m/%Y %H:%M:%S")

    trace = []
    tb = ex.__traceback__

    while tb is not None:
        trace.append({
            "filename": tb.tb_frame.f_code.co_filename,
            "name": tb.tb_frame.f_code.co_name,
            "lineno": tb.tb_lineno
        })
        tb = tb.tb_next

    error = str(f'Erro = type: {type(ex).__name__} | message: {str(ex)} | trace: {trace} | time: {time_error} \n')

    with open(f"{appdata_path}/rewardevents/web/src/error_log.txt", "a+", encoding='utf-8') as log_file_r:
        log_file_r.write(error)

def handshake(client_socket):
    try:
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
        ).format(accept_key=generate_accept_key(key))

        client_socket.send(response.encode())
    except Exception as e:
        error_log(e)

def generate_accept_key(key):
    try:
        magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        concatenated = key + magic_string
        sha1 = hashlib.sha1(concatenated.encode())
        encoded = base64.b64encode(sha1.digest()).strip()
        return encoded.decode()
    except Exception as e:
        error_log(e)
        return ''

def send_ping(client_socket):
    try:
        while True:
            client_socket.send(encode_websocket_frame('ping'))
            time.sleep(ping_interval)

            response = client_socket.recv(4048)

            decoded_response = decode_websocket_frame(response)

            if str('pong') in str(decoded_response):
                continue

    except Exception as e:
        error_log(e)

    # Encerra a conexão com o cliente
    client_socket.close()
    clients.remove(client_socket)

def handle_client(client_socket):
    try:
        handshake(client_socket)
        clients.append(client_socket)

        threading.Thread(target=send_ping, args=(client_socket,)).start()
    except Exception as e:
        error_log(e)

def decode_websocket_frame(data):
    try:
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

        return decoded.decode()
    except Exception as e:
        error_log(e)
        return ''

def encode_websocket_frame(data):
    try:
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
    except Exception as e:
        error_log(e)
        return b''

def broadcast_message(message):
    for client in clients:
        try:
            client.send(encode_websocket_frame(message))
        except Exception as e:
            error_log(e)

def receive_message(client_socket):

    try:
        while True:

            data = client_socket.recv(4048)

            if not data:
                break
            message = decode_websocket_frame(data)

            if message:
                
                if 'likes' in message:

                    
                    data_goal = {
                        'type' : 'update_goal',
                        'type_goal' : 'likes',
                        'html' : utils.update_goal({'type_id' : 'update_goal','type_goal' :'likes'}),
                        'current' : int(0),
                        'goal' : 1000
                    }

                    broadcast_message(json.dumps(data_goal))

                if 'gift' in message:

                    data_goal = {
                        'type' : 'update_goal',
                        'type_goal' : 'gift',
                        'html' : utils.update_goal({'type_id' : 'update_goal','type_goal' :'gift'}),
                        'current' : int(0),
                        'goal' : 1000
                    }

                    broadcast_message(json.dumps(data_goal))

                if 'share' in message:

                    data_goal = {
                        'type' : 'update_goal',
                        'type_goal' : 'share',
                        'html' : utils.update_goal({'type_id' : 'update_goal','type_goal' :'share'}),
                        'current' : int(0),
                        'goal' : 1000
                    }

                    broadcast_message(json.dumps(data_goal))

                if 'diamonds' in message:

                    print(f'Mensagem recebida: {message}')

                    data_goal = {
                        'type' : 'update_goal',
                        'type_goal' : 'diamonds',
                        'html' : utils.update_goal({'type_id' : 'update_goal','type_goal' :'diamonds'}),
                        'current' : int(0),
                        'goal' : 1000
                    }

                    broadcast_message(json.dumps(data_goal))

                if 'max_viewer' in message:

                    data_goal = {
                        'type' : 'update_goal',
                        'type_goal' : 'max_viewer',
                        'html' : utils.update_goal({'type_id' : 'update_goal','type_goal' :'max_viewer'}),
                        'current' : int(0),
                        'goal' : 1000
                    }

                    broadcast_message(json.dumps(data_goal))

                if 'follow' in message:

                    data_goal = {
                        'type' : 'update_goal',
                        'type_goal' : 'follow',
                        'html' : utils.update_goal({'type_id' : 'update_goal','type_goal' :'follow'}),
                        'current' : int(0),
                        'goal' : 1000
                    }

                    broadcast_message(json.dumps(data_goal))
                     
    except Exception as e:
        error_log(e)
    
def start_server(host, port):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    while True:
        try:
            client_socket, address = server_socket.accept()
            print('Novo cliente conectado:', address)
            threading.Thread(target=handle_client, args=(client_socket,)).start()
            threading.Thread(target=receive_message, args=(client_socket,)).start()
        except Exception as e:
            error_log(e)
