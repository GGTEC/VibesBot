import sqlite3

from datetime import datetime
import json
import utils

error_list = [
    "cannot start a transaction within a transaction",
    "no more rows available",
    "another row available",
    "cannot commit - no transaction is active",
    "error return without exception set",
    "not an error",
    " <method 'commit' of 'sqlite3.Connection' objects> returned NULL without setting an exception"
]

class DatabaseManager:

    def __init__(self):

        self.users_database_path = f"{utils.local_work('appdata_path')}/database/users_database.db"
        self.events_database_path = f"{utils.local_work('appdata_path')}/database/events_database.db"
        self.commands_path = f"{utils.local_work('appdata_path')}/database/commands_database.db"
        self.chat_path = f"{utils.local_work('appdata_path')}/database/chat_database.db"
        self.gift_path = f"{utils.local_work('appdata_path')}/database/gifts_database.db"
        self.responses_path = f"{utils.local_work('appdata_path')}/database/responses_database.db"
        self.goal_path = f"{utils.local_work('appdata_path')}/database/goal_database.db"

        self.connection_pool_users = None
        self.connection_users = None
        
        self.connection_pool_events =  None
        self.connection_events = None

        self.connection_pool_commands = None
        self.connection_commands = None

        self.connection_pool_chat = None
        self.connection_chat = None

        self.connection_pool_gift = None
        self.connection_gift = None

        self.connection_pool_responses = None
        self.connection_responses = None

        self.connection_pool_goal = None
        self.connection_goal = None

        self.connect()

    def connect(self):

        try:

            self.connection_pool_users = sqlite3.connect(self.users_database_path, check_same_thread=False, timeout=5)
            self.connection_users = True

            self.connection_pool_events = sqlite3.connect(self.events_database_path, check_same_thread=False, timeout=5)
            self.connection_events = True

            self.connection_pool_commands = sqlite3.connect(self.commands_path, check_same_thread=False, timeout=5)
            self.connection_commands = True

            self.connection_pool_chat = sqlite3.connect(self.chat_path, check_same_thread=False, timeout=5)
            self.connection_chat = True

            self.connection_pool_gift = sqlite3.connect(self.gift_path, check_same_thread=False, timeout=5)
            self.connection_gift = True

            self.connection_pool_responses = sqlite3.connect(self.responses_path, check_same_thread=False, timeout=5)
            self.connection_responses = True

            self.connection_pool_goal = sqlite3.connect(self.goal_path, check_same_thread=False, timeout=5)
            self.connection_goal = True

        except Exception as e:
            utils.error_log(e)

    def close(self):

        try:

            if self.connection_users:
                self.connection_pool_users.close()
            else:
                utils.error_log("Erro: Banco de dados não conectado.")

            if self.connection_events:
                self.connection_pool_events.close()
            else:
                utils.error_log("Erro: Banco de dados não conectado.")
            
            if self.connection_commands:
                self.connection_pool_commands.close()
            else:
                utils.error_log("Erro: Banco de dados não conectado.")

            if self.connection_chat:
                self.connection_pool_chat.close()
            else:
                utils.error_log("Erro: Banco de dados não conectado.")

            if self.connection_gift:
                self.connection_pool_gift.close()
            else:
                utils.error_log("Erro: Banco de dados não conectado.")

            if self.connection_responses:
                self.connection_pool_responses.close()
            else:
                utils.error_log("Erro: Banco de dados não conectado.")


        except Exception as e:
            utils.error_log(e)


db_manager = DatabaseManager()


class ChatLogManager:

    def __init__(self):

        self.connection_pool = db_manager.connection_pool_chat
        self.is_connected = db_manager.connection_chat

    def _check_connection(self):

        if not self.is_connected:
            
            utils.error_log("Erro: Conexão com o banco de dados não estabelecida.")
            return False
        
        return True
    
    def create_table_if_not_exists(self):

        try:

            if not self._check_connection():
                return

            date = datetime.now().strftime("%d_%m_%Y")

            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS "{date}" (
                    timestamp TEXT,
                    type_id TEXT,
                    userid INTEGER,
                    username TEXT,
                    display_name TEXT,
                    message TEXT,
                    badges TEXT,
                    follow INTEGER,
                    moderator INTEGER,
                    subscriber INTEGER,
                    top_gifter TEXT,
                    profile_pic TEXT,
                    font_size TEXT,
                    chat_color_border INTEGER,
                    chat_color_name INTEGER,
                    chat_name_select TEXT,
                    chat_border_select TEXT,
                    show_user_picture INTEGER,
                    chat_animation TEXT,
                    wrapp_message INTEGER,
                    data_show INTEGER,
                    chat_time TEXT,
                    type_data TEXT
                )
            ''')

            self.connection_pool.commit()

            cursor.close()

        except Exception as e:

            utils.error_log(e)

    def add_chat(self, date, chat_data):

        try:  

            if not self._check_connection():
                return
            
            self.create_table_if_not_exists()

            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                INSERT INTO "{date}" (
                    timestamp,
                    type_id,
                    userid,
                    username,
                    display_name,
                    message,
                    badges,
                    follow,
                    moderator,
                    subscriber,
                    top_gifter,
                    profile_pic,
                    font_size,
                    chat_color_border,
                    chat_color_name,
                    chat_name_select,
                    chat_border_select,
                    show_user_picture,
                    chat_animation,
                    wrapp_message,
                    data_show,
                    chat_time,
                    type_data
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(datetime.now()),
                chat_data['type_id'],
                chat_data['userid'],
                chat_data['username'],
                chat_data['display_name'],
                chat_data['message'],
                str(chat_data['badges']),
                int(chat_data['follow']),
                int(chat_data['moderator']),
                int(chat_data['subscriber']),
                chat_data['top_gifter'],
                chat_data['profile_pic'],
                chat_data['font_size'],
                int(chat_data['chat_color_border']),
                int(chat_data['chat_color_name']),
                chat_data['chat_name_select'],
                chat_data['chat_border_select'],
                int(chat_data['show_user_picture']),
                chat_data['chat_animation'],
                int(chat_data['wrapp_message']),
                int(chat_data['data_show']),
                chat_data['chat_time'],
                chat_data['type_data']
            ))

            self.connection_pool.commit()

            cursor.close()

            return True

        except Exception as e:

            utils.error_log(e)
            return False

    def get_messages(self, date, limit):

        try:
            if not self._check_connection():
                return
            
            cursor = self.connection_pool.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (date,))
            table_exists = cursor.fetchone()

            if not table_exists:
                self.create_table_if_not_exists()
                return []
            
            query = f'''
                SELECT * FROM "{date}"
                ORDER BY timestamp DESC
                LIMIT ?
            '''

            cursor.execute(query, (limit,))

            result = cursor.fetchall()

            cursor.close()

            columns = [
                "timestamp",
                "type_id",
                "userid",
                "username",
                "display_name",
                "message",
                "badges",
                "follow",
                "moderator",
                "subscriber",
                "top_gifter",
                "profile_pic",
                "font_size",
                "chat_color_border",
                "chat_color_name",
                "chat_name_select",
                "chat_border_select",
                "show_user_picture",
                "chat_animation",
                "wrapp_message",
                "data_show",
                "chat_time",
                "type_data"
            ]

            recent_events = [dict(zip(columns, row)) for row in result]

            return recent_events

        except Exception as e:

            utils.error_log(e)
            return []
        
    def remove_old_tables(self, max_age_days):

        try:

            if not self._check_connection():
                return
    
            cursor = self.connection_pool.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            tables_exclude = ['gifts', 
                'gifts_global',
                'users', 
                'event_log',
                'logs', 
                'commands',
                'giveaway', 
                'player', 
                'queue', 
                'tts', 
                'balance', 
                'champ', 
                'votes', 
                'subathon',
                'responses'
                ] 
            
            current_date = datetime.now()

            for table in tables:

                if table[0] not in tables_exclude:
                        
                    table_name = table[0]

                    table_date = datetime.strptime(table_name, "%d_%m_%Y")

                    if (current_date - table_date).days > max_age_days:

                        cursor.execute(f"DROP TABLE IF EXISTS [{table_name}];")

            self.connection_pool.commit()
            cursor.close()

            return True
        
        except Exception as e:

            utils.error_log(e)
            return False
        
    def get_message(self, date, index=0):


        try:

            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                SELECT * FROM "{date}"
                ORDER BY timestamp DESC
                LIMIT 1 OFFSET {index}
            ''')

            result = cursor.fetchone()

            cursor.close()

            if result:
                columns = [
                    "timestamp",
                    "type_id",
                    "userid",
                    "username",
                    "display_name",
                    "message",
                    "badges",
                    "follow",
                    "moderator",
                    "subscriber",
                    "top_gifter",
                    "profile_pic",
                    "font_size",
                    "chat_color_border",
                    "chat_color_name",
                    "chat_name_select",
                    "chat_border_select",
                    "show_user_picture",
                    "chat_animation",
                    "wrapp_message",
                    "data_show",
                    "chat_time",
                    "type_data"
                ]
                return dict(zip(columns, result))
            else:
                return None

        except Exception as e:

            utils.error_log(e)
            return None


