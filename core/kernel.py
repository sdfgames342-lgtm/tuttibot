import threading, time, logging
from utils.reply_helper import safe_reply
from utils.idiomas import obtener_texto
from core.db import guardar_sala, cargar_salas, eliminar_sala
from core.db import actualizar_pin
from core.db import obtener_grupos_espera_inactivos
import datetime

logger = logging.getLogger(__name__)

def start_kernel_threads(bot, salas, salas_lock, msg_queue):

    def guardar_estado_salas():
        while True:
            time.sleep(10)
            try:
                with salas_lock:
                    for cid, s in list(salas.items()):
                        guardar_sala(cid, s)
            except Exception as e:
                logger.error(f"Error guardando salas: {e}")

    def verificar_salas():
        while True:
            time.sleep(60)
            with salas_lock:
                for cid in list(salas.keys()):
                    try:
                        bot.get_chat(cid)
                    except:
                        logger.info(f"Limpiando sala zombie de chat {cid}")
                        for uid in salas[cid].get('jugadores', {}):
                            try:
                                safe_reply(bot, uid, obtener_texto("i18n_kernel_sala_eliminada"))
                            except:
                                pass
                        del salas[cid]
                        eliminar_sala(cid)

    def hilo_auto_leave():
        while True:
            time.sleep(3600)
            candidatos = obtener_grupos_espera_inactivos(24)
            for cid in candidatos:
                try:
                    bot.leave_chat(cid)
                    with salas_lock:
                        if cid in salas:
                            for uid in salas[cid].get('jugadores', {}):
                                try:
                                    safe_reply(bot, uid, obtener_texto("i18n_kernel_grupo_inactivo"))
                                except:
                                    pass
                            del salas[cid]
                            eliminar_sala(cid)
                    logger.info(f"Auto-abandono del grupo {cid}")
                except Exception as e:
                    logger.warning(f"No se pudo abandonar {cid}: {e}")

    def hilo_marketing_auto():
        while True:
            time.sleep(3600)
            try:
                actualizar_pin(bot, msg_queue)
            except Exception as e:
                logger.error(f"Error en marketing: {e}")

    threading.Thread(target=guardar_estado_salas, daemon=True).start()
    threading.Thread(target=verificar_salas, daemon=True).start()
    threading.Thread(target=hilo_auto_leave, daemon=True).start()
    threading.Thread(target=hilo_marketing_auto, daemon=True).start()

    def hilo_economia():
        while True:
            time.sleep(86400)
            try:
                from core.economia import actualizar_indicadores
                actualizar_indicadores()
            except Exception as e:
                logger.error(f"Error en worker económico: {e}")

    threading.Thread(target=hilo_economia, daemon=True).start()
