"""Truco Argentino – Reglamento completo con GameSession + botón e imagen."""
import random, logging
from telebot import types
from game_core.session import GameSession
from game_core.registry import register_game, get_game
from commands.montecarlo.cartas import (
    mazo_truco_db, calcular_envido, valor_truco, enviar_carta
)
from utils.imagenes import obtener_imagen
from utils.reply_helper import safe_reply
from utils.idiomas import obtener_texto

logger = logging.getLogger(__name__)

HELP_COMMANDS = [
    {"command": "/truco", "desc_key": "help.desc_truco", "sudo_level": 0, "category": "montecarlo"}
]

class TrucoSession(GameSession):
    def __init__(self, bot, chat_id, creator_id, num_jugadores, apuesta):
        super().__init__(bot, chat_id, [creator_id], apuesta)
        self.num_jugadores = num_jugadores
        self.creator = creator_id
        self.mazo = []
        self.cartas = {}
        self.ronda = 1
        self.ronda_cartas = []
        self.parejas = [[], []]
        self.puntos = [0, 0]
        self.mano_idx = 0
        self.ganadas_mano = [0, 0]
        self.envido_cantado = False
        self.envido_pendiente = None
        self.truco_pendiente = None
        self.fase = "envido"
        self.turno_actual = 0

    def unirse(self, user_id):
        if self.state != 'waiting_join' or len(self.players) >= self.num_jugadores:
            return
        if user_id not in self.players:
            self.players.append(user_id)
            self.bot.send_message(self.chat_id, f"✅ <b>{user_id}</b> se ha unido. ({len(self.players)}/{self.num_jugadores})", parse_mode='HTML')
            if len(self.players) == self.num_jugadores:
                self._formar_equipos()
                self.start()

    def _formar_equipos(self):
        j = self.players
        if self.num_jugadores == 2:
            self.parejas = [[j[0]], [j[1]]]
        elif self.num_jugadores == 4:
            self.parejas = [[j[0], j[2]], [j[1], j[3]]]
        elif self.num_jugadores == 6:
            self.parejas = [[j[0], j[2], j[4]], [j[1], j[3], j[5]]]

    def start(self):
        if self.apuesta:
            from core.db import sumar_itsunario
            for uid in self.players:
                sumar_itsunario(uid, tokens=0, fichas=-self.apuesta)
        self.mazo = mazo_truco_db()
        random.shuffle(self.mazo)
        for uid in self.players:
            self.cartas[uid] = [self.mazo.pop() for _ in range(3)]
        self.mano_idx = random.randint(0, len(self.players)-1)
        self.turno_actual = self.mano_idx
        self.fase = "envido"
        self.envido_cantado = False
        self.envido_pendiente = None
        self.truco_pendiente = None
        super().start()
        self._notify_all_players()
        self._update_public()

    def _pareja_de(self, uid):
        return 0 if uid in self.parejas[0] else 1

    def get_private_view(self, user_id):
        if self.state == 'finished':
            return "Partida finalizada.", None
        if self.state == 'waiting_join':
            return f"Esperando jugadores ({len(self.players)}/{self.num_jugadores}).", None
        if user_id not in self.cartas or not self.cartas[user_id]:
            return "No te quedan cartas.", None
        mano = self.cartas[user_id]
        texto = "🃏 Tus cartas:\n" + "\n".join(f"• {c}" for c in mano) + "\n\nEnvido: " + str(calcular_envido(mano))
        markup = types.InlineKeyboardMarkup(row_width=2)
        es_mi_turno = (self.players[self.turno_actual] == user_id)
        if self.fase == "envido":
            if es_mi_turno:
                markup.add(types.InlineKeyboardButton("Envido", callback_data=f'game_{self.chat_id}_{user_id}_envido_call_envido'),
                           types.InlineKeyboardButton("Real Envido", callback_data=f'game_{self.chat_id}_{user_id}_envido_call_realenvido'),
                           types.InlineKeyboardButton("Falta Envido", callback_data=f'game_{self.chat_id}_{user_id}_envido_call_falta'))
                for carta in mano:
                    markup.add(types.InlineKeyboardButton(carta, callback_data=f'game_{self.chat_id}_{user_id}_play_{carta}'))
        elif self.fase == "juego":
            if es_mi_turno:
                markup.add(types.InlineKeyboardButton("Truco", callback_data=f'game_{self.chat_id}_{user_id}_truco_call'))
                for carta in mano:
                    markup.add(types.InlineKeyboardButton(carta, callback_data=f'game_{self.chat_id}_{user_id}_play_{carta}'))
            else:
                if self.truco_pendiente and self.truco_pendiente['cantante'] != user_id:
                    markup.add(types.InlineKeyboardButton("Quiero", callback_data=f'game_{self.chat_id}_{user_id}_truco_quiero'),
                               types.InlineKeyboardButton("No Quiero", callback_data=f'game_{self.chat_id}_{user_id}_truco_noquiero'))
        elif self.fase == "envido_pendiente":
            if self.envido_pendiente and self.envido_pendiente['cantante'] != user_id:
                markup.add(types.InlineKeyboardButton("Quiero", callback_data=f'game_{self.chat_id}_{user_id}_envido_quiero'),
                           types.InlineKeyboardButton("No Quiero", callback_data=f'game_{self.chat_id}_{user_id}_envido_noquiero'),
                           types.InlineKeyboardButton("Son Buenas", callback_data=f'game_{self.chat_id}_{user_id}_envido_sonbuenas'))
        return texto, markup

    def get_public_view(self):
        if self.state == 'waiting_join':
            return f"🃏 Truco ({self.num_jugadores} jugadores) | Apuesta: {self.apuesta} fichas\nUsen /unirse_truco para entrar."
        if self.state == 'playing':
            current = self.players[self.turno_actual]
            return f"Turno de {current}\nPuntos: {self.puntos[0]} - {self.puntos[1]}"
        return "Partida finalizada."

    def handle_callback(self, call, action, data):
        if action == 'play':
            self._handle_play(call, data)
        elif action.startswith('envido_'):
            self._handle_envido(call, action, data)
        elif action.startswith('truco_'):
            self._handle_truco(call, action, data)
        else:
            self.bot.answer_callback_query(call.id, 'Acción no válida')

    def _handle_play(self, call, carta):
        uid = call.from_user.id
        if uid not in self.players or uid not in self.cartas or carta not in self.cartas[uid]:
            return self.bot.answer_callback_query(call.id, 'Carta no válida')
        if uid != self.players[self.turno_actual]:
            return self.bot.answer_callback_query(call.id, 'No es tu turno')
        if self.fase == "envido":
            if not self.envido_cantado:
                self.envido_cantado = True
            self.fase = "juego"
        if self.fase != "juego":
            return self.bot.answer_callback_query(call.id, 'No puedes jugar ahora')
        self.cartas[uid].remove(carta)
        self.ronda_cartas.append((uid, carta))
        self.bot.answer_callback_query(call.id, f'Jugaste {carta}')
        enviar_carta(self.bot, self.chat_id, carta)
        self.bot.send_message(self.chat_id, f"{uid} juega {carta}")
        if len(self.ronda_cartas) == len(self.players):
            self._resolver_mano()
        else:
            viejo_turno = self.turno_actual
            self.turno_actual = (self.turno_actual + 1) % len(self.players)
            self._update_after_turn_change(viejo_turno)

    def _update_after_turn_change(self, old_turn):
        self._send_private_message(self.players[old_turn])
        self._send_private_message(self.players[self.turno_actual])
        self._update_public()

    def _handle_envido(self, call, accion, data):
        uid = call.from_user.id
        if accion == 'envido_call_envido':
            self._cantar_envido(call, uid, tipo="envido")
        elif accion == 'envido_call_realenvido':
            self._cantar_envido(call, uid, tipo="real_envido")
        elif accion == 'envido_call_falta':
            self._cantar_envido(call, uid, tipo="falta_envido")
        elif accion == 'envido_quiero':
            if self.envido_pendiente and self.envido_pendiente['cantante'] != uid:
                self._resolver_envido(uid, acepta=True)
        elif accion == 'envido_noquiero':
            if self.envido_pendiente and self.envido_pendiente['cantante'] != uid:
                self._resolver_envido(uid, acepta=False)
        elif accion == 'envido_sonbuenas':
            if self.envido_pendiente and self.envido_pendiente['cantante'] != uid:
                self._resolver_envido(uid, son_buenas=True)

    def _cantar_envido(self, call, uid, tipo):
        if self.fase != "envido" or self.envido_cantado:
            self.bot.answer_callback_query(call.id, 'No se puede cantar envido ahora')
            return
        if uid != self.players[self.turno_actual]:
            self.bot.answer_callback_query(call.id, 'No es tu turno')
            return
        puntos_ofrecidos = {"envido": 2, "real_envido": 3, "falta_envido": self._calcular_falta()}[tipo]
        self.envido_pendiente = {"tipo": tipo, "cantante": uid, "puntos": puntos_ofrecidos}
        self.envido_cantado = True
        self.fase = "envido_pendiente"
        self._notify_all_players()
        self.bot.send_message(self.chat_id, f"{uid} cantó {tipo}")
        self.bot.answer_callback_query(call.id, f'Cantaste {tipo}')

    def _notify_all_players(self):
        for uid in self.players:
            self._send_private_message(uid)

    def _calcular_falta(self):
        if self.puntos[0] == self.puntos[1]:
            return 15
        elif self.puntos[0] > self.puntos[1]:
            return 15 - self.puntos[0]
        else:
            return 15 - self.puntos[1]

    def _resolver_envido(self, uid_respondedor, acepta=True, son_buenas=False):
        if not self.envido_pendiente:
            return
        pend = self.envido_pendiente
        if son_buenas:
            self.puntos[self._pareja_de(pend['cantante'])] += pend['puntos']
            self.bot.send_message(self.chat_id, f"{pend['cantante']} gana el envido por son buenas ({pend['puntos']} puntos)")
        elif acepta:
            env_cantante = calcular_envido(self.cartas[pend['cantante']])
            env_respondedor = calcular_envido(self.cartas[uid_respondedor])
            if env_cantante >= env_respondedor:
                ganador = pend['cantante']
            else:
                ganador = uid_respondedor
            self.puntos[self._pareja_de(ganador)] += pend['puntos']
            self.bot.send_message(self.chat_id, f"Envido: {ganador} gana con {env_cantante} vs {env_respondedor} ({pend['puntos']} puntos)")
        else:
            self.puntos[self._pareja_de(pend['cantante'])] += 1
            self.bot.send_message(self.chat_id, f"{pend['cantante']} gana 1 punto")
        self.envido_pendiente = None
        self.fase = "juego"
        self._notify_current_turn()
        self._update_public()

    def _handle_truco(self, call, accion, data):
        uid = call.from_user.id
        if accion == 'truco_call':
            self._cantar_truco(call, uid)
        elif accion == 'truco_quiero':
            if self.truco_pendiente and self.truco_pendiente['cantante'] != uid:
                self._resolver_truco(uid, acepta=True)
        elif accion == 'truco_noquiero':
            if self.truco_pendiente and self.truco_pendiente['cantante'] != uid:
                self._resolver_truco(uid, acepta=False)

    def _cantar_truco(self, call, uid):
        if self.fase != "juego":
            self.bot.answer_callback_query(call.id, 'No se puede cantar truco ahora')
            return
        if uid != self.players[self.turno_actual]:
            self.bot.answer_callback_query(call.id, 'No es tu turno')
            return
        if self.truco_pendiente:
            self.bot.answer_callback_query(call.id, 'Ya hay un truco pendiente')
            return
        self.truco_pendiente = {"nivel": 2, "cantante": uid}
        self.bot.send_message(self.chat_id, f"{uid} cantó TRUCO")
        self._notify_all_players()
        self.bot.answer_callback_query(call.id, 'Truco cantado')

    def _resolver_truco(self, uid_respondedor, acepta):
        if not self.truco_pendiente:
            return
        pend = self.truco_pendiente
        if acepta:
            self.bot.send_message(self.chat_id, f"{uid_respondedor} QUIERE")
            self.truco_pendiente = None
            self._notify_current_turn()
            self._update_public()
        else:
            self.puntos[self._pareja_de(pend['cantante'])] += 1
            self.bot.send_message(self.chat_id, f"{uid_respondedor} NO QUIERE. {pend['cantante']} gana 1 punto")
            self._terminar_mano_por_truco()
            self.truco_pendiente = None

    def _terminar_mano_por_truco(self):
        self.ronda = 1
        self.ronda_cartas = []
        self.mano_idx = (self.mano_idx + 1) % len(self.players)
        self.turno_actual = self.mano_idx
        self.mazo = mazo_truco_db()
        random.shuffle(self.mazo)
        for uid in self.players:
            self.cartas[uid] = [self.mazo.pop() for _ in range(3)]
        self.envido_cantado = False
        self.envido_pendiente = None
        self.fase = "envido"
        self._notify_all_players()
        self._update_public()

    def _resolver_mano(self):
        ganador = max(self.ronda_cartas, key=lambda x: valor_truco(x[1]))[0]
        pareja = self._pareja_de(ganador)
        self.ganadas_mano[pareja] += 1
        self.bot.send_message(self.chat_id, f"Mano ganada por {ganador}")
        self.ronda += 1
        self.ronda_cartas = []
        if self.ganadas_mano[0] >= 2 or self.ganadas_mano[1] >= 2:
            pareja_ganadora = 0 if self.ganadas_mano[0] >= 2 else 1
            self.puntos[pareja_ganadora] += 1
            self.bot.send_message(self.chat_id, f"Ronda ganada por pareja {pareja_ganadora+1}. Puntos: {self.puntos}")
            if self.puntos[pareja_ganadora] >= 15:
                self.end_game(winner=pareja_ganadora)
            else:
                self._nueva_mano()
        else:
            self.turno_actual = (self.mano_idx + 1) % len(self.players)
            self._notify_all_players()
            self._update_public()

    def _nueva_mano(self):
        self.ganadas_mano = [0, 0]
        self.ronda = 1
        self.ronda_cartas = []
        self.mano_idx = (self.mano_idx + 1) % len(self.players)
        self.turno_actual = self.mano_idx
        self.mazo = mazo_truco_db()
        random.shuffle(self.mazo)
        for uid in self.players:
            self.cartas[uid] = [self.mazo.pop() for _ in range(3)]
        self.envido_cantado = False
        self.envido_pendiente = None
        self.fase = "envido"
        self._notify_all_players()
        self._update_public()

    def on_game_over(self, winner, results):
        if self.apuesta and winner is not None:
            from core.db import sumar_itsunario
            for uid in self.parejas[winner]:
                sumar_itsunario(uid, tokens=0, fichas=self.apuesta * 2)
        self.bot.send_message(self.chat_id, f"Partida finalizada. Ganador: pareja {winner+1}")

    def abandon(self, user_id):
        self.end_game(None)

    def cancel(self, user_id):
        self.end_game(None)

