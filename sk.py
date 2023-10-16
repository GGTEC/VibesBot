from websocket_server import WebsocketServer
import time
import threading
import json
import utils
from datetime import datetime


connections_by_type = {
    'music': {},
    'likes': {},
    'gift': {},
    'share': {},
    'diamonds': {},
    'max_viewer': {},
    'follow': {},
}

last_pong_times = {}


def on_client_connected(client, server):
    print(f'Cliente conectado: {client["address"]}')

def on_client_disconnected(client, server):
    client_id = client['id']
    print(f'Cliente desconectado: {client["address"]}')
    for connection_type in connections_by_type:
        if client_id in connections_by_type[connection_type]:
            del connections_by_type[connection_type][client_id]

def broadcast_message(message):
    message_loads = json.loads(message) 
    if 'type_goal' in message_loads:
        connection_type = message_loads['type_goal']
    else:
        connection_type = 'music'
    if connection_type in connections_by_type:
        for client in connections_by_type[connection_type].values():
            client_handler = client['handler']
            try:
                client_handler.send_message(message)
            except Exception as e:
                utils.error_log(e)

def add_client_to_type(connection_type, client):
    client_id = client['id']
    connections_by_type[connection_type][client_id] = {
        "handler": client['handler'],
        "addr": client['address'][0]
    }

def create_goal_data(type_goal, current_value, goal_value):

    data_goal = {
        'type': 'update_goal',
        'type_goal': type_goal,
        'html': utils.update_goal({'type_id': 'update_goal', 'type_goal': type_goal}),
        'current': current_value,
        'goal': goal_value
    }

    return data_goal

def message_received(client, server, message):

    if 'likes' in message:

        add_client_to_type('likes', client)

        data_goal = create_goal_data('likes', 0, 1000)

        broadcast_message(json.dumps(data_goal))
        
    elif 'gift' in message:

        add_client_to_type('gift', client)

        data_goal = create_goal_data('gift', 0, 1000)

        broadcast_message(json.dumps(data_goal))
        
    elif 'share' in message:

        add_client_to_type('share', client)

        data_goal = create_goal_data('likes', 0, 1000)

        broadcast_message(json.dumps(data_goal))
        
    elif 'diamonds' in message:

        add_client_to_type('diamonds', client)

        data_goal = create_goal_data('diamonds', 0, 1000)

        broadcast_message(json.dumps(data_goal))

    elif 'max_viewer' in message:

        add_client_to_type('max_viewer', client)

        data_goal = create_goal_data('max_viewer', 0, 1000)

        broadcast_message(json.dumps(data_goal))

    elif 'follow' in message:

        add_client_to_type('follow', client)

        data_goal = create_goal_data('follow', 0, 1000)

        broadcast_message(json.dumps(data_goal))

    elif 'music' in message:

        add_client_to_type('music', client)

def ping_clients():

    while True:

        for connection_type, clients in connections_by_type.items():
            for client_id, client_info in clients.items():
                client_handler = client_info["handler"]
                try:
                    client_handler.send_message('ping')
                    last_pong_times[client_id] = time.time()
                except Exception as e:
                    utils.error_log(e)

        time.sleep(5)

def check_pong():
    while True:

        current_time = time.time()
        
        for client_id, last_pong_time in list(last_pong_times.items()):
            if current_time - last_pong_time > 5:
                for connection_type, clients in connections_by_type.items():
                    if client_id in clients:
                        try:
                            del clients[client_id]
                        except KeyError:
                            pass
                try:
                    del last_pong_times[client_id]
                except KeyError:
                    pass
        time.sleep(1)

def start_server(host, port):

    threading.Thread(target=ping_clients).start()
    threading.Thread(target=check_pong).start()

    server = WebsocketServer(port=port, host=host)
    server.set_fn_new_client(on_client_connected)
    server.set_fn_message_received(message_received)
    server.set_fn_client_left(on_client_disconnected)

    server.run_forever()

