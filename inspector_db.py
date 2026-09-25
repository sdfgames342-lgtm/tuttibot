import sqlite3

def inspeccionar(db_name):
    print(f"\n--- Analizando: {db_name} ---")
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        tablas = c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        tablas_list = [t[0] for t in tablas]
        print(f"✅ Tablas: {tablas_list}")
        
        if 'usuarios' in tablas_list:
            count = c.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
            print(f"📊 Usuarios encontrados: {count}")
        
        if 'banco_ledger' in tablas_list:
            movimientos = c.execute("SELECT COUNT(*) FROM banco_ledger").fetchone()[0]
            print(f"💰 Movimientos bancarios: {movimientos}")
            
        conn.close()
    except Exception as e:
        print(f"❌ Error leyendo {db_name}: {e}")

inspeccionar('tutti_game.db')
inspeccionar('main_database.db')
