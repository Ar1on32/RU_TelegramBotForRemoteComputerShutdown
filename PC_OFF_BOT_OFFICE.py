import sys
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QObject

# Установите уровень логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Укажите токен вашего бота
TOKEN = 'ВАШ ТОКЕН'  # Замените на ваш токен

# Задайте пароль
PASSWORD = 'ваш_пароль'  # Замените на ваш пароль

# Замените на ваш Telegram ID
ALLOWED_USER_ID =  id # Ваш Telegram ID

# Хранение статуса авторизации пользователя
user_authenticated = {}

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super(SystemTrayIcon, self).__init__(icon, parent)
        menu = QMenu(parent)
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.exit)
        self.setContextMenu(menu)
        self.setVisible(True)

    def exit(self):
        QApplication.quit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id == ALLOWED_USER_ID:
        await update.message.reply_text("Введите пароль для доступа к командам бота:")
    else:
        await update.message.reply_text("Вы не мой владелец.")

async def password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id == ALLOWED_USER_ID:
        if update.message.text == PASSWORD:
            user_authenticated[user_id] = True
            await update.message.reply_text("Пароль принят! Теперь вы можете использовать команду /shutdown.")
        else:
            await update.message.reply_text("Неверный пароль. Попробуйте снова.")
    else:
        await update.message.reply_text("Вы не мой владелец.")

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_authenticated.get(user_id, False):
        await context.bot.send_message(chat_id=user_id, text="Компьютер выключается через 5 секунд...")
        await asyncio.sleep(5)  # Задержка 5 секунд
        os.system('shutdown /s /t 0')
        await context.bot.send_message(chat_id=user_id, text="Компьютер выключился.")
    else:
        await context.bot.send_message(chat_id=user_id, text="Вы не авторизованы для использования этой команды. Пожалуйста, введите пароль с помощью команды /start.")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id == ALLOWED_USER_ID:
        user_authenticated[user_id] = False
        await update.message.reply_text("Статус авторизации сброшен. Введите пароль снова для доступа.")
    else:
        await update.message.reply_text("Вы не мой владелец.")

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики команд
    start_handler = CommandHandler('start', start)
    shutdown_handler = CommandHandler('shutdown', shutdown)
    reset_handler = CommandHandler('reset', reset)
    password_message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler)

    app.add_handler(start_handler)
    app.add_handler(shutdown_handler)
    app.add_handler(reset_handler)
    app.add_handler(password_message_handler)

    loop.run_until_complete(app.run_polling())

class BotThread(QThread):
    finished = pyqtSignal()  # Сигнал, который будет отправлен при завершении потока

    def run(self):
        start_bot()  # Запускаем бота
        self.finished.emit()  # Сообщаем, что поток завершился

def run_gui():
    app = QApplication(sys.argv)
    icon = QIcon("ВАШ ПУТЬ К ИЗОБРАЖЕНИЮ.png")  # Замените на путь к вашему файлу PNG
    tray_icon = SystemTrayIcon(icon)

    # Показываем иконку в системном трее
    tray_icon.show()

    # Запускаем бота в отдельном потоке
    bot_thread = BotThread()
    bot_thread.finished.connect(lambda: logging.info("Bot thread finished."))  # Логируем завершение потока
    bot_thread.start()

    # Запускаем цикл событий PyQt
    app.exec_()

if __name__ == "__main__":
    run_gui()
