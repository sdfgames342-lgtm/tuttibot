"""
Elementos visuales, cabeceras, separadores y renderizado ledger.
(Históricamente llamado decorators.py; no contiene decoradores.)
"""
import html
from utils.formatters import to_itsuki_font, to_mono_font, wrap_text
from utils.message_styles import HTML_HEADER, SEPARATOR  # constantes canónicas

ACID_SEPARATOR = '━' * 15

class ItsukiLedger:
    @staticmethod
    def _safe(val):
        return html.escape(str(val))

    @staticmethod
    def render_solo_titulo(title_key, lang='es'):
        from utils.idiomas import obtener_texto
        return to_itsuki_font(obtener_texto(title_key, lang=lang))

    @staticmethod
    def render(title_key, body_lines, variables=None, lang='es', chat_id=None, user_id=None):
        from utils.idiomas import obtener_texto
        titulo = to_itsuki_font(obtener_texto(title_key, lang=lang, chat_id=chat_id, user_id=user_id))
        msg_parts = [HTML_HEADER, f'╭─ ⟪ {titulo} ⟫']
        for line_key in body_lines:
            raw_text = obtener_texto(line_key, lang=lang, chat_id=chat_id, user_id=user_id)
            for wrapped in wrap_text(raw_text):
                msg_parts.append(f'│ {to_mono_font(wrapped)}')
        msg_parts.append('│')
        if variables:
            for k, v in variables.items():
                if isinstance(v, str) and v.startswith('/'):
                    val_render = v
                else:
                    val_render = f'<code>{html.escape(str(v))}</code>'
                msg_parts.append(f'│ ⊛ {to_mono_font(k)}: {val_render}')
        msg_parts.append(SEPARATOR)
        return '\n'.join(msg_parts)

# ─── Constantes de frases estáticas → ahora se obtienen desde JSON ───
def obtener_frase_estatica(categoria, indice=0, lang='es'):
    """
    Reemplaza las antiguas FRASES_ESTATICAS y HELP_CATEGORIAS.
    Busca en los archivos de idioma la clave correspondiente.
    """
    from utils.idiomas import obtener_texto
    clave = f"frases.{categoria}.{indice}"
    return obtener_texto(clave, lang=lang)

def obtener_ayuda_categoria(categoria, lang='es'):
    from utils.idiomas import obtener_texto
    return obtener_texto(f"help.cat_{categoria}", lang=lang)

# Las siguientes constantes ahora son funciones o se cargan desde JSON.
# Se dejan como referencia para comandos antiguos, pero eventualmente se eliminarán.
HELP_TITULO_PRINCIPAL = 'Protocolos de Soporte • Selecciona una categoría'
PREMIUM_MENSAJE = '╔══════════════════════════════╗\n   🔒 **NÚCLEO RESTRINGIDO**\n╚══════════════════════════════╝\n\nTu rango actual no permite acceder a este sector...'
TOP_GLOBAL_LINE = '│ * Top Global: #<code>{pos}</code>'
