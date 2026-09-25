from core.db import conectar_db, obtener_afinidad
"""
Comandos de educación financiera: /economia, /invertir
"""
import datetime
from utils.reply_helper import safe_reply
from utils.idiomas import obtener_texto
from utils.decorators import ItsukiLedger, to_mono_font
from core.db import get_connection, get_config
from core.economia import calcular_masa_monetaria, calcular_velocidad_circulacion, calcular_tasa_interes

HELP_COMMANDS = [
    {"command": "/economia", "desc_key": "help.desc_economia", "sudo_level": 0, "category": "economia"},
    {"command": "/invertir", "desc_key": "help.desc_invertir", "sudo_level": 0, "category": "economia"}
]


HELP_COMMANDS = [
    {"command": "/economia", "desc_key": "help.desc_economia", "sudo_level": 0, "category": "economia"},
    {"command": "/invertir", "desc_key": "help.desc_invertir", "sudo_level": 0, "category": "economia"}
]


def register_economia_handlers(bot, register_command=None):

    @bot.message_handler(commands=['economia'])
    def economia_cmd(message):
        """Muestra los indicadores macroeconómicos actuales."""
        uid = message.from_user.id
        M = calcular_masa_monetaria()
        V = calcular_velocidad_circulacion()
        inflacion = get_config('inflacion_actual') or "0"
        tasa_interes = calcular_tasa_interes()
        ultima_act = get_config('ultima_actualizacion_inflacion') or obtener_texto('economia.no_disponible')
        
        variables = {
            obtener_texto('economia.masa_monetaria'): f"{int(M) // 100} Its",
            obtener_texto('economia.velocidad'): str(round(V, 2)),
            obtener_texto('economia.inflacion'): f"{float(inflacion):.2f}%",
            obtener_texto('economia.tasa_interes'): f"{tasa_interes}%",
            obtener_texto('economia.ultima_actualizacion'): ultima_act[:19] if ultima_act != obtener_texto('economia.no_disponible') else ultima_act
        }
        
        msg = ItsukiLedger.render(
            title_key='economia.titulo',
            body_lines=['economia.cuerpo'],
            variables=variables,
            user_id=uid
        )
        safe_reply(bot, message, msg, parse_mode='HTML')

    @bot.message_handler(commands=['invertir'])
    def invertir_cmd(message):
        """Inversión a plazo fijo con tasa variable y bloqueo de capital."""
        parts = message.text.split()
        uid = message.from_user.id
        
        if len(parts) < 3:
            return safe_reply(bot, message, obtener_texto('economia.invertir_uso'))
        
        try:
            monto = int(parts[1])
            periodos = int(parts[2])
        except ValueError:
            return safe_reply(bot, message, obtener_texto('economia.valores_invalidos'))
        
        if monto <= 0 or periodos <= 0:
            return safe_reply(bot, message, obtener_texto('economia.valores_positivos'))
        
        # Verificar saldo
        conn = get_connection()
        cur = conn.execute("SELECT COALESCE(SUM(monto), 0) FROM banco_ledger WHERE user_id = ?", (uid,))
        saldo = cur.fetchone()[0]
        
        if saldo < monto:
            conn.close()
            return safe_reply(bot, message, obtener_texto('economia.saldo_insuficiente'))
        
        # Obtener tasa actual
        tasa = calcular_tasa_interes()
        fecha_fin = datetime.datetime.now() + datetime.timedelta(days=periodos)
        capital_final = int(monto * ((1 + tasa/100) ** periodos))
        ganancia = capital_final - monto
        
        # Registrar en ledger (bloqueo: se resta del disponible)
        conn.execute("INSERT INTO banco_ledger (user_id, monto, concepto) VALUES (?, ?, ?)",
                     (uid, -monto, f"Inversión a plazo fijo ({periodos} períodos al {tasa}%)"))
        # Registrar la inversión
        conn.execute("INSERT INTO inversiones (user_id, capital, tasa_aplicada, periodos, fecha_fin) VALUES (?, ?, ?, ?, ?)",
                     (uid, monto, tasa, periodos, fecha_fin.isoformat()))
        conn.commit()
        conn.close()
        
        variables = {
            obtener_texto('economia.inversion_capital'): f"{monto} Its",
            obtener_texto('economia.inversion_tasa'): f"{tasa}%",
            obtener_texto('economia.inversion_periodos'): str(periodos),
            obtener_texto('economia.inversion_ganancia'): f"{ganancia} Its",
            obtener_texto('economia.inversion_total'): f"{capital_final} Its"
        }
        msg = ItsukiLedger.render(
            title_key='economia.inversion_titulo',
            body_lines=['economia.inversion_cuerpo'],
            variables=variables,
            user_id=uid
        )
        safe_reply(bot, message, msg, parse_mode='HTML')