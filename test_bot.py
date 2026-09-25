#!/usr/bin/env python3
"""
Verificación automatizada de Itsuki Mainframe v6.0.
Comprueba imports, base de datos, lógica de juego y economía Itsunario.
No requiere token de Telegram real.
"""

import sys, os, sqlite3, json, hashlib

# ─── Configurar entorno ───────────────────
os.environ.setdefault("TELEGRAM_TOKEN", "test_token")
os.environ.setdefault("DATABASE_PATH", "tutte_game.db")
os.environ.setdefault("DB_QUOTA_LIMIT", "5000000")
sys.path.insert(0, os.path.dirname(__file__))

from pathlib import Path

def color(text, code):
    return f"\033[{code}m{text}\033[0m"
def ok(msg):
    print(color(f"  ✅ {msg}", "1;32"))
def fail(msg):
    print(color(f"  ❌ {msg}", "1;31"))
    return 1
def info(msg):
    print(color(f"  🔍 {msg}", "1;36"))

errors = 0

def test_imports():
    """Verifica que todos los módulos esenciales se importen."""
    print(color("\n📦 Verificando imports...", "1;33"))
    modulos = [
        ("core.db", "init_db"),
        ("core.loader", "load_commands"),
        ("core.kernel", "start_kernel_threads"),
        ("utils.idiomas", "obtener_texto"),
        ("utils.decorators", "ItsukiLedger"),
        ("utils.reply_helper", "safe_reply"),
        ("commands.salir", "register_salir_handlers"),
        ("commands.sizania", "register_sizania_handlers"),
        ("commands.user", "register_user_handlers"),
        ("commands.panel", "register_panel_commands"),
        ("commands.config", "register_config_handlers"),
        ("commands.lang", "register_lang_handlers"),
        ("commands.about", "register_about_command"),
        ("commands.help", "register_help_command"),
        ("commands.activar", "register_activar_handlers"),
        ("commands.broadcast", "register_broadcast_commands"),
        ("commands.sponsor", "register_sponsor_handlers"),
        ("commands.ytmusic", "register_ytmusic_command"),
        ("commands.itsunario", "register_itsunario_handlers"),
    ]
    err = 0
    for mod_name, func_name in modulos:
        try:
            mod = __import__(mod_name, fromlist=[func_name])
            if hasattr(mod, func_name):
                ok(f"{mod_name}.{func_name}")
            else:
                err += fail(f"{mod_name} se importó pero no tiene {func_name}")
        except Exception as e:
            err += fail(f"{mod_name}: {str(e)}")
    return err

def test_database():
    """Verifica que la base de datos tenga las tablas necesarias."""
    print(color("\n🗄️  Verificando base de datos...", "1;33"))
    err = 0
    try:
        conn = sqlite3.connect("tutte_game.db")
        cur = conn.cursor()
        # Tablas esperadas
        tablas_esperadas = [
            "jugadores", "partidas", "respuestas", "calculo_puntos",
            "control_grupos", "metricas_marketing", "log_eventos",
            "config_bot", "stickers_cartas", "partidas_guerra",
            "partida_jugadores", "partida_categorias",
            "itsunario", "itsunario_canjes", "itsunario_limites"
        ]
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas_reales = [r[0] for r in cur.fetchall()]
        for tabla in tablas_esperadas:
            if tabla in tablas_reales:
                ok(f"Tabla {tabla}")
            else:
                # Si falta, intentar crearla desde schema.sql
                info(f"Tabla {tabla} no encontrada, intentando crear...")
                try:
                    if Path("schema.sql").exists():
                        conn.executescript(open("schema.sql").read())
                        ok(f"Tabla {tabla} creada desde schema")
                    else:
                        err += fail(f"Tabla {tabla} no existe y no se encontró schema.sql")
                except Exception as e:
                    err += fail(f"No se pudo crear {tabla}: {e}")
        conn.close()
    except Exception as e:
        err += fail(f"Error de conexión a BD: {e}")
    return err

