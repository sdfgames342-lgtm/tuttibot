import time, threading, logging
from core.db import (
    limpiar_ruleta_expirada, limpiar_duelo_expirado, liberar_libros_expirados
)

logger = logging.getLogger(__name__)

def iniciar_reaper(bot, msg_queue):
    def reaper_loop():
        while True:
            time.sleep(5)
            limpiar_ruleta_expirada()
            limpiar_duelo_expirado()
            liberar_libros_expirados()
    threading.Thread(target=reaper_loop, daemon=True).start()
