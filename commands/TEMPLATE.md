"""
Plantilla para crear nuevos comandos modulares
==============================================

Para agregar un nuevo comando, sigue estos pasos:

1. Crea un archivo en la carpeta /commands con el nombre del comando
   Ejemplo: /commands/stats.py

2. Define una función register_<nombre>_command que envuelva el comando

3. La función debe recibir: bot, register_command (y opcionalmente: salas, registrar_jugador, etc.)

4. Usa el decorador @register_command('<nombre>') para registrar el comando

5. Importa la función en commands/__init__.py

6. Importa y llama en main.py

7. Agrega los textos al archivo idiomas/es.json

8. Usa utils.idiomas para obtener textos


EJEMPLO: Comando /stats para ver estadísticas
=============================================

En: /commands/stats.py
---

from utils.idiomas import obtener_texto, formatear_texto

def register_stats_command(bot, register_command, salas):
    @register_command('stats')
    def stats(message):
        '''Muestra estadísticas del juego'''
        safe_reply(bot, message, obtener_texto('stats.message'))


En: /commands/__init__.py
---

from .stats import register_stats_command

__all__ = ['register_start_command', 'register_help_command', 'register_create_command', 'register_about_command', 'register_stats_command']


En: /main.py
---

from commands import register_stats_command

# Dentro de la sección de registro de comandos:
register_stats_command(bot, register_command, salas)


En: /idiomas/es.json
---

"stats": {
  "message": "📊 Estadísticas de la partida\n\nTotal de partidas: {total}\nVictorias: {wins}\nPuntos acumulados: {points}"
}


RECOMENDACIONES:
================

- Siempre usa el sistema de idiomas (utils.idiomas)
- Para textos simples: obtener_texto('seccion.clave')
- Para textos con variables: formatear_texto('seccion.clave', var1=valor1, var2=valor2)
- Mantén la estética del juego intacta
- Si necesitas callbacks, registra con @register_callback('prefijo_')
- Si necesitas acceso a salas o base de datos, pásalos como parámetros
"""

from commands.stats import register_stats_command

# ... después de registrar otros comandos ...

register_stats_command(bot, register_command, salas)


PARÁMETROS DISPONIBLES
=======================

- bot: Instancia de TeleBot (para enviar mensajes)
- register_command: Decorador para registrar comandos
- register_callback: Decorador para registrar callbacks
- salas: Dict global con las salas activas
- registrar_jugador: Función de db_handler
- guardar_respuesta: Función de db_handler
- actualizar_votos: Función de db_handler
- etc.


ESTRUCTURA GENERAL
==================

def register_<nombre>_command(bot, register_command, <parámetros_opcionales>):
    @register_command('<nombre>')
    def <nombre>(message):
        '''Descripción del comando'''
        # Tu lógica aquí
        safe_reply(bot, message, "Respuesta")


MANTENER LA ESTÉTICA DEL JUEGO
==============================

Usa estos emojis en los comandos para mantener consistencia:

- 🎮 Juego
- 📊 Estadísticas
- 📝 Información
- ✅ Éxito
- ❌ Error
- ⚠️ Advertencia
- 🏆 Victoria/Ranking
- 🔔 Notificación
- 🚀 Inicio/Acción
- 🛑 Stop/Espera
- 📖 Ayuda/Instrucciones
"""