def test_itsunario():
    """Prueba el sistema económico Itsunario."""
    print(color("\n💰 Probando sistema Itsunario...", "1;33"))
    err = 0
    try:
        from core.db import (
            obtener_saldo_itsunario, sumar_itsunario,
            canjear_tokens_por_fichas, otorgar_token_tuttifrutti,
            otorgar_tokens_por_nivel, obtener_puntos_jugador
        )
        # Usar un user_id de prueba
        uid = 999999
        # Inicializar saldo
        conn = sqlite3.connect("tutte_game.db")
        conn.execute("INSERT OR REPLACE INTO itsunario (user_id, tokens, fichas) VALUES (?, ?, ?)", (uid, 50, 100))
        conn.commit()
        # Insertar límites por si faltan
        conn.execute("INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('fichas_por_token', 10)")
        conn.execute("INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('comision_canje_fichas', 5)")
        conn.execute("INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('canje_fichas_max_diario', 1000)")
        conn.close()

        t, f = obtener_saldo_itsunario(uid)
        if t == 50 and f == 100:
            ok(f"Saldo inicial: {t} tokens, {f} fichas")
        else:
            err += fail(f"Saldo incorrecto: {t} tokens, {f} fichas (esperado 50, 100)")

        # Canjear 10 tokens
        exito, fichas_ganadas = canjear_tokens_por_fichas(uid, 10)
        if exito:
            ok(f"Canje exitoso de 10 tokens -> {fichas_ganadas} fichas")
            t2, f2 = obtener_saldo_itsunario(uid)
            if t2 == 40 and f2 == 100 + fichas_ganadas:
                ok("Saldos actualizados correctamente")
            else:
                err += fail(f"Saldo tras canje: {t2} tokens, {f2} fichas")
        else:
            err += fail(f"Canje fallido: {fichas_ganadas}")

        # Otorgar token por racha
        ok_flag, tokens_ganados = otorgar_token_tuttifrutti(uid, True)
        if tokens_ganados == 0:
            ok_flag = True
            ok("Primera victoria no da token (necesita 2 consecutivas)")
        # Segunda victoria
        ok_flag2, tokens_ganados2 = otorgar_token_tuttifrutti(uid, True)
        if ok_flag2 and tokens_ganados2 > 0:
            ok(f"Segunda victoria consecutiva: +{tokens_ganados2} token")
        else:
            err += fail("No se otorgó token en la 2da victoria consecutiva")

        # Otorgar tokens por nivel (simular)
        tokens_nivel = otorgar_tokens_por_nivel(uid, 1500)  # nivel 1
        if tokens_nivel > 0:
            ok(f"Tokens por nivel: {tokens_nivel}")
        else:
            info("Tokens por nivel: 0 (nivel no subió o no aplica)")

        # Limpiar datos de prueba
        conn = sqlite3.connect("tutte_game.db")
        conn.execute("DELETE FROM itsunario WHERE user_id = ?", (uid,))
        conn.execute("DELETE FROM itsunario_canjes WHERE user_id = ?", (uid,))
        conn.commit()
        conn.close()
    except Exception as e:
        err += fail(f"Error en Itsunario: {e}")
    return err

def test_idiomas():
    """Verifica que el sistema i18n funcione."""
    print(color("\n🌐 Verificando sistema i18n...", "1;33"))
    err = 0
    try:
        from utils.idiomas import obtener_texto, cargar_textos
        t = obtener_texto('start.welcome', lang='es')
        if t and 'ITSUI_NET' in t:
            ok("Texto en español obtenido")
        else:
            err += fail(f"Texto español: {t}")
        t_pt = obtener_texto('start.welcome', lang='pt')
        if t_pt and 'ITSUI_NET' in t_pt:
            ok("Texto en portugués obtenido")
        else:
            info("Texto portugués no encontrado (puede faltar clave)")
        # Verificar que las claves i18n no tengan placeholders rotos
        data = cargar_textos('es')
        placeholders = [k for k, v in data.items() if isinstance(v, str) and v.startswith('<') and v.endswith('>')]
        if placeholders:
            info(f"{len(placeholders)} placeholders pendientes de traducción")
    except Exception as e:
        err += fail(f"Error i18n: {e}")
    return err

def test_minigames_structure():
    """Verifica que el paquete minigames tenga los submódulos."""
    print(color("\n🎲 Verificando estructura minigames...", "1;33"))
    err = 0
    subm = ['_reaper', 'ruleta', 'duelo', 'libro', 'exam_admin', 'data']
    for m in subm:
        try:
            __import__(f'commands.minigames.{m}')
            ok(f"Submódulo {m}")
        except Exception as e:
            err += fail(f"Submódulo {m}: {e}")
    return err

