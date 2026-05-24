import sqlite3
from datetime import datetime

DB_NAME = "iris_database.db"

def init_db():
    """Инициализация базы данных"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                quese_balance INTEGER DEFAULT 0,
                partner_id INTEGER DEFAULT NULL,
                last_farm TEXT DEFAULT NULL
            )
        ''')
        conn.commit()

def get_or_create_user(tg_id: int, username: str, first_name: str) -> dict:
    """Получает пользователя или создает его, если его нет"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
        user = cursor.fetchone()
        
        if user is None:
            cursor.execute(
                "INSERT INTO users (tg_id, username, first_name) VALUES (?, ?, ?)",
                (tg_id, username, first_name)
            )
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
            user = cursor.fetchone()
            
        return dict(user)

def update_farm(tg_id: int, new_balance: int, farm_time: str):
    """Обновляет баланс и время последнего фарма"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET quese_balance = ?, last_farm = ? WHERE tg_id = ?",
            (new_balance, farm_time, tg_id)
        )
        conn.commit()

def create_marriage(user_id: int, partner_id: int):
    """Записывает брак в базу для обоих пользователей"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET partner_id = ? WHERE tg_id = ?", (partner_id, user_id))
        cursor.execute("UPDATE users SET partner_id = ? WHERE tg_id = ?", (user_id, partner_id))
        conn.commit()

def divorce_users(user_id: int, partner_id: int):
    """Развод пары"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET partner_id = NULL WHERE tg_id = ?", (user_id,))
        cursor.execute("UPDATE users SET partner_id = NULL WHERE tg_id = ?", (partner_id,))
        conn.commit()
