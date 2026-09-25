import sqlite3

def optimizar():
    conn = sqlite3.connect('main_database.db')
    cursor = conn.cursor()
    
    print("--- Optimizando pesos de cartas (Mapeo Frances -> Truco) ---")

    # Mapeo de jerarquía basado en tus equivalencias confirmadas
    # Usamos los nombres en francés que ya están en tu tabla stickers_cartas
    pesos = {
        ('picas', 'as'): 14,      # Ancho de espadas
        ('treboles', 'as'): 13,   # Ancho de bastos
        ('picas', '7'): 12,       # 7 de espadas
        ('diamantes', '7'): 11,   # 7 de oros
        (None, '3'): 10,
        (None, '2'): 9,
        (None, 'as'): 8,          # Ases falsos
        (None, 'k'): 7,           # Rey
        (None, 'q'): 6,           # Caballo
        (None, 'j'): 5,           # Sota
        (None, '10'): 5,          # 10 (Sota en baraja francesa)
        (None, '7'): 4,           # 7s falsos
        (None, '6'): 3,
        (None, '5'): 2,
        (None, '4'): 1
    }

    cursor.execute("SELECT nombre, palo, rango FROM stickers_cartas")
    filas = cursor.fetchall()

    count = 0
    for nombre, palo, rango in filas:
        # 1. Manejo de NULLs: si palo o rango es None, saltar o poner peso 0
        if rango is None:
            cursor.execute("UPDATE stickers_cartas SET peso_truco = 0 WHERE nombre = ?", (nombre,))
            continue

        # 2. Normalización: quitamos comillas simples que SQLite mostró en tu consola
        p_clean = palo.replace("'", "").strip().lower() if palo else None
        r_clean = rango.replace("'", "").strip().lower()

        # 3. Asignación de peso
        # Intenta primero match específico (palo, rango) y luego general (None, rango)
        peso = pesos.get((p_clean, r_clean)) or pesos.get((None, r_clean), 0)

        cursor.execute("UPDATE stickers_cartas SET peso_truco = ? WHERE nombre = ?", (peso, nombre))
        count += 1

    conn.commit()
    conn.close()
    print(f"--- Éxito: {count} cartas procesadas correctamente ---")

if __name__ == "__main__":
    optimizar()

