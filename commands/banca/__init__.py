import ctypes, logging, sqlite3
from pathlib import Path
from utils.reply_helper import safe_reply
from utils.idiomas import obtener_texto

logger = logging.getLogger(__name__)

# ---- Cargar librería COBOL ----
_lib_path = Path(__file__).with_name('libbanco.so')
if _lib_path.exists():
    cobol = ctypes.CDLL(str(_lib_path))
    cobol.c_consultar_saldo.argtypes = [ctypes.POINTER(ctypes.c_longlong)]
    cobol.c_transferir.argtypes = [ctypes.POINTER(ctypes.c_longlong), ctypes.POINTER(ctypes.c_longlong)]
    cobol.c_interes_compuesto.argtypes = [ctypes.POINTER(ctypes.c_longlong), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int)]
else:
    cobol = None

# ---- Helpers ----
def _conectar():
    return sqlite3.connect("tutte_game.db")

def _saldo_centavos(user_id):
    conn = _conectar()
    cur = conn.execute("SELECT COALESCE(SUM(monto), 0) FROM banco_ledger WHERE user_id = ?", (user_id,))
    saldo = cur.fetchone()[0]
    conn.close()
    return saldo

def _registrar_entrada(user_id, monto, concepto, origen=None):
    conn = _conectar()
    conn.execute("INSERT INTO banco_ledger (user_id, monto, concepto, origen) VALUES (?,?,?,?)",
                 (user_id, monto, concepto, origen))
    conn.commit()
    conn.close()

# ---- Comando /banco ----
def register_banca_handlers(bot, register_command=None):
    @bot.message_handler(commands=['banco'])
    def banco_cmd(message):
        parts = message.text.split()
        uid = message.from_user.id
        if len(parts) == 1:
            return _mostrar_ayuda(bot, message)
        sub = parts[1].lower()
        if sub == 'saldo':
            return _cmd_saldo(bot, message, uid)
        elif sub == 'transferir' and len(parts) >= 4:
            return _cmd_transferir(bot, message, uid, parts)
        elif sub == 'invertir' and len(parts) >= 3:
            return _cmd_interes(bot, message, uid, parts)
        else:
            return _mostrar_ayuda(bot, message)

def _mostrar_ayuda(bot, message):
    texto = (
        "🏦 <b>BANCO ITSŲKI</b>\n"
        "/banco saldo – ver saldo\n"
        "/banco transferir <id_destino> <monto_en_centavos>\n"
        "/banco invertir <periodos>"
    )
    safe_reply(bot, message, texto, parse_mode='HTML')

def _cmd_saldo(bot, message, uid):
    saldo = _saldo_centavos(uid)
    if cobol:
        c_saldo = ctypes.c_longlong(saldo)
        cobol.c_consultar_saldo(ctypes.byref(c_saldo))
        saldo_verificado = c_saldo.value
    else:
        saldo_verificado = saldo
    texto = f"💰 Saldo: {saldo_verificado} centavos (Itsunarios)"
    safe_reply(bot, message, texto)

def _cmd_transferir(bot, message, uid, parts):
    try:
        destino = int(parts[2])
        monto = int(parts[3])
    except ValueError:
        safe_reply(bot, message, "Formato inválido. Use IDs numéricos y monto en centavos.")
        return
    if monto <= 0:
        safe_reply(bot, message, "El monto debe ser positivo.")
        return
    saldo_actual = _saldo_centavos(uid)
    if saldo_actual < monto:
        safe_reply(bot, message, "Fondos insuficientes.")
        return
    if cobol:
        c_saldo = ctypes.c_longlong(saldo_actual)
        c_monto = ctypes.c_longlong(monto)
        cobol.c_transferir(ctypes.byref(c_saldo), ctypes.byref(c_monto))
        nuevo_saldo = c_saldo.value
    else:
        nuevo_saldo = saldo_actual - monto
    _registrar_entrada(uid, -monto, f"Transferencia a {destino}")
    _registrar_entrada(destino, monto, f"Transferencia de {uid}")
    texto = f"✅ Transferencia de {monto} centavos a {destino} realizada. Tu nuevo saldo: {nuevo_saldo} centavos."
    safe_reply(bot, message, texto)

def _cmd_interes(bot, message, uid, parts):
    try:
        periodos = int(parts[2])
    except ValueError:
        safe_reply(bot, message, "Número de periodos inválido.")
        return
    capital = _saldo_centavos(uid)
    if cobol:
        c_capital = ctypes.c_longlong(capital)
        c_tasa = ctypes.c_double(0.05)
        c_periodos = ctypes.c_int(periodos)
        cobol.c_interes_compuesto(ctypes.byref(c_capital), ctypes.byref(c_tasa), ctypes.byref(c_periodos))
        nuevo_capital = c_capital.value
    else:
        nuevo_capital = int(capital * (1.05 ** periodos))
    ganancia = nuevo_capital - capital
    _registrar_entrada(uid, ganancia, f"Interés compuesto {periodos} periodos")
    texto = f"📈 Inversión a {periodos} periodos: capital final {nuevo_capital} centavos (ganancia: {ganancia} centavos)."
    safe_reply(bot, message, texto)
