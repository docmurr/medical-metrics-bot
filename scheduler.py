# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
from datetime import datetime, timedelta
import telebot
from config import NOTIFICATION_INTERVAL, SALE_START_DATE
from database import get_interested_users

def send_notifications(bot):
    """Отправка периодических уведомлений заинтересованным пользователям"""
    now = datetime.now()

    # Проверяем, не началась ли продажа
    if now >= SALE_START_DATE:
        message = "🎉 Продажи методички по медицинской наукометрии уже начались!\n\n" \
                  "Напишите /buy, чтобы получить ссылку на оплату и стать обладателем уникального материала!"
    else:
        time_left = get_time_until_sale()
        message = f"⏳ Осталось всего {time_left} до старта продаж методички по медицинской наукометрии!\n\n" \
                  "Этот материал поможет вам:\n" \
                  "✅ Легко разобраться в медицинской наукометрии\n" \
                  "✅ Проводить качественные исследования\n" \
                  "✅ Публиковать статьи в топовых журналах\n\n" \
                  "Напишите /promo, чтобы посмотреть промо-материалы и узнать больше!"

    # Отправляем всем заинтересованным пользователям
    interested_users = get_interested_users()
    for user in interested_users:
        user_id = user[0]
        try:
            bot.send_message(user_id, message)
            time.sleep(0.1)  # Задержка между сообщениями для избежания блокировки
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

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

def start_scheduler(bot):
    """Запуск планировщика уведомлений"""
    scheduler = BackgroundScheduler()

    # Добавляем задачу для периодических уведомлений
    scheduler.add_job(
        send_notifications,
        IntervalTrigger(hours=NOTIFICATION_INTERVAL),
        args=[bot]
    )

    # Добавляем задачу для первого уведомления сразу после запуска
    scheduler.add_job(
        send_notifications,
        'date',
        run_date=datetime.now(),
        args=[bot]
    )

    scheduler.start()
    return scheduler