class CommandDatabaseManager:

    def __init__(self):

        self.connection_pool = db_manager.connection_pool_commands
        self.is_connected = db_manager.connection_commands

    def _check_connection(self):

        if not self.is_connected:
            
            utils.error_log("Erro: Conexão com o banco de dados não estabelecida.")
            return False
        
        return True
        
    def execute_query(self, query, params=None):

        try:
            
            if not self._check_connection():
                return
            
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

    def default_command_exists(self, command_table, command_type):

        try:

            if not self._check_connection():
                return
            

            query = f'''
                SELECT COUNT(*) FROM {command_table} WHERE command_type=?
            '''
            result = self.execute_query(query, (command_type,)).fetchone()

            return result[0] > 0

        except Exception as e:
            utils.error_log(e)
            return False
      
    def get_default_command_info(self, command_type_table):

        try:

            if not self._check_connection():
                return
            
            query = f'''
                SELECT * FROM {command_type_table}
            '''

            results = self.execute_query(query).fetchall()

            default_commands = {}

            for result in results:

                level = result[5].split(",") if result[5] else []
                whitelist = result[9].split(",") if result[9] else []
                blacklist = result[10].split(",") if result[10] else []

                data = {
                    "command": result[1],
                    "status": result[2],
                    "delay": result[3],
                    "last_use": result[4],
                    "user_level": level,
                    "cost": result[6],
                    "cost_status": result[7],
                    "whitelist_status": result[8],
                    "whitelist": whitelist,
                    "blacklist": blacklist
                }

                command_type = result[0]

                if command_type not in default_commands:
                    default_commands[command_type] = data

            return default_commands

        except Exception as e:
            utils.error_log(e)
            return False
    
    def get_default_command(self, command_type, command_type_table):

        try:

            if not self._check_connection():
                return
            

            query = f'''
                SELECT * FROM {command_type_table} WHERE command_type=?
            '''

            result = self.execute_query(query, (command_type,)).fetchone()

            if result:

                level = result[5].split(",")

                if result[9] != None:
                    whitelist = result[9].split(",")
                else:
                    whitelist = ""

                if result[10] != None:
                    blacklist = result[10].split(",")
                else:
                    blacklist = ""
                

                data = {
                    "command": result[1],
                    "status": result[2],
                    "delay": result[3],
                    "user_level": level,
                    "cost": result[6],
                    "cost_status": result[7],
                    "whitelist_status" : result[8],
                    "whitelist" : whitelist,
                    "blacklist" : blacklist
                }

                return data
                
            return result

        except Exception as e:

            utils.error_log(e)
            return False
    
    def save_default_command(self, data, command_type_table):
        
        try:

            if not self._check_connection():
                return
            

            user_level = ",".join(data["user_level"])
            user_level_replace = user_level.replace(" ", "")

            if type(data["cost"]) == "string":
                cost = 0
            else:
                cost = data["cost"]

            command = data["command"].lower().strip()
            command_type = data["type_command"]
            status =  data["status"]
            delay = int(data["delay"])
            user_level = user_level_replace
            cost_status = int(data["cost_status"])
            whitelist_status = int(data["whitelist_status"])

            if self.default_command_exists(command_type_table, command_type):

                query = f'''
                    UPDATE {command_type_table}
                    SET command=?, status=?, delay=?, user_level=?, cost=?, cost_status=?, whitelist_status=?
                    WHERE command_type=?
                '''

                self.execute_query(query, (command, status, delay, user_level, cost, cost_status, whitelist_status, command_type))
                
                return True
            
            else:

                return False

        except Exception as e:
            utils.error_log(e)
            return False    
    
    def update_last_use(self, current, command_type, command_type_table):

        try:

            if not self._check_connection():
                return
            

            query = f'''
                UPDATE {command_type_table} SET last_use=?
                WHERE command_type = ?
            '''

            self.execute_query(query, (current ,command_type))

        except Exception as e:
            utils.error_log(e)
            return False

    def command_exists(self, command):
        
        try:

            if not self._check_connection():
                return
            
            query = '''
                SELECT COUNT(*) FROM commands WHERE command=?
            '''
            result = self.execute_query(query, (command,)).fetchone()
            return result[0] > 0

        except Exception as e:
            utils.error_log(e)
            return False
           
    def create_command(self, data):

        try:

            if not self._check_connection():
                return
            
            user_level = ",".join(data["user_level"])
            user_level_replace = user_level.replace(" ", "")

            keys = ",".join(data["keys"])

            command = data["command"].lower().strip()
            response = data["response"]
            command_type = data["type"]
            delay = int(data["delay"])
            user_level = user_level_replace
            sound = data["sound"]
            video = data["video"]
            video_time = data["video_time"]
            volume = int(data["volume"])
            cost = float(data["cost"])
            cost_status = int(data["cost_status"])
            keys_status = int(data["keys_status"])
            time_key = int(data["time_key"])
            whitelist_status = int(data["whitelist_status"])

            if response == "" or response == "null":
                response = None

            query = '''
                INSERT INTO commands (
                    command, status, delay, type, user_level, sound, volume, cost, cost_status, response, keys, keys_status, time_key, last_use, video, video_time, whitelist_status, whitelist, blacklist
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            self.execute_query(query, (command, 1, delay, command_type, user_level, sound, volume, cost, cost_status, response, keys, keys_status, time_key, 0, video, video_time, whitelist_status, "", ""))

            return True
        
        except Exception as e:

            utils.error_log(e)
            
            return False

    def edit_command(self, data):

        try:

            if not self._check_connection():
                return

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
            video = data["video"]
            video_time = data["video_time"]
            user_level = user_level_replace
            cost = data["cost"]
            cost_status = data["cost_status"]
            keys_status = data["keys_status"]
            time_key = data["time_key"]
            command_type = data["type"]
            whitelist_status = data["whitelist_status"]

            if cost == "":
                cost = 100
                cost_status = 0

            if response == "" or response == "null":
                response = None

            query = '''
                UPDATE commands
                SET command=?, status=?, delay=?, type=?, user_level=?, sound=?, volume=?, cost=?, cost_status=?, response=?, keys=?, keys_status=?, time_key=?, last_use=0, video=?, video_time=?, whitelist_status=?
                WHERE command=?
            '''

            self.execute_query(query, (new_command, status, delay, command_type, user_level, sound, volume, cost, cost_status, response, keys, keys_status, time_key, video, video_time, whitelist_status, command))
            
            return True
        
        except Exception as e:

            utils.error_log(e)
            
            return False

    def update_delay(self, command, new_delay):

        try:

            if not self._check_connection():
                return
    
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
            if not self._check_connection():
                return
    
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

            if not self._check_connection():
                return
    
            query = '''
                SELECT * FROM commands WHERE command=?
            '''
            result = self.execute_query(query, (command,)).fetchone()

            if result:

                level = result[4].split(",")
                keys = result[10].split(",")

                if result[18] != None:
                    blacklist = result[18].split(",")
                else:
                    blacklist = ""
                    
                if result[17] != None:
                    whitelist = result[17].split(",")
                else:
                    whitelist = ""

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
                    "edit_time_key": result[12],
                    "edit_video" : result[14],
                    "edit_video_time" : result[15],
                    "edit_whitelist_status" : result[16]
                }

                data_dump = json.dumps(data, ensure_ascii=False)

                return data_dump

        except Exception as e:

            utils.error_log(e)

    def get_command(self, command):

        try:

            if not self._check_connection():
                return
            
            result = self.execute_query(''' SELECT * FROM commands WHERE command=?''', (command,)).fetchone()

            if result:

                level = result[4].split(",")
                keys = result[10].split(",")

                if result[18] != None:
                    blacklist = result[18].split(",")
                else:
                    blacklist = ""
                    
                if result[17] != None:
                    whitelist = result[17].split(",")
                else:
                    whitelist = ""
                    

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
                    "last_use": result[13],
                    "video" : result[14],
                    "video_time" : result[15],
                    "whitelist_status" : result[16],
                    "whitelist" : blacklist,
                    "blacklist" : whitelist
                }

                data_dump = json.dumps(data, ensure_ascii=False)

                return data_dump

        except Exception as e:
            
            utils.error_log(e)

    def get_command_list(self):

        try:

            if not self._check_connection():
                return
    
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
            if not self._check_connection():
                return
    
            query = '''
                SELECT * FROM commands
            '''

            result = self.execute_query(query).fetchall()

            columns = ["command", "status", "delay", "type", "user_level", "sound", "volume", "cost", "cost_status", "response", "keys", "keys_status", "time_key", "last_use","video","video_time", "whitelist_status", "whitelist", "blacklist"]

            command_data = [dict(zip(columns, row)) for row in result]

            for command in command_data:
                command["user_level"] = command["user_level"].split(",") if command["user_level"] else []

            return command_data
        
        except Exception as e:
            utils.error_log(e)

    def add_to_blacklist(self, command, user_id):

        try:

            if not self._check_connection():
                return
            
            query = '''
                UPDATE commands
                SET blacklist = COALESCE(blacklist, '') || ? || ','
                WHERE command = ?
            '''

            self.execute_query(query, (user_id, command))

            return True
        
        except Exception as e:

            utils.error_log(e)
            return False

    def add_to_whitelist(self, command, user_id):

        try:
            if not self._check_connection():
                return
    
            query = '''
                UPDATE commands
                SET whitelist = COALESCE(whitelist, '') || ? || ','
                WHERE command = ?
            '''
            self.execute_query(query, (user_id, command))
            return True
        except Exception as e:
            utils.error_log(e)
            return False

    def remove_from_blacklist(self, command, user_id):

        try:

            if not self._check_connection():
                return
            
            current_blacklist = self.get_blacklist(command)

            if current_blacklist:

                blacklist_list = current_blacklist.split(',')

                if user_id in blacklist_list:

                    blacklist_list.remove(user_id)

                    updated_blacklist = ','.join(blacklist_list)

                    query = '''
                        UPDATE commands
                        SET blacklist = ?
                        WHERE command = ?
                    '''

                    self.execute_query(query, (updated_blacklist, command))

                    return True
                
            return False
        
        except Exception as e:

            utils.error_log(e)
            return False

    def remove_from_whitelist(self, command, user_id):

        try:

            if not self._check_connection():
                return
            
            current_whitelist = self.get_whitelist(command)

            if current_whitelist:

                whitelist_list = current_whitelist.split(',')

                if user_id in whitelist_list:

                    whitelist_list.remove(user_id)

                    updated_whitelist = ','.join(whitelist_list)

                    query = '''
                        UPDATE commands
                        SET whitelist = ?
                        WHERE command = ?
                    '''

                    self.execute_query(query, (updated_whitelist, command))

                    return True
                
            return False
        
        except Exception as e:

            utils.error_log(e)

            return False

    def get_blacklist(self, command):
        
        try:
            if not self._check_connection():
                return
            query = '''
                SELECT blacklist FROM commands WHERE command=?
            '''
            result = self.execute_query(query, (command,)).fetchone()

            return result[0] if result else None
        
        except Exception as e:
            utils.error_log(e)
            return None

    def get_whitelist(self, command):
        
        try:
            if not self._check_connection():
                return
            query = '''
                SELECT whitelist FROM commands WHERE command=?
            '''

            result = self.execute_query(query, (command,)).fetchone()
            return result[0] if result else None
        
        except Exception as e:
            utils.error_log(e)
            return None

    def add_to_blacklistDefault(self, command_table, command_type, user_id):

        try:
            if not self._check_connection():
                return
            query = f'''
                UPDATE {command_table}
                SET blacklist = COALESCE(blacklist, '') || ? || ','
                WHERE command_type = ?
            '''

            self.execute_query(query, (user_id, command_type))

            return True
        
        except Exception as e:

            utils.error_log(e)
            return False

    def add_to_whitelistDefault(self, command_table, command_type, user_id):
        
        try:

            if not self._check_connection():
                return
            
            query = f'''
                UPDATE {command_table}
                SET whitelist = COALESCE(whitelist, '') || ? || ','
                WHERE command_type = ?
            '''
            self.execute_query(query, (user_id, command_type))
            return True
        except Exception as e:
            utils.error_log(e)
            return False

    def remove_from_blacklistDefault(self, command_table, command_type, user_id):

        try:

            if not self._check_connection():
                return
            
            current_blacklist = self.get_blacklistDefault(command_table, command_type)

            if current_blacklist:

                blacklist_list = current_blacklist.split(',')

                if user_id in blacklist_list:

                    blacklist_list.remove(user_id)

                    updated_blacklist = ','.join(blacklist_list)

                    query = f'''
                        UPDATE {command_table}
                        SET blacklist = ?
                        WHERE command_type = ?
                    '''

                    self.execute_query(query, (updated_blacklist, command_type))

                    return True
                
            return False
        
        except Exception as e:

            utils.error_log(e)
            return False

    def remove_from_whitelistDefault(self, command_table, command_type, user_id):

        try:

            if not self._check_connection():
                return
            
            current_whitelist = self.get_whitelistDefault(command_table, command_type)

            if current_whitelist:

                whitelist_list = current_whitelist.split(',')

                if user_id in whitelist_list:

                    whitelist_list.remove(user_id)

                    updated_whitelist = ','.join(whitelist_list)

                    query = f'''
                        UPDATE {command_table}
                        SET whitelist = ?
                        WHERE command_type = ?
                    '''

                    self.execute_query(query, (updated_whitelist, command_type))

                    return True
                
            return False
        
        except Exception as e:

            utils.error_log(e)

            return False

    def get_blacklistDefault(self, command_table, command_type):
        
        try:

            if not self._check_connection():
                return
            
            query = f'''
                SELECT blacklist FROM {command_table} WHERE command_type=?
            '''
            result = self.execute_query(query, (command_type,)).fetchone()

            return result[0] if result else None
        
        except Exception as e:
            utils.error_log(e)
            return None

    def get_whitelistDefault(self,command_table, command_type):

        try:

            if not self._check_connection():
                return
            
            query = f'''
                SELECT whitelist FROM {command_table} WHERE command_type=?
            '''

            result = self.execute_query(query, (command_type,)).fetchone()
            return result[0] if result else None
            
        
        except Exception as e:
            utils.error_log(e)
            return None


class EventLogManager:

    def __init__(self):

        self.connection_pool = db_manager.connection_pool_events
        self.is_connected = db_manager.connection_events

    def _check_connection(self):

        if not self.is_connected:
            
            utils.error_log("Erro: Conexão com o banco de dados não estabelecida.")
            return False
        
        return True
    
    def add_event(self, event_data):

        try:

            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                INSERT INTO event_log (timestamp, type, message, user_input)
                VALUES (?, ?, ?, ?)
            ''', (str(datetime.now()), event_data['type'], event_data['message'], event_data['user_input']))
            
            self.connection_pool.commit()

            cursor.close()
            
            return True
        
        except Exception as e:

            self.connection_pool.rollback()

            if f"{e}" not in error_list:
                utils.error_log(e)

            return False

    def get_recent_events(self, limit=100):

        try:

            if not self._check_connection():
                return
            
            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                SELECT * FROM event_log
                ORDER BY timestamp DESC
                LIMIT {limit}
            ''')

            result = cursor.fetchall()

            cursor.close()

            columns = ["timestamp", "type", "message", "user_input"]

            recent_events = [dict(zip(columns, row)) for row in result]

            return recent_events
        
        except Exception as e:

            utils.error_log(e)

            return []
        
    def clean_up_events(self, max_items=1000):

        try:

            if not self._check_connection():
                return
            
            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                DELETE FROM event_log
                WHERE ROWID NOT IN (
                    SELECT ROWID FROM event_log
                    ORDER BY timestamp DESC
                    LIMIT {max_items}
                )
            ''')

            self.connection_pool.commit()

            cursor.close()

            return True
        
        except Exception as e:
            utils.error_log(e)
            return False


