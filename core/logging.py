import logging
import sqlite3
from django.conf import settings
from django.utils import timezone

class SQLiteLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.db_path = settings.DATABASES['logs_db']['NAME']
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS log_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level VARCHAR(10),
                    message TEXT,
                    timestamp DATETIME
                )
            ''')
            conn.commit()

    def emit(self, record):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO log_entries (level, message, timestamp)
                VALUES (?, ?, ?)
            ''', (record.levelname, self.format(record), timezone.now()))
            conn.commit()
        print(f"Log emitted to SQLite: {record.levelname} - {record.getMessage()}")  # Debug print

def get_logs(limit=100, level=None):
    db_path = settings.DATABASES['logs_db']['NAME']
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        if level:
            cursor.execute('''
                SELECT * FROM log_entries 
                WHERE level = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (level, limit))
        else:
            cursor.execute('''
                SELECT * FROM log_entries 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        return cursor.fetchall()