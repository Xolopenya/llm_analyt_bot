import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# используем Qwen через OpenRouter
MODEL_NAME = "qwen/qwen-2.5-72b-instruct"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# настройки
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 МБ
SUPPORTED_EXTENSIONS = ('.csv', '.xlsx', '.xls')
WORK_DIR = "temp_analysis"