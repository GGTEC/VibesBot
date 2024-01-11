from sqlite3 import dbapi2
from sqlite3.dbapi2 import Connection, Cursor

import utils

class DatabaseManager:

    def __init__(self):

        self.backup_path  = f"{utils.local_work('appdata_path')}/database/users_database_backup.db"
        self.old_database_path = f"{utils.local_work('appdata_path')}/user_info/users_database.db"
        self.users_database_path = f"{utils.local_work('appdata_path')}/database/users_database.db"
        self.events_database_path = f"{utils.local_work('appdata_path')}/database/events_database.db"
        self.errors_log_path = f"{utils.local_work('appdata_path')}/database/error_database.db"
        self.commands_path = f"{utils.local_work('appdata_path')}/database/commands_database.db"

        self.connection_pool = None
        self.conection = None

        self.connection_pool_backup = None
        self.conection_backup = None

        self.connection_pool_events = None
        self.conection_events = None

        self.connection_pool_errors = None
        self.conection_errors = None

        self.connection_pool_commands = None
        self.conection_commands = None

        self.connection_pool_old_database = None
        self.conection_old_database = None

        self.is_connected = False
        self.is_connected_backup = False
        self.is_connected_events = False
        self.is_connected_errors = False
        self.is_connected_commands = False
        self.is_connected_old_database = False


        self.connect()


    def connect(self):

        try:

            self.connection_pool = dbapi2.connect(self.users_database_path, check_same_thread=False, timeout=5)
            self.is_connected = True

            self.connection_pool_events = dbapi2.connect(self.events_database_path, check_same_thread=False, timeout=5)
            self.is_connected_events = True

            self.connection_pool_backup = dbapi2.connect(self.backup_path, check_same_thread=False, timeout=5)
            self.is_connected_backup = True

            self.connection_pool_errors = dbapi2.connect(self.errors_log_path, check_same_thread=False, timeout=5)
            self.is_connected_errors = True

            self.connection_pool_commands = dbapi2.connect(self.commands_path, check_same_thread=False, timeout=5) 
            self.is_connected_commands = True

            self.connection_pool_old_database = dbapi2.connect(self.old_database_path, check_same_thread=False, timeout=5)
            self.is_connected_old_database = True

            self.create_table_users()
            self.copy_users_data()

        except Exception as e:
            print(e)

    def create_table_users(self):
        try:

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    userid TEXT PRIMARY KEY,
                    display_name TEXT,
                    username TEXT,
                    roles TEXT,
                    likes INTEGER,
                    shares INTEGER,
                    gifts INTEGER,
                    points INTEGER,
                    profile_pic TEXT
                )
            ''')

            self.connection_pool.commit()

            cursor.close()

        except Exception as e:
            utils.error_log(e)

    def copy_users_data(self):

        try:

            self.create_table_users()
            
            cursor_old_db = self.connection_pool_old_database.cursor()
            cursor_new_db = self.connection_pool.cursor()

            cursor_old_db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            users_table_exists_A = cursor_old_db.fetchone()

            if not users_table_exists_A:

                return

            else:
        
                cursor_old_db.execute("SELECT * FROM users")
                users_data_A = cursor_old_db.fetchall()

                for user_data in users_data_A:

                    user_id_A = user_data[0]

                    cursor_new_db.execute("SELECT * FROM users WHERE userid = ?", (user_id_A,))
                    user_exists_B = cursor_new_db.fetchone()

                    if not user_exists_B:

                        cursor_new_db.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", user_data)

                self.connection_pool.commit()

                cursor_old_db.close()
                cursor_new_db.close()

        except Exception as e:

            utils.error_log(e)

        finally:
                
            cursor_old_db.close()
            cursor_new_db.close()

    def close(self):

        try:

            if self.is_connected:
                self.connection_pool.close()
            else:
                utils.error_log("Erro: Banco de dados não conectado.")

            if self.is_connected_backup:
                self.connection_pool_backup.close()
            else:
                utils.error_log("Erro: Banco de dados não conectado.")

            if self.is_connected_events:
                self.connection_pool_events.close()
            else:
                utils.error_log("Erro: Banco de dados não conectado.")

            if self.is_connected_errors:
                self.connection_pool_errors.close()
            else:
                utils.error_log("Erro: Banco de dados não conectado.")

            if self.is_connected_commands:
                self.connection_pool_commands.close()
            else:
                utils.error_log("Erro: Banco de dados não conectado.")

            if self.is_connected_old_database:
                self.connection_pool_old_database.close()
            else:
                utils.error_log("Erro: Banco de dados não conectado.")

        except Exception as e:
            utils.error_log(e)