"""Registro global de partidas activas."""
import logging
from threading import RLock

logger = logging.getLogger(__name__)

active_games = {}          # chat_id -> GameSession instance
lock = RLock()

def register_game(chat_id, game):
    with lock:
        active_games[str(chat_id)] = game

def unregister_game(chat_id):
    with lock:
        active_games.pop(str(chat_id), None)

def get_game(chat_id):
    with lock:
        return active_games.get(str(chat_id))

# ─── Callback global para juegos ───
def setup_bot_callbacks(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith('game_'))
    def game_callback(call):
        # Formato: game_<chat_id>_<player_id>_<action>_<data>
        parts = call.data.split('_', 4)  # game, chat_id, player_id, action, data
        if len(parts) < 4:
            return bot.answer_callback_query(call.id, 'Datos inválidos')
        chat_id = parts[1]
        player_id = int(parts[2])
        action = parts[3]
        data = parts[4] if len(parts) > 4 else ''
        game = get_game(chat_id)
        if game is None:
            return bot.answer_callback_query(call.id, 'Partida no encontrada')
        if call.from_user.id != player_id:
            return bot.answer_callback_query(call.id, 'No es tu turno')
        # Delegar
        try:
            game.handle_callback(call, action, data)
        except Exception as e:
            logger.exception(f'Error manejando callback de juego: {e}')
            bot.answer_callback_query(call.id, f'Error: {e}')
