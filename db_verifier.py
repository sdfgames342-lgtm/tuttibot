#!/usr/bin/env python3
"""
Verifica integridad entre schema.sql, tutte_game.db y core/db.py.
Corrige bugs, sugiere mejoras y genera reporte.
"""
import sqlite3, os, re, hashlib, datetime, json
from pathlib import Path

BASE = Path.cwd()
SCHEMA_FILE = BASE / "schema.sql"
DB_FILE = BASE / "tutte_game.db"
DB_PY = BASE / "core" / "db.py"

def color(text, code): return f"\033[{code}m{text}\033[0m"
def red(s): return color(s, "1;31")
def green(s): return color(s, "1;32")
def yellow(s): return color(s, "1;33")
def cyan(s): return color(s, "1;36")

# ─── 1. Extraer definición de schema.sql ─────────────────
schema_tables = {}
with open(SCHEMA_FILE) as f:
    schema_sql = f.read()

# Parsear CREATE TABLE statements
for match in re.finditer(
    r"CREATE TABLE(?: IF NOT EXISTS)? (\w+)\s*\((.*?)\);",
    schema_sql, re.DOTALL | re.IGNORECASE
):
    table_name = match.group(1)
    body = match.group(2)
    columns = []
    for col_match in re.finditer(r"(\w+)\s+(\w+[^,]*(?:\([^)]*\))?)", body):
        col_name = col_match.group(1)
        col_type = col_match.group(2).strip()
        # Evitar capturar constraint keywords
        if col_name.upper() in ('FOREIGN', 'PRIMARY', 'INDEX', 'UNIQUE', 'CHECK'):
            continue
        columns.append((col_name, col_type))
    schema_tables[table_name] = columns

print(f"{cyan('📄 Schema:')} {len(schema_tables)} tablas definidas")

# ─── 2. Extraer estructura de la base de datos ──────────
if DB_FILE.exists():
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    db_tables = [row[0] for row in cursor.fetchall()]
    db_structure = {}
    for table in db_tables:
        cursor.execute(f"PRAGMA table_info({table})")
        db_structure[table] = [(row[1], row[2]) for row in cursor.fetchall()]
    conn.close()
    print(f"{cyan('🗃️  BD:')} {len(db_tables)} tablas encontradas\n")
else:
    print(red("❌ Base de datos no encontrada"))
    exit(1)

# ─── 3. Comparar schema.sql con la BD ─────────────────
discrepancias = []
for table, cols in schema_tables.items():
    if table not in db_structure:
        discrepancias.append(f"Tabla '{table}' existe en schema.sql pero NO en la BD")
        continue
    db_cols = {name: dtype for name, dtype in db_structure[table]}
    schema_cols = {name: dtype for name, dtype in cols}
    
    # Columnas en schema pero no en BD
    for col, dtype in cols:
        if col not in db_cols:
            discrepancias.append(f"Columna '{table}.{col}' ({dtype}) existe en schema.sql pero NO en la BD")
    
    # Columnas en BD pero no en schema
    for col, dtype in db_structure[table]:
        if col not in schema_cols:
            discrepancias.append(f"Columna '{table}.{col}' ({dtype}) existe en la BD pero NO en schema.sql")

# Tablas en BD que no están en schema
for table in db_tables:
    if table not in schema_tables:
        discrepancias.append(f"Tabla '{table}' existe en la BD pero NO en schema.sql")

if discrepancias:
    print(yellow("⚠️  Discrepancias encontradas:"))
    for d in discrepancias:
        print(f"   - {d}")
else:
    print(green("✅ Coherencia perfecta entre schema.sql y la BD"))

# ─── 4. Verificar core/db.py ──────────────────────────
with open(DB_PY) as f:
    db_py_content = f.read()

# Bug: auto-importación
if re.search(r'from core\.db import get_connection', db_py_content):
    print(red("\n🐛 BUG DETECTADO: core/db.py se importa a sí mismo"))
    print("   Línea 1: 'from core.db import get_connection'")
    # Corregir
    fixed = db_py_content.replace('from core.db import get_connection\n', '')
    with open(DB_PY, 'w') as f:
        f.write(fixed)
    print(green("   ✅ Corregido automáticamente"))

