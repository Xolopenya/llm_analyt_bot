import os
import logging
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from config import TELEGRAM_BOT_TOKEN
from handlers.file_handler import handle_file, handle_text

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app на уровне модуля (нужно для gunicorn!)
app = Flask(__name__)


@app.route('/')
def home():
    return "LLM Analytics Bot работает!"


@app.route('/health')
def health():
    return "OK", 200


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я AI-аналитик данных.\n\n"
        "📊 Отправьте мне CSV или Excel файл с запросом одним сообщением, и я:\n"
        "• Рассчитаю метрики\n"
        "• Построю графики\n"
        "• Найду инсайты"
    )


def run_telegram_bot():
    """Запускает бота в отдельном потоке"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запуск в режиме polling (работает внутри контейнера)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    port = os.environ.get('PORT')

    if port:
        # Режим Render: запускаем бота в фоне + Flask сервер
        logger.info(f"Запуск на Render, порт {port}...")

        # Запускаем телеграм-бота в отдельном потоке
        bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        bot_thread.start()

        # Запускаем Flask сервер (gunicorn подключится сюда)
        app.run(host='0.0.0.0', port=int(port))
    else:
        # Локальный режим: просто polling
        logger.info("Запуск локально...")
        run_telegram_bot()


if __name__ == '__main__':
    main()