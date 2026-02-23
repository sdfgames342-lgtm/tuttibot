# core_game.py
def procesar_jugada(user_id, texto):
    if texto.lower() == "hola":
        return "👋 Hola jugador."
    
    return "🤔 No entendí tu jugada."
