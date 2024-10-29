import sys
import os
import logging
import asyncio
import psutil  # Для мониторинга состояния ПК
import GPUtil  # Для получения информации о видеокарте
import pyautogui  # Для захвата экрана
from io import BytesIO  # Для работы с байтовыми потоками
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal

# Установите уровень логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Укажите токен вашего бота
TOKEN = 'Ваш токен'  # Замените на ваш токен

# Задайте пароль
PASSWORD = 'Ваш пароль'  # Замените на ваш пароль

# Замените на ваш Telegram ID
ALLOWED_USER_ID = Ваш id  # Ваш Telegram ID

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
            await update.message.reply_text("Пароль принят! Теперь вы можете использовать команды /shutdown, /timer_shutdown, /status, /screenshot и /help.")
        else:
            await update.message.reply_text("Неверный пароль. Попробуйте снова.")
    else:
        await update.message.reply_text("Вы не мой владелец.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    commands = (
        "/start - начать взаимодействие с ботом\n"
        "/shutdown - выключить компьютер через 5 секунд\n"
        "/timer_shutdown <seconds> - выключить компьютер через указанное количество секунд\n"
        "/status - получить статус системы\n"
        "/screenshot - получить скриншот экрана\n"
        "/reset - сбросить статус авторизации\n"
        "/help - получить список доступных команд"
    )
    await context.bot.send_message(chat_id=user_id, text=commands)

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_authenticated.get(user_id, False):
        await context.bot.send_message(chat_id=user_id, text="Компьютер выключается через 5 секунд...")
        await asyncio.sleep(5)  # Задержка 5 секунд
        os.system('shutdown /s /t 0')
        await context.bot.send_message(chat_id=user_id, text="Компьютер выключился.")
    else:
        await context.bot.send_message(chat_id=user_id, text="Вы не авторизованы для использования этой команды. Пожалуйста, введите пароль с помощью команды /start.")

async def timer_shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_authenticated.get(user_id, False):
        if context.args and context.args[0].isdigit():
            delay = int(context.args[0])
            await context.bot.send_message(chat_id=user_id, text=f"Компьютер будет выключен через {delay} секунд...")
            await asyncio.sleep(delay)  # Задержка в заданное время
            os.system('shutdown /s /t 0')
            await context.bot.send_message(chat_id=user_id, text="Компьютер выключился.")
        else:
            await context.bot.send_message(chat_id=user_id, text="Пожалуйста, укажите время в секундах.")
    else:
        await context.bot.send_message(chat_id=user_id, text="Вы не авторизованы для использования этой команды. Пожалуйста, введите пароль с помощью команды /start.")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id == ALLOWED_USER_ID:
        user_authenticated[user_id] = False
        await update.message.reply_text("Статус авторизации сброшен. Введите пароль снова для доступа.")
    else:
        await update.message.reply_text("Вы не мой владелец.")

async def system_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_authenticated.get(user_id, False):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        gpu_info = GPUtil.getGPUs()
        
        gpu_usage = gpu_info[0].load * 100 if gpu_info else 0
        gpu_temp = gpu_info[0].temperature if gpu_info else "N/A"
        
        status_message = (
            f"Загрузка ЦП: {cpu_usage}%\n"
            f"Использование ОЗУ: {memory_info.percent}%\n"
            f"Загрузка ГП: {gpu_usage}%\n"
            f"Температура ГП: {gpu_temp}°C"
        )
        await context.bot.send_message(chat_id=user_id, text=status_message)
    else:
        await context.bot.send_message(chat_id=user_id, text="Вы не авторизованы для использования этой команды. Пожалуйста, введите пароль с помощью команды /start.")

async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_authenticated.get(user_id, False):
        # Захватываем скриншот
        screenshot = pyautogui.screenshot()
        
        # Сохраняем скриншот в байтовом потоке
        bio = BytesIO()
        screenshot.save(bio, format='PNG')
        bio.seek(0)  # Перемещаем указатель в начало потока
        
        # Отправляем скриншот пользователю
        await context.bot.send_photo(chat_id=user_id, photo=bio)
    else:
        await context.bot.send_message(chat_id=user_id, text="Вы не авторизованы для использования этой команды. Пожалуйста, введите пароль с помощью команды /start.")

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики команд
    start_handler = CommandHandler('start', start)
    shutdown_handler = CommandHandler('shutdown', shutdown)
    timer_shutdown_handler = CommandHandler('timer_shutdown', timer_shutdown)
    reset_handler = CommandHandler('reset', reset)
    system_status_handler = CommandHandler('status', system_status)
    screenshot_handler = CommandHandler('screenshot', screenshot)  # Команда для скриншота
    help_handler = CommandHandler('help', help_command)  # Новая команда для помощи
    password_message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler)

    app.add_handler(start_handler)
    app.add_handler(shutdown_handler)
    app.add_handler(timer_shutdown_handler)
    app.add_handler(reset_handler)
    app.add_handler(system_status_handler)
    app.add_handler(screenshot_handler)  # Регистрация команды скриншота
    app.add_handler(help_handler)  # Регистрация команды помощи
    app.add_handler(password_message_handler)

    loop.run_until_complete(app.run_polling())

class BotThread(QThread):
    finished = pyqtSignal()  # Сигнал, который будет отправлен при завершении потока

    def run(self):
        start_bot()  # Запускаем бота
        self.finished.emit()  # Сообщаем, что поток завершился

def run_gui():
    app = QApplication(sys.argv)

    # Определите путь к иконке
    base_path = os.path.dirname(__file__)
    icon_path = os.path.join(base_path, 'icon.png')  # Иконка в той же папке, что и скрипт

    icon = QIcon(icon_path)  # Замените на путь к вашему файлу PNG
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