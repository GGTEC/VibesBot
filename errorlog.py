import sqlite3

from datetime import datetime

import utils
import os
from discord_webhook import DiscordWebhook, DiscordEmbed


class ErrorManager:

    def __init__(self):

        self.errors_log_path = f"{utils.local_work('appdata_path')}/database/error_database.db"
    
        self.connection_pool_errors = sqlite3.connect(self.errors_log_path, check_same_thread=False, timeout=5)
        self.conection_errors = True

    def error_log(self, ex):

        try:

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

            error = str(f'Erro = type: {error_type} | message: {error_message} | trace: {trace} | time: {time_error} | Code Version : {utils.get_version('code')} | Online Version : {utils.get_version('online')}')

            data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json", "load")

            if data["error_status"] == True:

                username = data["USERNAME"]
                
                if username == None or username == "":
                    username = "Não autenticado"
                
                WEBHOOKURL = os.getenv('WEBHOOKURLERROR')

                webhook_login = DiscordWebhook(url=WEBHOOKURL)

                embed_login = DiscordEmbed(
                    title='Relátorio de erro',
                    description= F'https://www.tiktok.com/@{username}' ,
                    color= '03b2f8'
                )

                embed_login.add_embed_field(
                    name='Erro',
                    value=error,
                )

                embed_login.set_author(name=username, url=f'https://www.tiktok.com/@{username}')
                
                webhook_login.add_embed(embed_login)
                webhook_login.execute()

            cursor = self.connection_pool_errors.cursor()

            cursor.execute('''
                INSERT INTO logs (timestamp, message)
                VALUES (?, ?)
            ''', ( str(datetime.now()), error))
            
            self.connection_pool_errors.commit()

            cursor.close()

        except Exception as e:
            print(e)

    def get_recent_logs(self, limit=1000):

        try:
            cursor = self.connection_pool_errors.cursor()

            cursor.execute(f'''
                SELECT * FROM logs
                ORDER BY timestamp DESC
                LIMIT {limit}
            ''')
            
            result = cursor.fetchall()

            columns = ["timestamp", "message"]

            recent_logs = [dict(zip(columns, row)) for row in result]

            cursor.close()
            
            return recent_logs
        
        except Exception as e:

            print(e)

            return []

    def clean_up_logs(self, max_items=1000):

        try:

            cursor = self.connection_pool_errors.cursor()

            cursor.execute(f'''
                DELETE FROM logs
                WHERE ROWID NOT IN (
                    SELECT ROWID FROM logs
                    ORDER BY timestamp DESC
                    LIMIT {max_items}
                )
            ''')

            self.connection_pool_errors.commit()

            cursor.close()
            
        except Exception as e:
            
            print(e)

    def clear_logs(self):

        try:

            cursor = self.connection_pool_errors.cursor()

            cursor.execute('''DELETE FROM logs''')

            self.connection_pool_errors.commit()
            cursor.close()

        except Exception as e:
            print(f"Error clearing logs: {e}")

