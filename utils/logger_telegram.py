"""
Telemetry Handler – envía eventos WARNING o superiores al canal de logs
y limita el archivo local a solo la sesión actual.
"""
import logging
from core.db import get_config

class TelegramAlertHandler(logging.Handler):
    """Envía logs de nivel WARNING o superior al canal de Telegram usando msg_queue."""

    def __init__(self, bot, msg_queue):
        super().__init__(level=logging.WARNING)
        self.bot = bot
        self.msg_queue = msg_queue

    def emit(self, record):
        try:
            canal = get_config('canal_logs')
            if not canal:
                return
            msg = self.format(record)
            if len(msg) > 4000:
                msg = msg[:4000] + '…[truncado]'
            emoji = '⚠️' if record.levelno == logging.WARNING else '🚨'
            texto = f'{emoji} [SISTEMA LOG]\n{msg}'
            self.msg_queue.put(self.bot.send_message, canal, texto, raw=True)
        except Exception:
            pass