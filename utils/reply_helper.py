import logging
import re

logger = logging.getLogger(__name__)

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

def safe_reply(bot, message, text, *args, **kwargs):
    kwargs.pop('raw', None)
    kwargs.pop('caption', None)
    parse_mode = kwargs.get('parse_mode', 'HTML')

    try:
        # Caso 1: message es un número (chat_id directo)
        if isinstance(message, int):
            return bot.send_message(message, text, *args, **kwargs)

        # Caso 2: message es objeto de Telegram (mensaje)
        if message is not None:
            try:
                return bot.reply_to(message, text, **kwargs)
            except Exception as reply_err:
                # Si falla la respuesta directa (mensaje eliminado), enviar al chat sin reply
                logger.warning(f"Fallo reply_to, enviando mensaje normal: {reply_err}")
                chat_id = message.chat.id if hasattr(message, 'chat') else message
                return bot.send_message(chat_id, text, *args, **kwargs)

        # Caso 3: sin message, se usa chat_id de kwargs
        chat_id = kwargs.pop('chat_id', None)
        if not chat_id and args:
            chat_id = args[0]
            args = args[1:]
        if chat_id:
            return bot.send_message(chat_id, text, *args, **kwargs)

    except Exception as e:
        if "parse_mode" in kwargs:
            logger.warning(f"Falla parse_mode ({kwargs['parse_mode']}). Reintentando texto plano...")
            kwargs.pop("parse_mode")
            clean_text = clean_html(text)
            return safe_reply(bot, message, clean_text, *args, **kwargs)
        logger.error(f"Error crítico en safe_reply: {e}")
        return None
