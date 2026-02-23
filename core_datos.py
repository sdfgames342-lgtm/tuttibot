# core_datos.py
def guardar_mensaje(supabase, user_id, texto):
    supabase.table("mensajes").insert({
        "user_id": str(user_id),
        "content": texto
    }).execute()
