import os
import logging
import threading
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from config import TELEGRAM_BOT_TOKEN
from handlers.file_handler import handle_file, handle_text

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    force=True  # 🔥 Важно для Render
)
logger = logging.getLogger(__name__)

# Flask app на уровне модуля
app = Flask(__name__)


@app.route('/')
def home():
    return "LLM Analytics Bot работает!"


@app.route('/health')
def health():
    return "OK", 200


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Получена команда /start")
    await update.message.reply_text(
        "👋 Привет! Я AI-аналитик данных.\n\n"
        "📊 Отправьте мне CSV или Excel файл с запросом одним сообщением, и я:\n"
        "• Рассчитаю метрики\n"
        "• Построю графики\n"
        "• Найду инсайты"
    )


def run_telegram_bot():
    """Запускает бота с повторными попытками"""
    logger.info("Запуск Telegram бота...")

    while True:
        try:
            application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
            application.add_handler(CommandHandler("start", start))
            application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

            logger.info("Бот запущен, слушаю обновления...")
            # run_polling блокирует поток, но мы в while True, так что при ошибке перезапустим
            application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

        except Exception as e:
            logger.error(f"Ошибка бота: {e}", exc_info=True)
            logger.info("🔄 Перезапуск бота через 5 секунд...")
            time.sleep(5)  # Ждём перед перезапуском


def main():
    port = os.environ.get('PORT')
    logger.info(f"Запуск приложения (PORT={port})")

    # 🔥 Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=False)
    bot_thread.start()
    logger.info("🧵 Поток бота запущен")

    if port:
        # Render: запускаем Flask
        logger.info(f"🌐 Запуск Flask на порту {port}")
        app.run(host='0.0.0.0', port=int(port))
    else:
        # Локально: просто ждём
        logger.info("Локальный режим, бот работает в фоне")
        while True:
            time.sleep(60)


if __name__ == '__main__':
    main()