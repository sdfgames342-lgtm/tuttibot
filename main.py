import telebot
import time
import logging
import queue
from core.bot import ItsukiBot
from core.db import inicializar_db
from core.loader import cargar_comandos
from core.kernel import start_kernel_threads
from utils.game_state import salas_lock
from utils.logger_telegram import TelegramAlertHandler
from game_core.registry import setup_bot_callbacks

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_mainframe():
    try:
        inicializar_db()
        bot = ItsukiBot().get_instance()
        msg_queue = queue.Queue()

        telegram_handler = TelegramAlertHandler(bot, msg_queue)
        telegram_handler.setLevel(logging.WARNING)
        logging.getLogger().addHandler(telegram_handler)

        salas = {}
        cargar_comandos(bot, salas=salas, msg_queue=msg_queue, salas_lock=salas_lock)
        setup_bot_callbacks(bot)

        logger.info("🚀 Itsuki Mainframe ONLINE")
        start_kernel_threads(bot, salas, salas_lock, msg_queue)
        bot.infinity_polling(timeout=20, long_polling_timeout=10, logger_level=logging.ERROR)
    except Exception as e:
        logger.critical(f"❌ Error fatal en el arranque: {e}")
        time.sleep(10)

if __name__ == "__main__":
    start_mainframe()
