# user_handlers.py
import os
from config import (
    PROMO_VIDEO_PATH,
    PROMO_DOC_PATH,
    MANUAL_PATH,
    PAYMENT_URL,
    SALE_START_DATE,
    ADMIN_IDS
)
from database import add_user, mark_as_interested, is_paid, add_payment
from datetime import datetime
import telebot


def register_user_handlers(bot):
    """
    Регистрирует все обработчики для пользователей
    """

    def get_time_until_sale():
        """Возвращает оставшееся время до старта продаж"""
        now = datetime.now()
        if now >= SALE_START_DATE:
            return "продажи уже начались!"

        delta = SALE_START_DATE - now
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60

        return f"{days} дней, {hours} часов, {minutes} минут"

    # === КЛАВИАТУРА ===
    def get_main_menu():
        """Создаёт клавиатуру с основными командами"""
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard.add(
            "ℹ️ О методичке",
            "🎬 Промо",
            "⏳ Время до старта",
            "💳 Предзаказ",
            "📞 Связаться с админом"
        )
        return keyboard

    # === КОМАНДА /start ===
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        """Приветственное сообщение с клавиатурой"""
        user = message.from_user
        add_user(user.id, user.username, user.first_name, user.last_name)

        time_left = get_time_until_sale()

        welcome_message = (f"👋 Добро пожаловать в сообщество медицинской наукометрии!\n\n"
                          f"⏳ <b>Осталось до старта продаж:</b> *{time_left}*\n\n"
                          f"📘 Уникальная методичка по медицинской наукометрии поможет вам:\n"
                          f"✅ Легко разобраться в медицинской наукометрии\n"
                          f"✅ Проводить качественные исследования\n"
                          f"✅ Публиковать статьи в топовых журналах\n\n"
                          f"Выберите, что хотите сделать:")

        bot.send_message(
            message.chat.id,
            welcome_message,
            parse_mode='HTML',
            reply_markup=get_main_menu()
        )


    # === ОБРАБОТКА КНОПКИ "О методичке" ===
    @bot.message_handler(func=lambda message: message.text == "ℹ️ О методичке")
    def about_manual(message):
        bot.send_message(
            message.chat.id,
            "📘 <b>Методичка по медицинской наукометрии</b>\n\n"
            "Это практическое руководство для врачей, научных сотрудников и аспирантов.\n\n"
            "Вы научитесь:\n"
            "✅ Анализировать научные публикации\n"
            "✅ Оценивать качество исследований\n"
            "✅ Подготавливать статьи к публикации\n"
            "✅ Работать с метриками (h-index, IF, Altmetric и др.)",
            parse_mode='HTML'
        )

    # === ОБРАБОТКА КНОПКИ "Промо" ===
    @bot.message_handler(func=lambda message: message.text == "🎬 Промо")
    def promo_button(message):
        user = message.from_user
        add_user(user.id, user.username, user.first_name, user.last_name)
        mark_as_interested(user.id)

        try:
            with open(PROMO_VIDEO_PATH, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="🎥 Промо-видео о методичке")
        except Exception as e:
            bot.send_message(message.chat.id, f"🎥 Видео временно недоступно: {e}")

        try:
            with open(PROMO_DOC_PATH, 'rb') as doc:
                bot.send_document(message.chat.id, doc, caption="📄 Промо-документ с подробной информацией")
        except Exception as e:
            bot.send_message(message.chat.id, f"📄 Документ временно недоступен: {e}")

    # === ОБРАБОТКА КНОПКИ "Время до старта" ===
    @bot.message_handler(func=lambda message: message.text == "⏳ Время до старта")
    def time_button(message):
        time_left = get_time_until_sale()
        bot.send_message(
            message.chat.id,
            f"⏳ <b>Осталось до старта продаж:</b> *{time_left}*",
            parse_mode='HTML'
        )

    # === ОБРАБОТКА КНОПКИ "Предзаказ" ===
    @bot.message_handler(func=lambda message: message.text == "💳 Предзаказ")
    def preorder(message):
        now = datetime.now()
        time_left = get_time_until_sale()

        preorder_message = (f"🌟 <b>Забронируйте методичку уже сейчас!</b>\n\n"
                           f"📅 Продажи начнутся через: *{time_left}*\n\n"
                           f"✅ Получите методичку в первый день\n"
                           f"🎁 Участие в закрытом обсуждении с авторами\n"
                           f"🔒 Ваша копия будет зарезервирована\n\n"
                           f"💳 <b>Ссылка для предоплаты:</b>\n"
                           f"{PAYMENT_URL}\n\n"
                           f"После оплаты напишите сюда ваш <b>ID платежа</b> — и мы подтвердим бронь.")

        bot.send_message(message.chat.id, preorder_message, parse_mode='HTML')

    # === ОБРАБОТКА КНОПКИ "Связаться с админом" ===
    @bot.message_handler(func=lambda message: message.text == "📞 Связаться с админом")
    def contact_admin(message):
        bot.send_message(
            message.chat.id,
            "📬 Вы можете задать любой вопрос!\n\n"
            "Напишите сюда — и администратор свяжется с вами в ближайшее время.\n\n"
            "Пример:\n"
            "<i>«Когда начнутся продажи?»\n"
            "«Есть ли скидки для студентов?»</i>",
            parse_mode='HTML'
        )


    # === КОМАНДА /time ===
    @bot.message_handler(commands=['time'])
    def show_time_left(message):
        time_left = get_time_until_sale()
        bot.reply_to(
            message,
            f"⏳ <b>Осталось до старта продаж:</b> *{time_left}*",
            parse_mode='HTML'
        )


    # === КОМАНДА /promo ===
    @bot.message_handler(commands=['promo'])
    def send_promo_materials(message):
        user = message.from_user
        add_user(user.id, user.username, user.first_name, user.last_name)
        mark_as_interested(user.id)

        try:
            with open(PROMO_VIDEO_PATH, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="🎥 Промо-видео о методичке")
        except Exception as e:
            bot.send_message(message.chat.id, f"🎥 Видео временно недоступно: {e}")

        try:
            with open(PROMO_DOC_PATH, 'rb') as doc:
                bot.send_document(message.chat.id, doc, caption="📄 Промо-документ с подробной информацией")
        except Exception as e:
            bot.send_message(message.chat.id, f"📄 Документ временно недоступен: {e}")

        time_left = get_time_until_sale()
        bot.send_message(
            message.chat.id,
            f"Спасибо за интерес! 🙌\n\n"
            f"⏳ До старта продаж осталось: *{time_left}*\n\n"
            f"Нажмите /start, чтобы увидеть меню.",
            parse_mode='HTML'
        )


    # === КОМАНДА /buy ===
    @bot.message_handler(commands=['buy'])
    def send_payment_link(message):
        now = datetime.now()

        if now < SALE_START_DATE:
            time_left = get_time_until_sale()
            bot.reply_to(
                message,
                f"Продажи начнутся через: *{time_left}*\n\n"
                f"Но вы можете уже сейчас сделать <b>предзаказ</b> — нажмите /start и выберите «💳 Предзаказ».",
                parse_mode='HTML'
            )
            return

        if is_paid(message.from_user.id):
            bot.reply_to(
                message,
                "✅ Вы уже приобрели методичку! Спасибо за покупку.\n\n"
                "Если у вас возникли вопросы, напишите нам."
            )
            return

        payment_message = (f"💳 <b>Ссылка для оплаты:</b>\n\n"
                          f"{PAYMENT_URL}\n\n"
                          f"После оплаты напишите сюда ваш <b>ID платежа</b>.")

        bot.reply_to(message, payment_message, parse_mode='HTML')


    # === ОБРАБОТКА ID ПЛАТЕЖА ===
    @bot.message_handler(func=lambda message: "ID платежа" in message.text or "платежа" in message.text.lower())
    def process_payment(message):
        user_id = message.from_user.id

        if is_paid(user_id):
            bot.reply_to(
                message,
                "✅ Вы уже приобрели методичку! Спасибо за покупку.\n\n"
                "Если у вас возникли вопросы, напишите нам."
            )
            return

        payment_id = None
        words = message.text.split()
        for word in words:
            if len(word) > 10 and word.replace('-', '').replace('_', '').isalnum():
                payment_id = word
                break

        if not payment_id:
            bot.reply_to(
                message,
                "❌ Не удалось определить ID платежа. Пожалуйста, отправьте точный ID платежа."
            )
            return

        add_payment(user_id, payment_id)

        try:
            with open(MANUAL_PATH, 'rb') as manual:
                bot.send_document(
                    user_id,
                    manual,
                    caption="📘 <b>Ваша методичка по медицинской наукометрии!</b>\n\n"
                            "Спасибо за покупку! Если у вас возникнут вопросы, наши создатели всегда готовы помочь.",
                    parse_mode='HTML'
                )
            bot.send_message(
                user_id,
                "🎉 Вы также были добавлены в закрытую беседу с создателями методички.\n\n"
                "Добро пожаловать в сообщество профессионалов!"
            )
        except Exception as e:
            bot.send_message(
                user_id,
                "❌ Произошла ошибка при отправке методички. Пожалуйста, свяжитесь с администратором."
            )
            print(f"❌ Ошибка при отправке методички пользователю {user_id}: {e}")