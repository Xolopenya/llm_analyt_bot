import os
import sys
import glob
import subprocess
import logging

logger = logging.getLogger(__name__)


def run_code_safely(code: str, work_dir: str) -> dict:
    try:
        # устанавливаем кодировку UTF-8 для subprocess
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=work_dir,
            timeout=60,
            env=env,
            encoding='utf-8',
            errors='replace'  # заменяем проблемные символы вместо падения
        )

        plots = glob.glob(os.path.join(work_dir, "plot_*.png"))
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "plots": plots,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Превышено время (60 сек).", "plots": [], "returncode": 1}
    except Exception as e:
        return {"stdout": "", "stderr": f"Ошибка: {str(e)}", "plots": [], "returncode": 1}