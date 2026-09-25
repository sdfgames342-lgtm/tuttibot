import os
import sys
import importlib
import sqlite3

def check_step(name, condition, error_msg):
    if condition:
        print(f"✅ {name}")
        return True
    else:
        print(f"❌ {name}: {error_msg}")
        return False

print("--- AUDITORÍA DE SISTEMA ITSUKI MAINFRAME ---")

# 1. Verificación de Entorno
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), '../.env'))
check_step("Archivo .env", os.getenv('TELEGRAM_TOKEN') is not None, "TOKEN no encontrado en ../.env")

# 2. Integridad de Base de Datos
try:
    conn = sqlite3.connect('main_database.db')
    tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    conn.close()
    check_step("Base de Datos", 'usuarios' in tables, "Tabla 'usuarios' inexistente en main_database.db")
except Exception as e:
    print(f"❌ Base de Datos: Error de conexión - {e}")

# 3. Prueba de Importaciones Core (El corazón del error)
core_modules = [
    ('core.db', ['get_db', 'inicializar_db']),
    ('core.bot', ['ItsukiBot']),
    ('core.loader', ['cargar_comandos']),
    ('utils.idiomas', ['obtener_texto'])
]

print("\n🧪 Verificando Módulos Core:")
for mod_name, functions in core_modules:
    try:
        mod = importlib.import_module(mod_name)
        missing = [f for f in functions if not hasattr(mod, f)]
        if not missing:
            print(f"  ✅ {mod_name}: OK")
        else:
            print(f"  ❌ {mod_name}: Faltan funciones {missing}")
    except Exception as e:
        print(f"  ❌ {mod_name}: Error Crítico - {e}")

# 4. Escaneo de Comandos uno por uno
print("\n📂 Análisis de Comandos (commands/):")
cmd_path = "commands"
for file in sorted(os.listdir(cmd_path)):
    if file.endswith(".py") and file != "__init__.py":
        mod_name = f"commands.{file[:-3]}"
        try:
            # Forzamos la recarga para ver errores de sintaxis internos
            importlib.invalidate_caches()
            importlib.import_module(mod_name)
            print(f"  ✅ {file}: Sin errores de sintaxis")
        except Exception as e:
            print(f"  ⚠️ {file}: ERROR DETECTADO -> {e}")

# 5. Detección de Conflictos de Archivos (Duplicados)
print("\n⚖️ Verificando Conflictos de Nombre:")
duplicados = [f for f in os.listdir('.') if f in ['itsuki.py', 'itsuki_engine.py', 'bot.py']]
if duplicados:
    print(f"  ⚠️ Cuidado: Tienes scripts en la raíz que pueden confundir al cargador: {duplicados}")
else:
    print("  ✅ Sin scripts redundantes en la raíz.")

print("\n--- FIN DE LA AUDITORÍA ---")
