# config.py
import os
from datetime import datetime, timedelta

# Токен вашего бота (получите у @BotFather)
BOT_TOKEN = os.getenv('BOT_TOKEN', 'ВАШ_ТОКЕН')

# ID администраторов (получите через @userinfobot)
ADMIN_IDS = [
    676228432,  # Замените на ваш ID
    104769408,  # ID второго администратора (если есть)
    664833698   # ID третьего администратора (если есть)
]

# Дата старта продаж (ГГГГ, ММ, ДД, ЧЧ, ММ, СС)
SALE_START_DATE = datetime(2025, 9, 1, 0, 0, 0)  # Замените на реальную дату

# Путь к файлам
PROMO_VIDEO_PATH = 'data/promo/promo_video.m4v'
PROMO_DOC_PATH = 'data/promo/promo_document.pdf'
MANUAL_PATH = 'data/manual/medical_metrics_manual.pdf'

# Ссылка на оплату
PAYMENT_URL = "https://vk.com/gorilla_shigella"

# Период уведомлений (в часах)
NOTIFICATION_INTERVAL = 24

def get_time_until_sale():
    """Возвращает оставшееся время до старта продаж в виде строки"""
    now = datetime.now()
    if now >= SALE_START_DATE:
        return "уже начались"

    delta = SALE_START_DATE - now
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    return f"{days} дней, {hours} часов, {minutes} минут"