from itsuki_engine import ItsukiCore
from utils.idiomas import obtener_idioma_chat
from core.db import get_sudo_level
from commands.spacing import programar_repaso, obtener_palabras_para_revisar
import random
itsuki = ItsukiCore()

HELP_COMMANDS = [
    {"command": "/frase", "desc_key": "help.desc_frase", "sudo_level": 0, "category": "otros"},
    {"command": "/revisar", "desc_key": "help.desc_revisar", "sudo_level": 0, "category": "otros"}
]


def register_handlers(bot, register_command=None, msg_queue=None):
    if register_command is None:
        def register_command(name):
            def decorator(f): return f
            return decorator
    if msg_queue is None:
        class DummyQueue:
            def put(self, fn, *args, **kwargs): return fn(*args, **kwargs)
        msg_queue = DummyQueue()


    @register_command('frase')
    def frase_cmd(message):
        chat_id = str(message.chat.id)
        idioma = obtener_idioma_chat(chat_id)[:2]
        nivel = get_sudo_level(message.from_user.id) % 3 + 1
        itsuki.idioma = idioma
        itsuki.nivel = nivel
        frase = itsuki.generar_frase()
        semilla = itsuki.semillas.get(nivel, [201, 202, 203])
        ids = itsuki.expandir(semilla)
        if message.from_user.id:
            try:
                programar_repaso(message.from_user.id, ids)
            except:
                pass
        msg_queue.put(bot.reply_to, message, frase)

    @register_command('revisar')
    def revisar_cmd(message):
        user_id = message.from_user.id
        pendientes = obtener_palabras_para_revisar(user_id)
        if not pendientes:
            return msg_queue.put(bot.reply_to, message, obtener_texto('hardcoded.revisar_sin_palabras'))
        muestra = random.sample(pendientes, min(3, len(pendientes)))
        with open('lexico.json', 'r') as f:
            lex = json.load(f)
        chat_id = str(message.chat.id)
        idioma = obtener_idioma_chat(chat_id)[:2]
        repaso = []
        for pid in muestra:
            entrada = lex.get(str(pid), {})
            palabra = entrada.get(idioma, entrada.get('es', f'ID:{pid}'))
            repaso.append(f'→ {palabra}')
        msg = '📚 **Palabras para repasar:**\n' + '\n'.join(repaso)
        msg_queue.put(bot.reply_to, message, msg, parse_mode='Markdown')