class GiftsManager:

    def __init__(self):

        self.connection_pool = db_manager.connection_pool_gift
        self.is_connected = db_manager.connection_gift

    def _check_connection(self):

        if not self.is_connected:
            
            utils.error_log("Erro: Conexão com o banco de dados não estabelecida.")
            return False
        
        return True
    
    def create_table_if_not_exists(self):

        try:
            if not self._check_connection():
                return
            
            cursor = self.connection_pool.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gifts (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    name_br TEXT,
                    value INTEGER,
                    icons TEXT,
                    audio TEXT,
                    status INTEGER,
                    volume INTEGER,
                    points_global INTEGER,
                    points INTEGER,
                    time TEXT,
                    keys TEXT,
                    key_status INTEGER,
                    key_time INTEGER,
                    status_subathon INTEGER,
                    video_status INTEGER,
                    video TEXT,
                    video_time INTEGER
                )
            ''')

            self.connection_pool.commit()
            cursor.close()

        except Exception as e:
            
            utils.error_log(e)

    def create_table_if_not_exists_global(self):

        try:
            if not self._check_connection():
                return
            
            cursor = self.connection_pool.cursor()

            cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="gifts_global";')
            table_exists = cursor.fetchone()

            if not table_exists:

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS gifts_global (
                        id INTEGER PRIMARY KEY,
                        audio TEXT,
                        status INTEGER,
                        volume INTEGER,
                        video_status INTEGER,
                        video TEXT,
                        video_time INTEGER
                    )
                ''')

                self.connection_pool.commit()

                cursor.execute('SELECT COUNT(*) FROM gifts_global;')
                table_empty = cursor.fetchone()[0]

                if table_empty == 0:

                    cursor.execute('''
                        INSERT INTO gifts_global (
                            id,
                            video_status,
                            video_time,
                            video, 
                            status,
                            audio,
                            volume
                        )      
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                                
                    ''', (1, 0, 0, "", 0, "", 0))

                    self.connection_pool.commit()

                    cursor.close()

        except Exception as e:
            
            utils.error_log(e)

    def tiktok_gift(self, data_receive):

        try:
            if not self._check_connection():
                return
            
            ttk_data_gifts = json.loads(data_receive)

            type_id = ttk_data_gifts["type_id"]

            if type_id == "get":
                return self.get_all_gift_data()
            if type_id == "get_global":
                return self.get_global_gift()
            elif type_id == "save_sound_gift":
                return self.save_sound_gift(ttk_data_gifts)
            elif type_id == "save_point_gift":
                return self.save_point_gift(ttk_data_gifts)
            elif type_id == "get_gift_info":
                return self.get_gift_info(ttk_data_gifts)
            elif type_id == "global_gift_save":
                return self.save_global_gift(ttk_data_gifts)
            else:
                return None

        except Exception as e:

            
            utils.error_log(e)
            return None

    def add_gift(self, data):

        try:
            if not self._check_connection():
                return
            
            self.create_table_if_not_exists()

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                           
                INSERT INTO gifts (
                    id,
                    name,
                    name_br,
                    value,
                    icons,
                    audio,
                    status,
                    volume,
                    points_global,
                    points,
                    time,
                    keys,
                    key_status,
                    key_time,
                    status_subathon,
                    video_status,
                    video,
                    video_time
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['id'],
                data['name'],
                data['name_br'],
                data['value'],
                ','.join(data['icon']),
                data['audio'],
                data['status'],
                data['volume'],
                data['points-global'],
                data['points'],
                data['time'],
                ','.join(data['keys']),
                data['key_status'],
                data['key_time'],
                data['status_subathon'],
                data['video_status'],
                data['video'],
                data['video_time']
            ))

            self.connection_pool.commit()
            cursor.close()

            return True
        except Exception as e:

            
            utils.error_log(e)
            
            return False

    def get_gift_data(self, id):

        try:
            if not self._check_connection():
                return
            
            cursor = self.connection_pool.cursor()

            cursor.execute('''
                SELECT * FROM gifts WHERE id = ?
            ''', (id,))

            result = cursor.fetchone()

            cursor.close()

            if result:

                icons = result[4].split(',')
                keys = result[11].split(',')

                gift_data = {
                    "name": result[1],
                    "name_br": result[2],
                    "value": result[3],
                    "icons": icons,
                    "audio": result[5],
                    "status": result[6],
                    "volume": result[7],
                    "points_global": result[8],
                    "points": result[9],
                    "time": result[10],
                    "keys": keys,
                    "key_status": result[12],
                    "key_time": result[13],
                    "status_subathon": result[14],
                    "video_status": result[15],
                    "video": result[16],
                    "video_time": result[17]
                }

                return gift_data
            
            else:
                return None
            
        except Exception as e:

            
            utils.error_log(e)
            return None

    def get_all_gift_data(self):

        try:
            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()

            cursor.execute('SELECT * FROM gifts')

            results = cursor.fetchall()

            gifts_data = {"gifts" : {}}

            gifts_data_dict = gifts_data["gifts"]

            for result in results:

                icons = result[4].split(',')
                keys = result[11].split(',')

                gift_data = {
                    "name": result[1],
                    "name_br": result[2],
                    "value": result[3],
                    "icons": icons,
                    "audio": result[5],
                    "status": result[6],
                    "volume": result[7],
                    "points_global": result[8],
                    "points": result[9],
                    "time": result[10],
                    "keys": keys,
                    "key_status": result[12],
                    "key_time": result[13],
                    "status_subathon": result[14],
                    "video_status": result[15],
                    "video": result[16],
                    "video_time": result[17]
                }

                gifts_data_dict[result[0]] = gift_data

            cursor.close()

            return json.dumps(gifts_data, ensure_ascii=False)

        except Exception as e:
            utils.error_log(e)
            return None
        
    def save_sound_gift(self, data_receive):

        try:
            if not self._check_connection():
                return

            gift_id = data_receive["id"]
            audio_loc = data_receive["sound_loc"]
            volume = data_receive["sound_volume"]

            name_br = data_receive["name"]
            status = data_receive["status"]
            video = data_receive["video"]
            video_time = data_receive["video_time"]
            video_status = data_receive["video_status"]
            keys = data_receive["keys"]
            key_status = data_receive["key_status"]
            key_time = data_receive["key_time"]

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                UPDATE gifts
                SET audio = ?,
                    volume = ?,
                    name_br = ?,
                    status = ?,
                    video = ?,
                    video_time = ?,
                    video_status = ?,
                    keys = ?,
                    key_status = ?,
                    key_time = ?
                WHERE id = ?
            ''', (audio_loc, volume, name_br, status, video, video_time, video_status, ','.join(keys), key_status, key_time, gift_id))

            self.connection_pool.commit()
            cursor.close()

            return "success"
        
        except Exception as e:

            
            utils.error_log(e)

            return "error"

    def save_point_gift(self, data_receive):

        try:
            if not self._check_connection():
                return
            
            gift_id = data_receive["id"]
            points_global = data_receive["status"]
            points = data_receive["points"]

            cursor = self.connection_pool.cursor()
            cursor.execute('''
                UPDATE gifts
                SET points_global = ?,
                    points = ?
                WHERE id = ?
            ''', (points_global, points, gift_id))

            self.connection_pool.commit()
            cursor.close()

            return "success"
        
        except Exception as e:

            utils.error_log(e)
            return "error"

    def save_subathon_gift(self, data_receive):

        try:

            if not self._check_connection():
                return

            gift_id = data_receive["id"]
            time = data_receive['time']
            status_subathon = data_receive['status']

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                UPDATE gifts
                SET status_subathon = ?,
                    time = ?
                WHERE id = ?
            ''', (status_subathon, time, gift_id))

            self.connection_pool.commit()
            cursor.close()

            return "success"
        
        except Exception as e:

            utils.error_log(e)
            return "error"
        
    def get_gift_info(self, data_receive):

        try:
            if not self._check_connection():
                return

            gift_id = data_receive["id"]

            cursor = self.connection_pool.cursor()
            cursor.execute('SELECT * FROM gifts WHERE id = ?', (gift_id,))
            
            result = cursor.fetchone()
            cursor.close()

            if result:
                columns = [
                    "id",
                    "name",
                    "name_br",
                    "value",
                    "icons",
                    "audio",
                    "status",
                    "volume",
                    "points_global",
                    "points",
                    "time",
                    "keys",
                    "key_status",
                    "key_time",
                    "status_subathon",
                    "video_status",
                    "video",
                    "video_time"
                ]

                data = dict(zip(columns, result))

                data['icons'] = data['icons'].split(',')
                data['keys'] = data['keys'].split(',')

                return json.dumps(data, ensure_ascii=False)
            
            else:

                return None
        except Exception as e:

            
            utils.error_log(e)
            return None

    def get_global_gift(self):

        try:

            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()
            cursor.execute('SELECT * FROM gifts_global WHERE id = 1')
            
            result = cursor.fetchone()
            cursor.close()

            if result:

                columns = [
                    "id",
                    "audio",
                    "status",
                    "volume",
                    "video_status",
                    "video",
                    "video_time"
                ]

                data = dict(zip(columns, result))

                return data
            
        except Exception as e:

            utils.error_log(e)

            return "error"

    def save_global_gift(self, data_receive):

        try:
            if not self._check_connection():
                return

            video_status = data_receive["video_status"]
            video_time = data_receive["video_time"]
            video = data_receive["video"]
            status = data_receive["status"]
            audio = data_receive["sound"]
            volume = data_receive["volume"]

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                UPDATE gifts_global
                SET video_status = ?,
                    video_time = ?,
                    video = ?,
                    status = ?,
                    audio = ?,
                    volume = ?
                WHERE id = 1
            ''', (video_status, video_time, video, status, audio, volume))

            self.connection_pool.commit()
            cursor.close()

            return "success"
        
        except Exception as e:
            utils.error_log(e)

            return "error"
             
    def update_or_insert_gifts(self, data_dict):

        try:
            if not self._check_connection():
                return
            
            self.create_table_if_not_exists()
            self.create_table_if_not_exists_global()

            for id, data in data_dict.items():

                cursor = self.connection_pool.cursor()

                cursor.execute('SELECT * FROM gifts WHERE id = ?', (id,))

                existing_data = cursor.fetchone()

                if existing_data:

                    existing_data = {
                        'id': existing_data[0],
                        'name': existing_data[1],
                        'name_br': existing_data[2],
                        'value': existing_data[3],
                        'icon': existing_data[4].split(','),  # Converta a string para uma lista
                        'audio': existing_data[5],
                        'status': existing_data[6],
                        'volume': existing_data[7],
                        'points-global': existing_data[8],
                        'points': existing_data[9],
                        'time': existing_data[10],
                        'keys': existing_data[11],
                        'key_status': existing_data[12],
                        'key_time': existing_data[13],
                        'status_subathon': existing_data[14],
                        'video_status': existing_data[15],
                        'video': existing_data[16],
                        'video_time': existing_data[17]
                    }

                    if existing_data['name'] != data['name'] or existing_data['icon'] != data['icon']:
                        self.update_gifts(id, data)

                else:

                    self.add_gift({
                        'id': id,
                        'name': data['name'],    
                        'name_br' : data['name_br'],
                        'value': data['value'],
                        'icon': data['icon'], 
                        'audio': data['audio'],
                        'status': data['status'],
                        'volume': data['volume'],
                        'points-global': data['points-global'],
                        'points': data['points'],
                        'time': 0,
                        'keys': [],
                        'key_status': 0,
                        'key_time': 0,
                        'status_subathon': 0,
                        'video_status': 0,
                        'video': "",
                        'video_time': 0,
                        'video_status': 0,
                    })

            return "success"

        except Exception as e:

            
            utils.error_log(e)

            return "error"

    def update_gifts(self, id, data):

        try:
            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()
            cursor.execute('''
                UPDATE tiktok_data
                SET name = ?,
                    icons = ?,
                    audio = ?,
                    status = ?,
                    volume = ?,
                    points_global = ?,
                    points = ?,
                    time = ?,
                    keys = ?,
                    key_status = ?,
                    key_time = ?,
                    status_subathon = ?,
                    video_status = ?,
                    video = ?,
                    video_time = ?
                WHERE id = ?
            ''', (
                data['name'],
                ','.join(data['icon']),
                data['audio'],
                data['status'],
                data['volume'],
                data['points-global'],
                data['points'],
                data['time'],
                ','.join(data['keys']),
                data['key_status'],
                data['key_time'],
                data['status_subathon'],
                data['video_status'],
                data['video'],
                data['video_time'],
                id
            ))

            self.connection_pool.commit()
            cursor.close()

            return "success"

        except Exception as e:

            
            utils.error_log(e)

            return "error"

    def remove_unused_gifts(self, ids_to_keep):

        try:

            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()

            cursor.execute('SELECT id FROM gifts')
            all_ids = set(row[0] for row in cursor.fetchall())

            ids_to_remove = all_ids - set(ids_to_keep)

            for id_to_remove in ids_to_remove:
                cursor.execute('DELETE FROM gifts WHERE id = ?', (id_to_remove,))

            self.connection_pool.commit()
            cursor.close()

            return "success"

        except Exception as e:

            
            utils.error_log(e)

            return "error"


class ResponsesManager:

    def __init__(self):

        self.connection_pool = db_manager.connection_pool_responses
        self.is_connected = db_manager.connection_responses

    def _check_connection(self):

        if not self.is_connected:
            
            utils.error_log("Erro: Conexão com o banco de dados não estabelecida.")
            return False
        
        return True
    
    def import_responses(self, responses_dict):
        try:
            if not self._check_connection():
                return
            
            cursor = self.connection_pool.cursor()

            for response_name, data in responses_dict.items():

                cursor.execute('''
                    SELECT response_name FROM responses
                    WHERE response_name = ?
                ''', (response_name,))
                
                existing_response = cursor.fetchone()

                if not existing_response:
                    cursor.execute('''
                        INSERT INTO responses (response_name, status, status_s, response)
                        VALUES (?, ?, ?, ?)
                    ''', (response_name, data['status'], data['status_s'], data['response']))

            self.connection_pool.commit()
            cursor.close()

        except Exception as e:
            utils.error_log(e)

    def get_response(self, response_name):

        try:

            if not self._check_connection():
                return
            
            cursor = self.connection_pool.cursor()

            cursor.execute('''
                SELECT * FROM responses
                WHERE response_name = ?
            ''', (response_name,))

            result = cursor.fetchone()
            cursor.close()

            if result:

                columns = ["response_name", "status", "status_s", "response"]
                response_data = dict(zip(columns, result))
                return response_data
            
            else:

                return None

        except Exception as e:
            utils.error_log(e)

            return None

    def update_response(self, response_name, new_data):
       
        try:
            
            if not self._check_connection():
                return
            
            cursor = self.connection_pool.cursor()

            cursor.execute('''
                UPDATE responses
                SET status = ?, status_s = ?, response = ?
                WHERE response_name = ?
            ''', (new_data['status'], new_data['status_s'], new_data['response'], response_name))

            self.connection_pool.commit()
            cursor.close()

            return True
        
        except Exception as e:
            utils.error_log(e)


class UserDatabaseManager:

    def __init__(self):

        self.connection_pool = db_manager.connection_pool_users
        self.is_connected = db_manager.connection_users

    def connect(self):

        try:

            if not self.is_connected:
                utils.error_log("Erro: Banco de dados não conectado. 4")
                return False

            else:

                cursor = self.connection_pool.cursor()

                cursor.execute(''' SELECT * FROM users WHERE username = ? ''', ("usuarioexemplo"))

                result = cursor.fetchone()

                if not result:

                    cursor.execute('''
                        INSERT INTO users (userid, display_name, username, roles, likes, shares, gifts, points, profile_pic
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (1234567891011121314, "Usuário de testes", "usuarioexemplo", "spec", 0, 0, 0, 100000, "None"))
                    
                    self.connection_pool.commit()

                    cursor.close()

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

    def get_user_data(self, identifier):

        try:

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                SELECT * FROM users WHERE userid = ? OR display_name = ? OR username = ?
            ''', (identifier, identifier, identifier))

            result = cursor.fetchone()

            if result:

                cursor.close()

                return {
                    "userid": result[0],
                    "display_name": result[1],
                    "username": result[2],
                    "roles":  result[3].split(","),
                    "likes": result[4],
                    "shares": result[5],
                    "gifts": result[6],
                    "points": result[7],
                    "profile_pic": result[8]
                }

                
            else:

                cursor.close()

                return None

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return None

    def clear_main_database(self):

        try:
            if not self.is_connected:
                utils.error_log("Erro: Banco de dados não conectado. 6 ")
                return False

            cursor = self.connection_pool.cursor()

            cursor.execute('DELETE FROM users')

            self.connection_pool.commit()

            
            cursor.close()

            return True

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return False

    def clear_user_points(self):

        try:
            if not self.is_connected:
                utils.error_log("Erro: Banco de dados não conectado. 9")
                return False

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                UPDATE users
                SET points = 0
            ''')

            self.connection_pool.commit()
            
            cursor.close()
            
        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

    def add_user_database(self, data):

        try:

            role_mapping = ["follow", "moderator", "subscriber", "spec"]


            display_name = data["display_name"]
            username = data["username"]
            profile_pic = data["profile_pic"]
            userid = data["userid"]

            if "roles" in data:
                roles_user = list(set([role.strip() for role in data["roles"]]))
            else:
                roles_user = ["spec"]

            for role in role_mapping:
                if role in data:
                    if data[role] == True and role not in roles_user:
                        roles_user.append(role)
                    elif data[role] == False and role in roles_user:
                        roles_user.remove(role)

            result = self.get_user_data(userid)

            if result:

                role_mapping = ["follow", "moderator", "subscriber", "spec"]

                roles_user = list(set([role.strip()
                                  for role in result['roles']]))

                for role in role_mapping:
                    if role in data:
                        if data[role] == True and role not in roles_user:
                            roles_user.append(role)
                        elif data[role] == False and role in roles_user:
                            roles_user.remove(role)

                roles_string = ",".join(roles_user)
                roles_string_replace = roles_string.replace(" ", "")

                
                cursor = self.connection_pool.cursor()

                cursor.execute('''
                    UPDATE users SET
                        roles = ?,
                        username = ?,
                        display_name = ?
                    WHERE userid = ?
                ''', (roles_string_replace,
                      username,
                      display_name,
                      userid
                      ))

                self.connection_pool.commit()
                
                cursor.close()

            else:

                roles_string = ",".join(roles_user)
                roles_string_replace = roles_string.replace(" ", "")

                cursor = self.connection_pool.cursor()

                cursor.execute('''
                    INSERT INTO users (
                        userid, display_name, username, roles, likes, shares, gifts, points, profile_pic
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    userid, 
                    display_name, 
                    username, 
                    roles_string_replace,
                    data.get("likes", 0), 
                    data.get("shares", 0), 
                    data.get("gifts", 0),
                    data.get("points", 0), profile_pic
                ))

                self.connection_pool.commit()

                cursor.close()

            return True

        except Exception as e:


            if f"{e}" not in error_list:
                utils.error_log(e)

            return False

    def remove_user(self, user):

        try:

            if not self.is_connected:

                utils.error_log("Erro: Banco de dados não conectado. 8")
                return False

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                DELETE FROM users WHERE userid = ?
            ''', (user,))

            self.connection_pool.commit()

            cursor.close()

            return True
        
        except Exception as e:
            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return False
        
    def get_all_users_data(self):

        try:

            cursor = self.connection_pool.cursor()

            cursor.execute('''SELECT * FROM users''')

            results = cursor.fetchall()

            users_data = {}

            for result in results:

                roles = [element.strip() for element in result[3].split(',')]

                user_data = {
                    "userid": result[0],
                    "display_name": result[1],
                    "username": result[2],
                    "roles": roles,
                    "likes": result[4],
                    "shares": result[5],
                    "gifts": result[6],
                    "points": result[7],
                    "profile_pic": result[8]
                }

                users_data[result[0]] = user_data

            cursor.close()

            return users_data

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return None

    def get_all_users_names(self):

        try:

            cursor = self.connection_pool.cursor()

            cursor.execute('''SELECT * FROM users''')

            results = cursor.fetchall()

            users_data = {}

            for result in results:

                user_data = {
                    "userid": result[0],
                    "display_name": result[1],
                    "username": result[2]
                }

                users_data[result[0]] = user_data

            cursor.close()

            return users_data

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return None
    
    def edit_user_database(self, data):

        try:

            cursor = self.connection_pool.cursor()

            userid = data["userid"]

            cursor.execute('''
                SELECT 1 FROM users WHERE userid = ?
            ''', (userid,))

            result = cursor.fetchone()

            if result:
                # Se o usuário já existe, atualiza os valores específicos
                roles_user = data.get("roles", ['spec'])

                cursor.execute('''
                    UPDATE users SET
                        roles = ?,
                        likes = ?,
                        shares = ?,
                        gifts = ?,
                        points = ?
                    WHERE userid = ?
                ''', (
                    ",".join(roles_user),
                    data.get("likes", 0),
                    data.get("shares", 0),
                    data.get("gifts", 0),
                    data.get("points", 0),
                    userid
                ))

            self.connection_pool.commit()
            
            
            cursor.close()
            
            return True

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return False

    def check_cost(self, user, cost, status):

        try:
            if not self.is_connected:
                utils.error_log("Erro: Banco de dados não conectado. 12")
                return False

            cursor = self.connection_pool.cursor()

            cursor.execute('''SELECT points FROM users WHERE userid = ? ''', (user,))

            result = cursor.fetchone()

            if result:

                value_user = float(result[0])

                if status and value_user >= float(cost):
                    value_user -= float(cost)

                    cursor.execute('''
                        UPDATE users SET points = ? WHERE userid = ?
                    ''', (value_user, user))

                    self.connection_pool.commit()
                    
                    
                    cursor.close()

                    return True
                
                elif not status:
                    
                    cursor.close()

                    return True

        except Exception as e:
            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return False

    def give_balance(self, user, cost):

        try:

            cursor = self.connection_pool.cursor()

            cursor.execute('''SELECT points FROM users WHERE userid = ?''', (user,))

            result = cursor.fetchone()

            if result:

                value_user = float(result[0])
                value_user += float(cost)

                cursor.execute(
                    '''UPDATE users SET points = ? WHERE userid = ?''', (value_user, user))

                self.connection_pool.commit()
                
                cursor.close()

                return True

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

        return False

    def get_user_rank(self, user_id):

        try:
            cursor = self.connection_pool.cursor()

            cursor.execute('''
                SELECT userid, points
                FROM users
                ORDER BY points DESC
            ''')

            ranking = cursor.fetchall()

            pos = [i + 1 for i, (id, _) in enumerate(ranking) if id == user_id]

            if pos:
                
                cursor.close()

                return pos[0]
            else:

                
                cursor.close()

                return None

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return None

    def get_users_ranking(self, ranking_type='points', limit=10):
        try:
            if not self.is_connected:
                utils.error_log("Erro: Banco de dados não conectado. 16")
                return None

            cursor = self.connection_pool.cursor()

            valid_ranking_types = ["points", "gifts", "likes", "shares"]

            if ranking_type not in valid_ranking_types:
                utils.error_log("Erro: Tipo de ranking inválido. 17")
                return None

            cursor.execute(f'''
                SELECT userid, display_name, username, roles, likes, shares, gifts, points, profile_pic
                FROM users
                ORDER BY {ranking_type} DESC
                LIMIT ?
            ''', (limit,))

            rows = cursor.fetchall()

            columns = ["userid", "display_name", "username", "roles",
                       "likes", "shares", "gifts", "points", "profile_pic"]
            rank_data = [dict(zip(columns, row)) for row in rows]

            cursor.close()

            return rank_data

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return None
        
    def get_all_users_rank(self, type_rank, limit):

        try:
            if not self.is_connected:
                utils.error_log("Erro: Banco de dados não conectado. 14")
                return None

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                SELECT userid, display_name, username, roles, likes, shares, gifts, points, profile_pic
                FROM users
                ORDER BY {} DESC
                LIMIT {}
            '''.format(type_rank, limit))

            rows = cursor.fetchall()

            columns = ["userid", "display_name", "username", "roles",
                       "likes", "shares", "gifts", "points", "profile_pic"]
            rank_data = [dict(zip(columns, row)) for row in rows]

            
            cursor.close()
            
            return rank_data

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return None

    def clear_database_without_activity(self):
        
        try:
            if not self.is_connected:
                utils.error_log("Erro: Banco de dados não conectado. 6 ")
                return False

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                DELETE FROM users
                WHERE likes = 0 AND shares = 0 AND gifts = 0 AND points = 0
            ''')

            self.connection_pool.commit()

            cursor.close()

            return True

        except Exception as e:
            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return False

    def update_user_value(self, value_type, value, userid):

        try:

            cursor = self.connection_pool.cursor()

            if value_type == 'roles':
                value = ','.join(value)

            cursor.execute(f'''
                UPDATE users SET {value_type} = ? WHERE userid = ?
            ''', (value, userid))

            self.connection_pool.commit()

            
            cursor.close()
            
            return True

        except Exception as e:
            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return None

    def close(self):

        try:

            if self.is_connected:

                self.connection_pool.close()

            else:

                utils.error_log("Erro: Banco de dados não conectado.15")

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":

                utils.error_log(e)

            utils.error_log(e)


