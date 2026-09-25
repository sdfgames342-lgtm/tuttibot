"""Genera botoneras de ayuda dinámicas. El loader alimenta el catálogo."""
import logging
from core.db import get_sudo_level
from utils.idiomas import obtener_texto

logger = logging.getLogger(__name__)

SUDO_OWNER = 4
SUDO_COOWNER = 3
SUDO_ADMIN = 2
SUDO_MOD = 1

# Catálogo global { '/comando': {'desc_key':..., 'sudo_level':..., 'category':...} }
_catalogo = {}

def registrar_comando(cmd, desc_key, sudo_level=0, category='otros'):
    """Llamado por loader al cargar cada comando."""
    if not cmd.startswith('/'):
        cmd = '/' + cmd
    _catalogo[cmd] = {
        'desc_key': desc_key,
        'sudo_level': sudo_level,
        'category': category
    }

def generar_menu(user_id, lang='es'):
    nivel = get_sudo_level(user_id)
    categorias = {}
    for cmd, info in _catalogo.items():
        if nivel >= info['sudo_level']:
            cat = info['category']
            if cat not in categorias:
                categorias[cat] = {
                    'emoji': _emoji_por_categoria(cat),
                    'label': obtener_texto(f'help.cat_{cat}', lang=lang),
                    'comandos': []
                }
            categorias[cat]['comandos'].append(cmd)
    return categorias

def _emoji_por_categoria(cat):
    return {
        'nodo': '🛠️',
        'juegos': '🎮',
        'montecarlo': '♤',
        'minigames': '🎲',
        'economia': '💰',
        'admin': '🛡️',
    }.get(cat, '📌')
