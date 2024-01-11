import utils
from sqlite3 import dbapi2
from sqlite3.dbapi2 import Connection, Cursor
from database import DatabaseManager

database_manager = DatabaseManager()


class UserDatabaseManager:

    def __init__(self):

        self.connection_pool = database_manager.connection_pool
        self.connection_pool_backup = database_manager.connection_pool_backup

        self.is_connected = database_manager.is_connected
        self.is_connected_backup = database_manager.is_connected_backup

    def connect(self):

        try:

            if not self.is_connected:
                utils.error_log("Erro: Banco de dados não conectado. 4")
                return False

            if not self.is_table_valid():

                if self.restore_backup():

                    utils.error_log("Tabela recuperada do backup com sucesso 1.")
                else:

                    utils.error_log("Erro ao recuperar a tabela do backup 2.")

            else:

                self.backup_database()

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

    def is_table_valid(self):

        try:

            cursor = self.connection_pool.cursor()

            cursor.execute("SELECT * FROM users LIMIT 1")

            return True  # Se executou sem erros, a tabela está válida

        except Exception as e:

            utils.error_log(f"Tabela corrompida: {e}")

            return False

    def backup_database(self):

        try:

            if self.is_connected_backup:

                cursor_backup = self.connection_pool_backup.cursor()

                cursor_backup.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                response = cursor_backup.fetchone()

                if response is None:

                    cursor_backup.execute('''
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
                    self.connection_pool_backup.commit()

                cursor_backup.execute('DELETE FROM users')
                self.connection_pool_backup.commit()

                cursor_backup.execute('VACUUM')
                self.connection_pool_backup.commit()

                users_data = self.get_all_users_data()

                for userid, data in users_data.items():

                    roles_string = ",".join(data["roles"])
                    roles_string_replace = roles_string.replace(" ", "")

                    cursor_backup.execute('''
                        INSERT INTO users (
                            userid, display_name, username, roles, likes, shares, gifts, points, profile_pic
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        data["userid"], data["display_name"], data["username"],
                        roles_string_replace, data["likes"], data["shares"],
                        data["gifts"], data["points"], data["profile_pic"]
                    ))

                self.connection_pool_backup.commit()

                cursor_backup.close()

                return True

            else:

                utils.error_log("Não foi possivel conectar a o banco de dados de backup.")
                return False

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return False

    def restore_backup(self):

        try:
            if not self.is_connected:
                utils.error_log("Erro: Banco de dados não conectado. 4")
                return False

            if not self.is_connected_backup:
                utils.error_log(
                    "Erro: Banco de dados de backup não conectado. 4")
                return False

            cursor_backup = self.connection_pool_backup.cursor()

            users_data = self.get_all_users_data_from_backup(cursor_backup)

            if users_data:

                for userid, data in users_data.items():
                    self.add_user_database(data)

                cursor_backup.close()

                return True
            
            else:

                cursor_backup.close()

                return False

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return False

    def get_all_users_data_from_backup(self, cursor):

        try:
            if not self.is_connected:
                utils.error_log("Erro: Banco de dados não conectado. 10")
                return None

            if not self.is_connected_backup:
                utils.error_log("Erro: Banco de dados não conectado. 10")
                return None

            cursor_backup = self.connection_pool_backup.cursor()

            cursor_backup.execute('''SELECT * FROM users''')

            results = cursor_backup.fetchall()

            users_data = {}

            for result in results:
                roles_list = [element.strip()
                              for element in result[3].split(',')]
                user_data = {
                    "userid": result[0],
                    "display_name": result[1],
                    "username": result[2],
                    "roles": roles_list,
                    "likes": result[4],
                    "shares": result[5],
                    "gifts": result[6],
                    "points": result[7],
                    "profile_pic": result[8]
                }

                users_data[result[0]] = user_data


            cursor_backup.close()

            return users_data

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":
                utils.error_log(e)

            return None

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

            cursor = self.connection_pool.cursor()

            display_name = data["display_name"]
            username = data["username"]
            profile_pic = data["profile_pic"]
            userid = data["userid"]

            if "roles" in data:
                roles_user = list(set([role.strip()
                                  for role in data["roles"]]))
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

                cursor.execute('''
                    INSERT INTO users (
                        userid, display_name, username, roles, likes, shares, gifts, points, profile_pic
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    userid, display_name, username, roles_string_replace,
                    data.get("likes", 0), data.get(
                        "shares", 0), data.get("gifts", 0),
                    data.get("points", 0), profile_pic
                ))

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

            cursor.execute('''
                SELECT * FROM users
            ''')

            results = cursor.fetchall()

            users_data = {}

            for result in results:

                lista_sem_espacos = [element.strip()
                                     for element in result[3].split(',')]

                user_data = {
                    "userid": result[0],
                    "display_name": result[1],
                    "username": result[2],
                    "roles": lista_sem_espacos,
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

                self.backup_database()

            else:

                utils.error_log("Erro: Banco de dados não conectado.15")

        except Exception as e:

            if not str(e) == "Cannot operate on a closed database":

                utils.error_log(e)

            utils.error_log(e)