class GoalManager:

    def __init__(self):

        self.connection_pool = db_manager.connection_pool_goal
        self.is_connected = db_manager.connection_goal

    def _check_connection(self):

        if not self.is_connected:
            print("Erro: Conexão com o banco de dados não estabelecida.")
            return False
        
        return True

    def get_goal(self, goal_type):

        try:
            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                SELECT * FROM '{goal_type}' ''')

            result = cursor.fetchone()

            cursor.close()

            if result:
                
                if goal_type == "gift":
                    columns = [
                        "status",
                        "event",
                        "goal",
                        "gift",
                        "goal_after",
                        "goal_style",
                        "current",
                        "sound_status",
                        "sound_file",
                        "sound_volume",
                        "goal_text",
                        "text_size",
                        "outer_bar",
                        "goal_above",
                        "goal_type",
                        "background_color",
                        "title_text",
                        "progress_bar",
                        "progress_bar_background",
                        "background_border",
                        "progress_bar_background_opacity",
                        "video_status",
                        "video_file",
                        "video_time"
                        ]
                else:
                    columns = [
                        "status",
                        "event",
                        "goal",
                        "goal_after",
                        "goal_style",
                        "current",
                        "sound_status",
                        "sound_file",
                        "sound_volume",
                        "goal_text",
                        "text_size",
                        "outer_bar",
                        "goal_above",
                        "goal_type",
                        "background_color",
                        "title_text",
                        "progress_bar",
                        "progress_bar_background",
                        "background_border",
                        "progress_bar_background_opacity",
                        "video_status",
                        "video_file",
                        "video_time"
                        ]

                goal_data = dict(zip(columns, result))

                return goal_data
            
            return False

        except Exception as e:
            print(f"Erro ao obter meta: {e}")

            return False
        
    def save_goal(self, goal_data, goal_type):

        try:
            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()
            
            if goal_type == "gift":

                cursor.execute(f'''
                    UPDATE '{goal_type}'
                    SET status = ?,
                        event = ?,
                        goal = ?,
                        gift = ?,
                        goal_after = ?,
                        sound_status = ?,
                        sound_file = ?,
                        sound_volume = ?,
                        video_status = ?,
                        video_file = ?,
                        video_time = ?
                ''', (goal_data["status"],
                    goal_data["event"],
                    goal_data["goal"],
                    goal_data["gift"],
                    goal_data["goal_after"],
                    goal_data["sound_status"],
                    goal_data["sound_file"],
                    goal_data["sound_volume"],
                    goal_data["video_status"],
                    goal_data["video_file"],
                    goal_data["video_time"]))

            else:
                cursor.execute(f'''
                    UPDATE '{goal_type}'
                    SET status = ?,
                        event = ?,
                        goal = ?,
                        goal_after = ?,
                        sound_status = ?,
                        sound_file = ?,
                        sound_volume = ?,
                        video_status = ?,
                        video_file = ?,
                        video_time = ?
                ''', (goal_data["status"],
                    goal_data["event"],
                    goal_data["goal"],
                    goal_data["goal_after"],
                    goal_data["sound_status"],
                    goal_data["sound_file"],
                    goal_data["sound_volume"],
                    goal_data["video_status"],
                    goal_data["video_file"],
                    goal_data["video_time"]))

            self.connection_pool.commit()
            cursor.close()
            
            return True

        except Exception as e:

            print(f"Erro ao salvar meta: {e}")

            return False
        
    def save_html(self, goal_data, goal_type):

        try:

            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                UPDATE '{goal_type}'
                SET goal_style = ?,
                    goal_above = ?,
                    goal_type = ?,
                    goal_text = ?,
                    title_text = ?,
                    text_size = ?,
                    progress_bar = ?,
                    progress_bar_background = ?,
                    background_color = ?,
                    background_border = ?,
                    progress_bar_background_opacity = ?
            ''', (goal_data["goal_style"],
                goal_data["goal_above"],
                goal_data["goal_type"],
                goal_data["text_value"],
                goal_data["text_color"],
                goal_data["text_size"],
                goal_data["bar_color"],
                goal_data["background_bar_color"],
                goal_data["background_color"],
                goal_data["background_border"],
                goal_data["background_bar_color_opacity"]))


            self.connection_pool.commit()
            cursor.close()
            
            return True

        except Exception as e:

            print(f"Erro ao salvar meta: {e}")

            return False
        
    def reset_goal(self,goal_type):

        try:
            
            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                UPDATE '{goal_type}'
                SET current = ?
            ''', (0,))


            self.connection_pool.commit()
            cursor.close()
            
            return True

        except Exception as e:

            print(f"Erro ao salvar meta: {e}")

            return False
    
    def reset_goal(self,goal_type):

        try:
            
            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                UPDATE '{goal_type}'
                SET current = ?
            ''', (0,))

            self.connection_pool.commit()
            cursor.close()
            
            return True

        except Exception as e:

            print(f"Erro ao salvar meta: {e}")

            return False
        
    def get_current(self, goal_type):

        try:

            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                SELECT current FROM '{goal_type}' ''')

            result = cursor.fetchone()

            cursor.close()

            if result:

                return result[0]

            return False

        except Exception as e:
            print(f"Erro ao obter meta: {e}")

            return False
        
    def update_current(self, current, goal_type):

        try:

            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                UPDATE '{goal_type}'
                SET current = ?
            ''', (current,))

            self.connection_pool.commit()
            cursor.close()

            return True

        except Exception as e:
            print(f"Erro ao obter meta: {e}")

            return False
        
    def update_goal(self, goal, goal_type):

        try:

            if not self._check_connection():
                return

            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                UPDATE '{goal_type}'
                SET goal = ?
            ''', (goal,))

            self.connection_pool.commit()
            cursor.close()

            return True

        except Exception as e:
            print(f"Erro ao obter meta: {e}")

            return False