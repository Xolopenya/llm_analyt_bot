import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import MAX_FILE_SIZE, SUPPORTED_EXTENSIONS
from services.llm_service import analyze_data

logger = logging.getLogger(__name__)


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()

    if file.file_size > MAX_FILE_SIZE:
        await update.message.reply_text("Файл слишком большой (макс. 15 МБ).")
        return

    ext = os.path.splitext(file.file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        await update.message.reply_text("Поддерживаются только .csv, .xlsx, .xls")
        return

    local_path = f"uploads/{file.file_unique_id}{ext}"
    os.makedirs("uploads", exist_ok=True)
    await file.download_to_drive(local_path)

    await update.message.reply_text("Файл получен. Запускаю анализ... Это может занять время.")

    user_context = ""
    if update.message.caption:
        user_context = update.message.caption
    elif context.user_data.get("last_text"):
        user_context = context.user_data["last_text"]

    try:
        report_text, plots = await analyze_data(local_path, user_context)

        # экранируем MD символы
        safe_text = report_text.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`').replace('[', '\\[').replace(
            ']', '\\]').replace('(', '\\(').replace(')', '\\)')

        await update.message.reply_text(safe_text)

        for plot_path in plots:
            if os.path.exists(plot_path):
                await update.message.reply_photo(photo=open(plot_path, "rb"))

    except Exception as e:
        logger.error(f"Ошибка анализа: {e}")
        await update.message.reply_text(f"Ошибка: {str(e)}")
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_text"] = update.message.text
    await update.message.reply_text("Теперь отправьте файл для анализа.")