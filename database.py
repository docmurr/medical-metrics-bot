# database.py
import sqlite3
import os
from datetime import datetime

DB_NAME = 'bot.db'

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Таблица заинтересованных пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interested_users (
        user_id INTEGER PRIMARY KEY,
        interested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')

    # Таблица оплативших пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS paid_users (
        user_id INTEGER PRIMARY KEY,
        paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        payment_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')

    # Таблица сообщений между админами и пользователями
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

def add_user(user_id, username, first_name, last_name):
    """Добавление пользователя в базу"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
    VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name))

    conn.commit()
    conn.close()

def mark_as_interested(user_id):
    """Пометить пользователя как заинтересованного"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Сначала добавляем пользователя, если его еще нет
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO users (user_id) VALUES (?)
        ''', (user_id,))

    # Помечаем как заинтересованного
    cursor.execute('''
    INSERT OR IGNORE INTO interested_users (user_id)
    VALUES (?)
    ''', (user_id,))

    conn.commit()
    conn.close()

def is_interested(user_id):
    """Проверить, заинтересован ли пользователь"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT 1 FROM interested_users WHERE user_id = ?
    ''', (user_id,))

    result = cursor.fetchone()
    conn.close()
    return result is not None

def add_payment(user_id, payment_id):
    """Добавить информацию об оплате"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR REPLACE INTO paid_users (user_id, payment_id)
    VALUES (?, ?)
    ''', (user_id, payment_id))

    conn.commit()
    conn.close()

def is_paid(user_id):
    """Проверить, оплатил ли пользователь"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT 1 FROM paid_users WHERE user_id = ?
    ''', (user_id,))

    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_interested_users():
    """Получить список заинтересованных пользователей"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT u.user_id, u.username, u.first_name, u.last_name, i.interested_at
    FROM users u
    JOIN interested_users i ON u.user_id = i.user_id
    ''')

    users = cursor.fetchall()
    conn.close()
    return users

def get_paid_users():
    """Получить список оплативших пользователей"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT u.user_id, u.username, u.first_name, u.last_name, p.paid_at
    FROM users u
    JOIN paid_users p ON u.user_id = p.user_id
    ''')

    users = cursor.fetchall()
    conn.close()
    return users

def add_message(sender_id, receiver_id, message):
    """Добавить сообщение в историю"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO messages (sender_id, receiver_id, message)
    VALUES (?, ?, ?)
    ''', (sender_id, receiver_id, message))

    conn.commit()
    conn.close()

def get_message_history(user_id):
    """Получить историю сообщений для пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT sender_id, receiver_id, message, sent_at
    FROM messages
    WHERE sender_id = ? OR receiver_id = ?
    ORDER BY sent_at
    ''', (user_id, user_id))

    messages = cursor.fetchall()
    conn.close()
    return messages