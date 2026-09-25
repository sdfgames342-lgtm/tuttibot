import sqlite3

conn = sqlite3.connect('database.db') # Ajustá el nombre si usas otro en tu config
cursor = conn.cursor()

# Crear tabla de usuarios con los campos que pide user.py
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    user_id INTEGER PRIMARY KEY,
    nombre TEXT DEFAULT 'Desconocido',
    puntos_historicos INTEGER DEFAULT 0,
    afinidad INTEGER DEFAULT 0
)
''')

# Crear tabla itsunario que pide economia.py
cursor.execute('''
CREATE TABLE IF NOT EXISTS itsunario (
    user_id INTEGER PRIMARY KEY,
    tokens REAL DEFAULT 0,
    fichas INTEGER DEFAULT 0
)
''')

conn.commit()
conn.close()
print("✅ Tablas 'usuarios' e 'itsunario' creadas/verificadas.")
