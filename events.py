import json
import utils
from database import DatabaseManager
from datetime import datetime


class EventLogManager:

    def __init__(self):

        self.db_manager = DatabaseManager()
        self.connection_pool = self.db_manager.connection_pool_events
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):

        try:

            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS event_log (
                    timestamp TEXT,
                    type TEXT,
                    message TEXT,
                    user_input TEXT
                )
            ''')

            self.connection_pool.commit()

            cursor.close()

        except Exception as e:
            utils.error_log(e)


    def add_event(self, event_data):

        try:

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                INSERT INTO event_log (timestamp, type, message, user_input)
                VALUES (?, ?, ?, ?)
            ''', (str(datetime.now()),  event_data['type'], event_data['message'], event_data['user_input']))
            
            self.connection_pool.commit()

            cursor.close()
            
            return True
        
        except Exception as e:
            
            utils.error_log(e)

            return False

    def get_recent_events(self, limit=100):

        try:

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