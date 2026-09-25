"""Función de estilo directa para mensajes Itsuki."""
from utils.formatters import to_mono_font

HTML_HEADER = f"❧ {to_mono_font('Itsuki')} 🌷"
ACID_SEPARATOR = '━' * 15
SEPARATOR = ACID_SEPARATOR

def itsuki_msg(text, style='standard'):
    """Construye un mensaje con cabecera Itsuki."""
    header = HTML_HEADER
    # Ya NO aplicamos to_mono_font al texto, solo al header
    if style == 'acid':
        return f"{header}\n❗ {text}\n{ACID_SEPARATOR}"
    return f'{header}\n{text}'
