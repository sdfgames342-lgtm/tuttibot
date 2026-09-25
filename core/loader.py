import os, importlib, logging, inspect
from core.help_generator import registrar_comando

logger = logging.getLogger(__name__)

def cargar_comandos(bot, salas=None, msg_queue=None, salas_lock=None):
    if salas is None:
        salas = {}
    comandos_path = os.path.join(os.path.dirname(__file__), '..', 'commands')
    archivos = []

    for root, dirs, files in os.walk(comandos_path):
        for f in files:
            if f.endswith('.py') and f != '__init__.py':
                rel_path = os.path.relpath(os.path.join(root, f), comandos_path)
                archivos.append(rel_path.replace(os.sep, '.')[:-3])

    cargados = 0
    for mod_name in archivos:
        try:
            modulo = importlib.import_module(f'commands.{mod_name}')
            funcs = [f for f in dir(modulo) if f.startswith('register_')]

            help_entries = getattr(modulo, 'HELP_COMMANDS', None)

            for f_name in funcs:
                func = getattr(modulo, f_name)
                if not callable(func):
                    continue
                sig = inspect.signature(func)
                params = sig.parameters

                # Solo llamamos a funciones que aceptan 'bot' como primer parámetro
                if 'bot' not in params:
                    continue

                disponibles = {
                    'bot': bot,
                    'register_command': lambda name: bot.message_handler(commands=[name]),
                    'register_callback': lambda pattern: bot.callback_query_handler(func=lambda call: call.data.startswith(pattern)),
                    'msg_queue': msg_queue,
                    'salas': salas,
                    'salas_lock': salas_lock,
                    'registrar_jugador': lambda *a: True,
                    'iniciar_juego_desde_grupo': lambda *a: True
                }
                kwargs = {k: v for k, v in disponibles.items() if k in params}
                func(**kwargs)

            # Registrar en el catálogo de ayuda
            if help_entries:
                for entry in help_entries:
                    cmd = entry['command']
                    if not cmd.startswith('/'):
                        cmd = '/' + cmd
                    registrar_comando(cmd, entry.get('desc_key', f'help.desc_{cmd[1:]}'),
                                      entry.get('sudo_level', 0),
                                      entry.get('category', _infer_category(mod_name)))

            cargados += 1
            logger.info(f"✅ SINCRONIZADO: {mod_name}")

        except Exception as e:
            logger.exception(f"❌ FALLO EN {mod_name}: {e}")

    logger.info(f"🚀 MAINFRAME OPERATIVO: {cargados} módulos listos.")

def _infer_category(mod_name):
    if 'admin' in mod_name or mod_name in ('broadcast', 'sizania', 'sponsor', 'config'):
        return 'admin'
    if mod_name in ('economia', 'itsunario', 'casino', 'otorgar'):
        return 'economia'
    if 'tuttifrutti' in mod_name or mod_name in ('create', 'unir', 'play', 'cagon', 'off', 'salir', 'spacing'):
        return 'juegos'
    if mod_name in ('about', 'profile', 'afinidad', 'user', 'lang', 'help'):
        return 'nodo'
    if 'montecarlo' in mod_name or mod_name in ('truco', 'pagos'):
        return 'montecarlo'
    if 'minigames' in mod_name:
        return 'minigames'
    return 'otros'
