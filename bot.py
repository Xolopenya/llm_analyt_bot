import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN
from handlers.file_handler import handle_file, handle_text

# 🔥 Настройка логирования для Render
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    force=True
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Получена команда /start от %s", update.effective_user.id)
    await update.message.reply_text(
        "👋 Привет! Я AI-аналитик данных.\n\n"
        "📊 Отправьте мне CSV или Excel файл с запросом, и я:\n"
        "• Рассчитаю метрики\n"
        "• Построю графики\n"
        "• Найду инсайты"
    )


def main():
    logger.info("Запуск бота...")

    # Создаём приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Бот запущен, жду сообщения...")

    # 🔥 Запускаем polling (блокирует процесс, но это нормально для Render)
    # drop_pending_updates=True — игнорировать старые сообщения при старте
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == '__main__':
    main()