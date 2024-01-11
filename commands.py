import json
import utils
from database import DatabaseManager



class CommandDatabaseManager:

    def __init__(self):

        database_manager = DatabaseManager()
        self.connection_pool = database_manager.connection_pool_commands
        self.is_connected = database_manager.is_connected_commands
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):

        try:

            cursor = self.connection_pool.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commands (
                    command TEXT PRIMARY KEY,
                    status INTEGER,
                    delay INTEGER,
                    type TEXT,
                    user_level TEXT,
                    sound TEXT,
                    volume INTEGER,
                    cost REAL,
                    cost_status INTEGER,
                    response TEXT,
                    keys TEXT,
                    keys_status INTEGER,
                    time_key INTEGER,
                    last_use INTEGER
                )
            ''')
            self.connection_pool.commit()

            cursor.close()

        except Exception as e:

            utils.error_log(e)

    def execute_query(self, query, params=None):

        try:
            
            cursor = self.connection_pool.cursor()

            if params:

                cursor.execute(query, params)
                
            else:

                cursor.execute(query)

            self.connection_pool.commit()

            return cursor
        
        except Exception as e:
            utils.error_log(e)
            return None

    def command_exists(self, command):
        
        try:
            query = '''
                SELECT COUNT(*) FROM commands WHERE command=?
            '''
            result = self.execute_query(query, (command,)).fetchone()
            return result[0] > 0

        except Exception as e:
            utils.error_log(e)
            return False
        
    def import_commands_from_json(self, json_data):

        try:
            self.create_table_if_not_exists()

            for command, data in json_data.items():

                if not self.command_exists(command):
                    
                    user_level = ",".join(data["user_level"])
                    user_level_replace = user_level.replace(" ", "")

                    keys = ",".join(data.get("keys", ""))

                    response = data.get("response", None)
                    command_type = data.get("type", "")
                    delay = int(data.get("delay", 0))
                    user_level = user_level_replace
                    sound = data.get("sound", "")
                    volume = int(data.get("volume", 0))
                    cost = float(data.get("cost", 0.0))
                    cost_status = int(data.get("cost_status", 0))
                    keys_status = int(data.get("keys_status", 0))
                    time_key = int(data.get("time_key", 0))

                    query = '''
                        INSERT INTO commands (
                            command, status, delay, type, user_level, sound, volume, cost, cost_status, response, keys, keys_status, time_key, last_use
                        ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    '''

                    self.execute_query(query, (command, delay, command_type, user_level, sound, volume, cost, cost_status, response, keys, keys_status, time_key))

            return True
        
        except Exception as e:
            utils.error_log(e)
            return False
        
    def create_command(self, data):

        try:

            user_level = ",".join(data["user_level"])
            user_level_replace = user_level.replace(" ", "")

            keys = ",".join(data["keys"])

            command = data["command"].lower().strip()
            response = data["response"]
            command_type = data["type"]
            delay = int(data["delay"])
            user_level = user_level_replace
            sound = data["sound"]
            volume = int(data["volume"])
            cost = float(data["cost"])
            cost_status = int(data["cost_status"])
            keys_status = int(data["keys_status"])
            time_key = int(data["time_key"])

            if response == "" or response == "null":
                response = None

            query = '''
                INSERT INTO commands (
                    command, status, delay, type, user_level, sound, volume, cost, cost_status, response, keys, keys_status, time_key, last_use
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            self.execute_query(query, (command, 1, delay, command_type, user_level, sound, volume, cost, cost_status, response, keys, keys_status, time_key, 0))

            return True
        
        except Exception as e:

            utils.error_log(e)
            
            return False

    def edit_command(self, data):

        try:

            user_level = ",".join(data["user_level"])
            user_level_replace = user_level.replace(" ", "")

            keys = ",".join(data["keys"])
        
            command = data["command"]
            response = data["response"]
            new_command = data["new_command"]
            status = data["status_command"]
            delay = data["delay"]
            sound = data["sound"]
            volume = data["volume"]
            user_level = user_level_replace
            cost = data["cost"]
            cost_status = data["cost_status"]
            keys_status = data["keys_status"]
            time_key = data["time_key"]
            command_type = data["type"]

            if cost == "":
                cost = 100
                cost_status = 0

            if response == "" or response == "null":
                response = None

            query = '''
                UPDATE commands
                SET command=?, status=?, delay=?, type=?, user_level=?, sound=?, volume=?, cost=?, cost_status=?, response=?, keys=?, keys_status=?, time_key=?, last_use=0
                WHERE command=?
            '''

            self.execute_query(query, (new_command, status, delay, command_type, user_level, sound, volume, cost, cost_status, response, keys, keys_status, time_key, command))
            
            return True
        
        except Exception as e:

            utils.error_log(e)
            
            return False

    def update_delay(self, command, new_delay):

        try:
            query = '''
                UPDATE commands
                SET last_use=?
                WHERE command=?
            '''
            self.execute_query(query, (new_delay, command))

            return True
        
        except Exception as e:
            utils.error_log(e)
            
            return False
    
    def delete_command(self, command):

        try:
            query = '''
                DELETE FROM commands WHERE command=?
            '''
            self.execute_query(query, (command,))

            return True

        except Exception as e:

            utils.error_log(e)
            
            return False

    def get_command_info(self, command):

        try:
            query = '''
                SELECT * FROM commands WHERE command=?
            '''
            result = self.execute_query(query, (command,)).fetchone()

            if result:

                level = result[4].split(",")
                keys = result[10].split(",")

                data = {
                    "status": result[1],
                    "edit_type": result[3],
                    "edit_command": result[0],
                    "edit_level": level,
                    "edit_delay": result[2],
                    "edit_cost": result[7],
                    "edit_cost_status": result[8],
                    "edit_sound": result[5],
                    "edit_volume": result[6],
                    "edit_response": result[9],
                    "edit_keys": keys,
                    "edit_keys_status": result[11],
                    "edit_time_key": result[12]
                }

                data_dump = json.dumps(data, ensure_ascii=False)

                return data_dump

        except Exception as e:

            utils.error_log(e)

    def get_command(self, command):

        try:
            query = '''
                SELECT * FROM commands WHERE command=?
            '''
            result = self.execute_query(query, (command,)).fetchone()

            if result:

                level = result[4].split(",")
                keys = result[10].split(",")

                data = {
                    "status": result[1],
                    "type": result[3],
                    "command": result[0],
                    "user_level": level,
                    "delay": result[2],
                    "cost": result[7],
                    "cost_status": result[8],
                    "sound": result[5],
                    "volume": result[6],
                    "response": result[9],
                    "keys": keys,
                    "keys_status": result[11],
                    "time_key": result[12],
                    "last_use": result[13]
                }

                data_dump = json.dumps(data, ensure_ascii=False)

                return data_dump

        except Exception as e:
            
            utils.error_log(e)

    def get_command_list(self):
        try:
            query = '''
                SELECT command FROM commands
            '''

            result = self.execute_query(query).fetchall()
            command_list = [item[0] for item in result]

            return json.dumps(command_list, ensure_ascii=False)
        
        except Exception as e:
            utils.error_log(e)

    def get_all_command_data(self):

        try:
            query = '''
                SELECT * FROM commands
            '''

            result = self.execute_query(query).fetchall()

            columns = ["command", "status", "delay", "type", "user_level", "sound", "volume", "cost", "cost_status", "response", "keys", "keys_status", "time_key", "last_use"]

            command_data = [dict(zip(columns, row)) for row in result]

            for command in command_data:
                command["user_level"] = command["user_level"].split(",") if command["user_level"] else []

            return command_data
        
        except Exception as e:
            utils.error_log(e)