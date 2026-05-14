import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN
from handlers.file_handler import handle_file, handle_text

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я AI-аналитик данных.\n\n"
        "📊 Отправьте мне CSV или Excel файл с запросом одним сообщением, и я:\n"
        "• Рассчитаю метрики\n"
        "• Построю графики\n"
        "• Найду инсайты"
    )


def main():
    # Для Render: используем PORT из переменных окружения (если есть)
    # Для локального запуска: polling
    port = os.environ.get('PORT')

    if port:
        # запуск как webhook
        logger.info(f"Запуск бота на порту {port}...")
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

        # простой веб-сервер для health checks
        from flask import Flask
        app = Flask(__name__)

        @app.route('/')
        def home():
            return "🤖 Бот работает!"

        @app.route('/health')
        def health():
            return "OK", 200

        import threading
        def run_bot():
            application.run_webhook(
                listen='0.0.0.0',
                port=int(port),
                url_path=TELEGRAM_BOT_TOKEN,
                webhook_url=f'https://{os.environ.get("RENDER_EXTERNAL_HOSTNAME", "localhost")}:{port}/{TELEGRAM_BOT_TOKEN}'
            )

        bot_thread = threading.Thread(target=run_bot)
        bot_thread.start()

        app.run(host='0.0.0.0', port=int(port))
    else:
        # Локальный запуск (polling)
        logger.info("Бот запущен (локальный режим)...")
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()