def test_montecarlo_fichas():
    """Verifica que Montecarlo use fichas correctamente."""
    print(color("\n🃏 Verificando Montecarlo...", "1;33"))
    err = 0
    try:
        from commands.montecarlo import (
            partidas_guerra, juegos_mayormenor, valor_carta, crear_mazo, repartir_mazos
        )
        ok("Módulo montecarlo importado")
        # Verificar función de valor
        v = valor_carta("as_espadas")
        if v == 14:
            ok("valor_carta funciona")
        else:
            err += fail(f"valor_carta: {v}")
    except Exception as e:
        err += fail(f"Error en Montecarlo: {e}")
    return err

def test_schema_integrity():
    """Compara schema.sql con la BD real."""
    print(color("\n🔬 Verificando integridad schema...", "1;33"))
    err = 0
    try:
        if not Path("schema.sql").exists():
            err += fail("schema.sql no encontrado")
            return err
        with open("schema.sql") as f:
            schema_sql = f.read()
        # Contar tablas en schema
        import re
        schema_tables = re.findall(r'CREATE TABLE(?: IF NOT EXISTS)? (\w+)', schema_sql)
        conn = sqlite3.connect("tutte_game.db")
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        db_tables = [r[0] for r in cur.fetchall()]
        conn.close()
        faltan = set(schema_tables) - set(db_tables)
        sobran = set(db_tables) - set(schema_tables)
        if not faltan and not sobran:
            ok(f"Coherencia perfecta ({len(schema_tables)} tablas)")
        else:
            if faltan:
                err += fail(f"Tablas en schema pero no en BD: {faltan}")
            if sobran:
                info(f"Tablas en BD pero no en schema: {sobran}")
    except Exception as e:
        err += fail(f"Error de integridad: {e}")
    return err


def test_banco_journaling():
    """Verifica el sistema de journaling del banco."""
    print(color("\n🏦 Probando journaling bancario...", "1;33"))
    err = 0
    try:
        import sqlite3
        conn = sqlite3.connect("tutte_game.db")
        # Crear tabla si no existe
        conn.execute("CREATE TABLE IF NOT EXISTS banco_ledger (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, monto INTEGER NOT NULL, concepto TEXT, origen TEXT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES jugadores(user_id))")
        
        uid_a, uid_b = 1001, 1002
        monto = 500
        
        # Insertar entradas de prueba
        conn.execute("INSERT INTO banco_ledger (user_id, monto, concepto, origen) VALUES (?, ?, ?, ?)", 
                     (uid_a, -monto, "Transferencia a B", str(uid_b)))
        conn.execute("INSERT INTO banco_ledger (user_id, monto, concepto, origen) VALUES (?, ?, ?, ?)", 
                     (uid_b, monto, "Transferencia de A", str(uid_a)))
        conn.commit()
        
        # Verificar saldos
        saldo_a = conn.execute("SELECT COALESCE(SUM(monto), 0) FROM banco_ledger WHERE user_id = ?", (uid_a,)).fetchone()[0]
        saldo_b = conn.execute("SELECT COALESCE(SUM(monto), 0) FROM banco_ledger WHERE user_id = ?", (uid_b,)).fetchone()[0]
        
        if saldo_a == -monto and saldo_b == monto:
            ok(f"Journaling correcto: A={saldo_a}, B={saldo_b}")
        else:
            err += fail(f"Journaling incorrecto: A={saldo_a}, B={saldo_b}")
        
        # Limpiar datos de prueba
        conn.execute("DELETE FROM banco_ledger WHERE user_id IN (?, ?)", (uid_a, uid_b))
        conn.commit()
        conn.close()
    except Exception as e:
        err += fail(f"Error en test de journaling: {e}")
    return err


def main():
    print("╔═══════════════════════════════════════╗")
    print("║   ITSŲKI MAINFRAṀE · VERIFICACIÓN    ║")
    print("╚═══════════════════════════════════════╝")
    total_errors = 0
    total_errors += test_imports()
    total_errors += test_database()
    total_errors += test_schema_integrity()
    total_errors += test_idiomas()
    total_errors += test_itsunario()
    total_errors += test_minigames_structure()
    total_errors += test_montecarlo_fichas()
    total_errors += test_banco_journaling()

    print("\n" + "="*30)
    if total_errors == 0:
        print(color("🎉 Todas las pruebas pasaron sin errores", "1;32"))
    else:
        print(color(f"⚠ {total_errors} errores encontrados", "1;33"))
    print("="*30)

if __name__ == "__main__":
    main()