def register_truco_handlers(bot, register_command=None):
    @bot.message_handler(commands=['truco'])
    def cmd_truco(message):
        chat_id = str(message.chat.id)
        if get_game(chat_id):
            bot.reply_to(message, "Ya hay una partida en curso.")
            return
        parts = message.text.split()
        if len(parts) < 3 or not parts[1].isdigit() or not parts[2].isdigit():
            bot.reply_to(message, "Uso: /truco <jugadores> <apuesta>")
            return
        n = int(parts[1])
        apuesta = int(parts[2])
        if n not in (2,4,6):
            bot.reply_to(message, "Número inválido (2,4,6).")
            return

        # Mensaje visual con botón
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            "Unirse a la partida",
            callback_data="truco_join_" + chat_id
        ))
        msg_texto = (
            "<b>Nueva partida de Truco Argentino!</b>

"
            "<b>Creador:</b> " + message.from_user.first_name + "
"
            "<b>Jugadores:</b> " + str(n) + "
"
            "<b>Apuesta:</b> " + str(apuesta) + " fichas

"
            "<i>Pulsa el botón de abajo para entrar.</i>"
        )
        img = obtener_imagen('truco')
        if img:
            bot.send_photo(chat_id, img, caption=msg_texto, reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(chat_id, msg_texto, reply_markup=markup, parse_mode='HTML')

        # Registrar sesión
        session = TrucoSession(bot, chat_id, message.from_user.id, n, apuesta)
        register_game(chat_id, session)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('truco_join_'))
    def callback_unirse_truco(call):
        chat_id = call.data.replace('truco_join_', '')
        session = get_game(chat_id)
        if not session or not isinstance(session, TrucoSession):
            bot.answer_callback_query(call.id, "La partida ya no existe.")
            return
        if call.from_user.id in session.players:
            bot.answer_callback_query(call.id, "Ya estás en esta partida.")
            return
        session.unirse(call.from_user.id)
        bot.answer_callback_query(call.id, "Te has unido con éxito!")
