# admin_handlers.py
from config import ADMIN_IDS
from database import get_interested_users, get_paid_users, get_message_history, add_message
from datetime import datetime

def register_admin_handlers(bot):
    def is_admin(user_id):
        """Проверка, является ли пользователь администратором"""
        return user_id in ADMIN_IDS

    @bot.message_handler(commands=['admin'])
    def admin_panel(message):
        """Панель администратора"""
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "У вас нет прав доступа к админ-панели.")
            return

        admin_message = "🛡️ Админ-панель\n\n" \
                        "Доступные команды:\n" \
                        "/users - список заинтересованных пользователей\n" \
                        "/paid - список оплативших пользователей\n" \
                        "/history [user_id] - история сообщений с пользователем\n" \
                        "/reply [user_id] [сообщение] - ответить пользователю"

        bot.reply_to(message, admin_message)

    @bot.message_handler(commands=['users'])
    def list_interested_users(message):
        """Список заинтересованных пользователей"""
        if not is_admin(message.from_user.id):
            return

        users = get_interested_users()
        if not users:
            bot.reply_to(message, "Нет заинтересованных пользователей.")
            return

        response = "👥 Заинтересованные пользователи:\n\n"
        for i, user in enumerate(users, 1):
            user_id, username, first_name, last_name, interested_at = user
            username_display = f"@{username}" if username else "без username"
            name_display = f"{first_name} {last_name}" if last_name else first_name
            response += f"{i}. {username_display} ({name_display}) - {interested_at[:10]}\n"

        bot.reply_to(message, response)

    @bot.message_handler(commands=['paid'])
    def list_paid_users(message):
        """Список оплативших пользователей"""
        if not is_admin(message.from_user.id):
            return

        users = get_paid_users()
        if not users:
            bot.reply_to(message, "Нет оплативших пользователей.")
            return

        response = "💰 Оплатившие пользователи:\n\n"
        for i, user in enumerate(users, 1):
            user_id, username, first_name, last_name, paid_at = user
            username_display = f"@{username}" if username else "без username"
            name_display = f"{first_name} {last_name}" if last_name else first_name
            response += f"{i}. {username_display} ({name_display}) - {paid_at[:10]}\n"

        bot.reply_to(message, response)

    @bot.message_handler(commands=['history'])
    def show_message_history(message):
        """История сообщений с пользователем"""
        if not is_admin(message.from_user.id):
            return

        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Используйте: /history [user_id]")
            return

        try:
            user_id = int(parts[1])
            history = get_message_history(user_id)

            if not history:
                bot.reply_to(message, f"Нет истории сообщений с пользователем {user_id}.")
                return

            response = f"История сообщений с пользователем {user_id}:\n\n"
            for msg in history:
                sender_id, receiver_id, text, sent_at = msg
                direction = "→" if sender_id == user_id else "←"
                response += f"[{sent_at[:19]}] {direction} {text}\n\n"

            bot.reply_to(message, response[:4000])  # Ограничение на длину сообщения
        except ValueError:
            bot.reply_to(message, "Неверный формат user_id. Должно быть число.")

    @bot.message_handler(commands=['reply'])
    def admin_reply(message):
        """Ответ администратора пользователю"""
        if not is_admin(message.from_user.id):
            return

        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "Используйте: /reply [user_id] [сообщение]")
            return

        try:
            user_id = int(parts[1])
            reply_text = parts[2]

            # Сохраняем сообщение в базу
            add_message(message.from_user.id, user_id, reply_text)

            # Отправляем сообщение пользователю
            try:
                bot.send_message(user_id, f"Сообщение от администратора:\n\n{reply_text}")
                bot.reply_to(message, f"Сообщение пользователю {user_id} отправлено.")
            except Exception as e:
                bot.reply_to(message, f"Не удалось отправить сообщение: {str(e)}")
        except ValueError:
            bot.reply_to(message, "Неверный формат user_id. Должно быть число.")

    @bot.message_handler(func=lambda message: not message.text.startswith('/') and 
                                      is_admin(message.from_user.id) and 
                                      len(message.text.split()) > 1)
    def handle_admin_message(message):
        """Обработка сообщений от администраторов без команд"""
        # Если сообщение начинается с числа (предполагаемый user_id), считаем это ответом пользователю
        parts = message.text.split(maxsplit=1)
        try:
            user_id = int(parts[0])
            reply_text = parts[1]

            # Сохраняем сообщение в базу
            add_message(message.from_user.id, user_id, reply_text)

            # Отправляем сообщение пользователю
            try:
                bot.send_message(user_id, f"Сообщение от администратора:\n\n{reply_text}")
                bot.reply_to(message, f"Сообщение пользователю {user_id} отправлено.")
            except Exception as e:
                bot.reply_to(message, f"Не удалось отправить сообщение: {str(e)}")
        except (ValueError, IndexError):
            # Это не ответ пользователю, возможно, администратор просто пишет
            pass