import logging, time
from core.db import registrar_jugador, grupo_activo

logger = logging.getLogger(__name__)

HELP_COMMANDS = [
    {"command": "/create", "desc_key": "help.desc_create", "sudo_level": 0, "category": "juegos"}
]

def register_create_command(bot, register_command=None, salas=None, salas_lock=None):
    if salas is None:
        return

    @bot.message_handler(commands=['create'])
    def crear_tutti(message):
        chat_id = str(message.chat.id)
        user_id = message.from_user.id

        if not grupo_activo(chat_id):
            from core.db import activar_grupo
            activar_grupo(chat_id)

        with salas_lock:
            if chat_id in salas:
                bot.reply_to(message, "Ya hay una partida en curso en este grupo.")
                return
            # Crear nueva sala
            salas[chat_id] = {
                'estado': 'ESPERA',
                'creador': user_id,
                'jugadores': {user_id: message.from_user.first_name},
                'categorias': ['Animales', 'Países', 'Colores', 'Frutas', 'Profesiones'],
                'letra': None,
                'ronda': 0,
                'inicio_epoch': None,
                'bloques_procesados': 0,
                'start_message_id': None
            }
            registrar_jugador(user_id, message.from_user.first_name)
        bot.reply_to(message, f"📝 Sala Tutti‑Frutti creada. ¡Usen /unir para entrar!")
