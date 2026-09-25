import asyncio
import sqlite3
import os
from dotenv import load_dotenv
from telegram import Bot

# Cargamos las variables del archivo .env
load_dotenv()

# Obtenemos el token desde las variables de entorno
TOKEN = os.getenv('TELEGRAM_TOKEN')
# Nombre del set (lo puedes dejar fijo o también llevarlo al .env)
SET_NAME = 'PlayingCardsDeck' 

async def actualizar_ids():
    if not TOKEN:
        print("Error: No se encontró TELEGRAM_TOKEN en el archivo .env")
        return

    bot = Bot(token=TOKEN)
    
    try:
        # Usamos un context manager para la base de datos (más seguro)
        with sqlite3.connect('main_database.db') as conn:
            cursor = conn.cursor()
            print(f"--- Conectado a Telegram. Solicitando info del set: {SET_NAME} ---")
            
            try:
                sticker_set = await bot.get_sticker_set(SET_NAME)
                actualizados = 0
                
                for sticker in sticker_set.stickers:
                    f_unique = sticker.file_unique_id
                    f_id = sticker.file_id
                    
                    # Actualizamos el file_id largo usando el unique_id como llave
                    cursor.execute("""
                        UPDATE stickers_cartas 
                        SET file_id = ? 
                        WHERE file_unique_id = ?
                    """, (f_id, f_unique))
                    
                    if cursor.rowcount > 0:
                        actualizados += 1

                conn.commit()
                print(f"--- Proceso terminado ---")
                print(f"Cartas encontradas en el set: {len(sticker_set.stickers)}")
                print(f"Registros actualizados en DB: {actualizados}")
                
            except Exception as e:
                print(f"Error al obtener el sticker set de Telegram: {e}")
                
    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")

if __name__ == "__main__":
    asyncio.run(actualizar_ids())

