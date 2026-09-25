"""Obtiene y guarda file_id de imágenes configuradas por /setimg."""
from core.db import get_config, set_config

def obtener_imagen(tipo: str):
    """Retorna el file_id guardado para el tipo de imagen, o None."""
    return get_config(f'img_{tipo}')

def guardar_imagen(tipo: str, file_id: str):
    """Guarda el file_id en la configuración."""
    set_config(f'img_{tipo}', file_id)