# Verificar que las funciones referencien columnas existentes
all_schema_columns = set()
for table, cols in schema_tables.items():
    for col, _ in cols:
        all_schema_columns.add(f"{table}.{col}")
        all_schema_columns.add(col)  # también sin prefijo

func_errors = []
for match in re.finditer(r"def (\w+)\(.*?\):\s+.*?\"(SELECT.*?)\"", db_py_content, re.DOTALL):
    func_name = match.group(1)
    query = match.group(2)
    # Extraer columnas de la consulta (simple: buscar palabras después de SELECT)
    select_part = re.search(r"SELECT\s+(.*?)\s+FROM", query, re.IGNORECASE)
    if select_part:
        columns_in_query = re.findall(r"\b(\w+)\b", select_part.group(1))
        for col in columns_in_query:
            if col.upper() in ('COUNT', 'SUM', 'MIN', 'MAX', 'AVG', 'DISTINCT', 'AS', 'AND', 'OR'):
                continue
            if col not in all_schema_columns and col != '1':
                func_errors.append(f"Columna '{col}' en función '{func_name}()' no encontrada en el schema")

if func_errors:
    print(red("❌ Errores en funciones:"))
    for e in func_errors:
        print(f"   - {e}")
else:
    print(green("✅ Todas las funciones de db.py referencian columnas válidas"))

# ─── 5. Sugerencias de mejora ─────────────────────────
print(cyan("\n📈 Mejoras recomendadas:"))

# a) Normalizar columnas JSON
json_cols = re.findall(r"(\w+)\s+TEXT.*(?:JSON|json)", schema_sql)
if json_cols:
    print(f"   • Columnas JSON detectadas: {', '.join(json_cols)}")
    print("     Considerar crear tablas de relación (1FN)")

# b) CTEs para consultas complejas
complex_queries = [
    ("obtener_ranking_global_grupo", 
     "WITH grupo_puntos AS (SELECT puntos_grupo FROM control_grupos WHERE chat_id = ?)\nSELECT COUNT(*) FROM control_grupos WHERE estado='ACTIVO' AND puntos_grupo > (SELECT * FROM grupo_puntos)"),
    ("obtener_grupo_aleatorio_activo",
     "WITH bloqueados AS (SELECT chat_id FROM config_bot WHERE clave = 'book_blocked_' || ? AND valor = '1')\nSELECT cg.chat_id FROM control_grupos cg WHERE cg.estado='ACTIVO' AND cg.chat_id NOT IN (SELECT * FROM bloqueados) ORDER BY RANDOM() LIMIT 1")
]
print("   • CTEs sugeridas para mejorar rendimiento:")
for name, cte in complex_queries:
    print(f"     - {name}():")
    for line in cte.split('\n'):
        print(f"       {line}")

# c) Vistas
print("   • Vistas útiles para consultas frecuentes:")
print("     CREATE VIEW v_grupos_activos AS SELECT * FROM control_grupos WHERE estado='ACTIVO'")
print("     CREATE VIEW v_ranking_jugadores AS SELECT nombre, puntos_historicos FROM jugadores ORDER BY puntos_historicos DESC")

# d) Migraciones
migrations_dir = BASE / "migrations"
if not migrations_dir.exists():
    migrations_dir.mkdir()
    print(f"   • Carpeta 'migrations/' creada para versionado de cambios")

# ─── 6. Reporte ──────────────────────────────────────
report = {
    "schema_tables": len(schema_tables),
    "db_tables": len(db_tables),
    "discrepancias": len(discrepancias),
    "func_errors": len(func_errors),
    "json_cols": len(json_cols),
    "timestamp": datetime.datetime.now().isoformat()
}
report_file = BASE / "db_report.json"
with open(report_file, 'w') as f:
    json.dump(report, f, indent=2, default=str)
print(f"\n📄 Reporte guardado en {report_file}")
