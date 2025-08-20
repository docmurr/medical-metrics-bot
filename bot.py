# bot.py
import telebot
from config import BOT_TOKEN, SALE_START_DATE
from database import init_db
from scheduler import start_scheduler
from user_handlers import register_user_handlers
from admin_handlers import register_admin_handlers
from keep_alive import keep_alive  # ← импортируем функцию
from datetime import datetime
import time
import threading
import os

def main():
    # Инициализация базы данных
    init_db()

    # Запуск keep_alive для предотвращения засыпания
    # ВАЖНО: сохраняем результат, чтобы поток не завершился
    keep_alive()  # ← эта функция запускает Flask-сервер в отдельном потоке

    # Создание бота
    bot = telebot.TeleBot(BOT_TOKEN)

    # Регистрация обработчиков
    register_user_handlers(bot)
    register_admin_handlers(bot)

    # Запуск планировщика
    scheduler = start_scheduler(bot)  # ← передаём bot в планировщик

    # Запуск бота
    print("Бот запущен и работает 24/7...")
    bot.infinity_polling()

if __name__ == "__main__":
    main()