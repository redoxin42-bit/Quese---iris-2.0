import sqlite3
import datetime

DB_NAME = "bot.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                username TEXT,
                quese_balance INTEGER DEFAULT 0,
                partner_id INTEGER DEFAULT NULL,
                last_farm TEXT DEFAULT NULL
            )
        ''')
        # Таблица мешка (инвентаря)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                tg_id INTEGER,
                item_name TEXT,
                quantity INTEGER DEFAULT 1,
                PRIMARY KEY (tg_id, item_name)
            )
        ''')
        conn.commit()
