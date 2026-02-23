# core_datos.py
import os
import string
import random
from supabase import Client

CREATOR_ID = int(os.getenv("CREATOR_ID", 0))
CREATOR_CUS = os.getenv("CREATOR_CUS", None)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def guardar_mensaje(user_id, content):
    data = {"user_id": user_id, "content": content}
    supabase.table("mensajes").insert(data).execute()
def generar_cus(length=26):
    """Genera un CUS aleatorio de 26 caracteres"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def registrar_usuario(supabase: Client, telegram_id: int):
    """Registra un usuario en Supabase si no existe"""
    # 1. Revisar si ya existe
    res = supabase.table("id_history").select("cus").eq("telegram_id", telegram_id).execute()
    if res.data:
        return res.data[0]["cus"], False  # Ya existía

    # 2. Determinar CUS y admin
    if telegram_id == CREATOR_ID and CREATOR_CUS:
        nuevo_cus = CREATOR_CUS
        es_admin = True
    else:
        nuevo_cus = generar_cus()
        es_admin = False

    # 3. Insertar en tabla users
    supabase.table("users").insert({
        "cus": nuevo_cus,
        "es_admin": es_admin
    }).execute()

    # 4. Vincular telegram_id con CUS
    supabase.table("id_history").insert({
        "telegram_id": telegram_id,
        "cus": nuevo_cus
    }).execute()

    return nuevo_cus, True  # Nuevo registro
