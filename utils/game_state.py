"""Estado global de las salas: lock reentrante y función unificada de estado."""
import threading
salas_lock = threading.RLock()

def sala_activa(sala: dict) -> bool:
    """True si la sala no está en ESPERA."""
    if not sala:
        return False
    return sala.get('estado') != 'ESPERA'