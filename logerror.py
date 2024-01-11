from datetime import datetime
from database import DatabaseManager

class LogManager:

    def __init__(self):
    
        self.db_manager = DatabaseManager()
        self.connection_pool = self.db_manager.connection_pool_errors
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):

        try:

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    timestamp TEXT,
                    message TEXT
            )''')
            
            self.connection_pool.commit()

            cursor.close()

        except Exception as e:

            print(e)

    def save_log(self, message):

        try:

            cursor = self.connection_pool.cursor()

            cursor.execute('''
                INSERT INTO logs (timestamp, message)
                VALUES (?, ?)
            ''', ( str(datetime.now()), message))
            
            self.connection_pool.commit()

            cursor.close()

        except Exception as e:

            print(e)

    def get_recent_logs(self, limit=1000):

        try:
            cursor = self.connection_pool.cursor()

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

            cursor = self.connection_pool.cursor()

            cursor.execute(f'''
                DELETE FROM logs
                WHERE ROWID NOT IN (
                    SELECT ROWID FROM logs
                    ORDER BY timestamp DESC
                    LIMIT {max_items}
                )
            ''')

            self.connection_pool.commit()

            cursor.close()
            
        except Exception as e:
            print(e)

    def clear_logs(self):

        try:
            cursor = self.connection_pool.cursor()

            cursor.execute('''
                DELETE FROM logs
            ''')

            self.connection_pool.commit()
            cursor.close()

        except Exception as e:
            print(f"Error clearing logs: {e}")

