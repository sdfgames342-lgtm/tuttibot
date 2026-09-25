"""Clase base para cualquier juego por turnos con privacidad."""
import logging
from abc import ABC, abstractmethod
from telebot import types
from game_core.registry import register_game, unregister_game

logger = logging.getLogger(__name__)

class GameSession(ABC):
    def __init__(self, bot, chat_id, players, apuesta=None):
        self.bot = bot
        self.chat_id = str(chat_id)
        self.players = players          # lista de user_id
        self.apuesta = apuesta
        self.state = 'waiting_join'     # waiting_join, playing, finished
        self.private_msgs = {}          # user_id -> message_id (privado)
        self.public_msg_id = None
        self.turn = None                # índice en players
        self.registered = False

    def start(self):
        """Iniciar partida. Se llama cuando todos los jugadores están listos."""
        self.state = 'playing'
        self.turn = 0
        self._set_public_message()
        self._update_public()
        self._notify_current_turn()
        register_game(self.chat_id, self)
        self.registered = True

    @abstractmethod
    def handle_callback(self, call, action, data):
        """Procesa un callback de un botón privado. action y data vienen del callback."""
        pass

    @abstractmethod
    def get_private_view(self, user_id):
        """Retorna (texto, markup) que se enviará al jugador en privado."""
        pass

    @abstractmethod
    def get_public_view(self):
        """Retorna texto que se muestra en el grupo (estado de la partida)."""
        pass

    def _send_private_message(self, user_id):
        """Envía o edita el mensaje privado del jugador con su vista actual."""
        text, markup = self.get_private_view(user_id)
        if user_id in self.private_msgs:
            try:
                self.bot.edit_message_text(
                    chat_id=user_id,
                    message_id=self.private_msgs[user_id],
                    text=text,
                    reply_markup=markup,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.warning(f"No se pudo editar mensaje privado para {user_id}: {e}")
                # enviar nuevo
                self._send_new_private(user_id, text, markup)
        else:
            self._send_new_private(user_id, text, markup)

    def _send_new_private(self, user_id, text, markup):
        try:
            msg = self.bot.send_message(user_id, text, reply_markup=markup, parse_mode='HTML')
            self.private_msgs[user_id] = msg.message_id
        except Exception as e:
            logger.error(f"No se pudo enviar privado a {user_id}: {e}")

    def _set_public_message(self):
        """Envía el mensaje público inicial y lo guarda."""
        text = self.get_public_view()
        msg = self.bot.send_message(self.chat_id, text, parse_mode='HTML')
        self.public_msg_id = msg.message_id

    def _update_public(self):
        """Edita el mensaje público con el estado actual."""
        if not self.public_msg_id:
            return
        try:
            self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.public_msg_id,
                text=self.get_public_view(),
                parse_mode='HTML'
            )
        except Exception as e:
            logger.warning(f"No se pudo editar mensaje público: {e}")

    def _notify_current_turn(self):
        """Envía mensaje privado al jugador del turno actual."""
        if self.turn is not None and self.state == 'playing':
            uid = self.players[self.turn]
            self._send_private_message(uid)

    def _next_turn(self):
        """Avanza al siguiente jugador y notifica."""
        self.turn = (self.turn + 1) % len(self.players)
        self._notify_current_turn()
        self._update_public()

    def end_game(self, winner=None, results=None):
        """Finaliza la partida, reparte premios si hay apuesta."""
        self.state = 'finished'
        unregister_game(self.chat_id)
        self.registered = False
        # Notificar
        self._update_public()
        # Reparto de fichas (se implementa en subclase si es necesario)
        self.on_game_over(winner, results)

    @abstractmethod
    def on_game_over(self, winner, results):
        """Lógica de premios."""
        pass

    def abandon(self, user_id):
        """Jugador abandona. La subclase decide cómo manejarlo."""
        pass

    def cancel(self, user_id):
        """Administrador cancela la partida."""
        pass
