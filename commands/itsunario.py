"""Comando /itsunario – consulta de saldo, canje y venta de fichas."""
from utils.reply_helper import safe_reply
from utils.idiomas import obtener_texto
from core.db import obtener_saldo_itsunario, canjear_tokens_por_fichas, vender_fichas_por_tokens
import logging

logger = logging.getLogger(__name__)

HELP_COMMANDS = [
    {"command": "/itsunario", "desc_key": "help.desc_itsunario", "sudo_level": 0, "category": "economia"}
]

def register_itsunario_handlers(bot, register_command=None):

    @bot.message_handler(commands=['itsunario'])
    def itsunario_cmd(message):
        parts = message.text.split()
        uid = message.from_user.id
        tokens, fichas = obtener_saldo_itsunario(uid)

        if len(parts) == 1:
            msg = (
                f"💰 <b>ITSUNARIO</b>\n"
                f"Tokens: {tokens}\n"
                f"Fichas: {fichas}\n\n"
                f"Usá /itsunario canjear <tokens> para cambiar tokens por fichas.\n"
                f"Usá /itsunario vender <fichas> para obtener tokens."
            )
            return safe_reply(bot, message, msg, parse_mode='HTML')

        if len(parts) >= 3:
            accion = parts[1].lower()
            try:
                cantidad = int(parts[2])
                if cantidad <= 0: raise ValueError
            except ValueError:
                return safe_reply(bot, message, obtener_texto('itsunario.cantidad_invalida'))

            if accion == 'canjear':
                exito, resultado = canjear_tokens_por_fichas(uid, cantidad)
                if exito:
                    msg = obtener_texto('itsunario.canje_exito').format(cantidad=cantidad, fichas=resultado)
                else:
                    msg = f"❌ {resultado}"
                return safe_reply(bot, message, msg)

            elif accion == 'vender':
                exito, resultado = vender_fichas_por_tokens(uid, cantidad)
                if exito:
                    msg = obtener_texto('itsunario.venta_exito').format(fichas=cantidad, tokens=resultado)
                else:
                    msg = f"❌ {resultado}"
                return safe_reply(bot, message, msg)

        return safe_reply(bot, message, "Uso: /itsunario [canjear <tokens>|vender <fichas>]")
