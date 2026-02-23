from core_datos import registrar_usuario

def registrar_comandos(bot, supabase):

    # Decorador para verificar/registrar usuario
    def require_registration(func):
        def wrapper(message, *args, **kwargs):
            user_id = message.from_user.id
            chat_id = message.chat.id

            # Llamar a la función que registra/obtiene usuario en Supabase
            cus, es_nuevo = registrar_usuario(supabase, user_id)

            # Si el mensaje es en grupo y el usuario acaba de registrarse (o no existía)
            if chat_id != user_id and es_nuevo:
                bot.reply_to(
                    message,
                    f"❌ Debes escribirme en privado para comenzar a jugar. Tu CUS: `{cus}`"
                )
                return  # No ejecuta el comando original
            elif chat_id == user_id and es_nuevo:
                # En privado y es registro nuevo
                bot.reply_to(
                    message,
                    f"✅ ¡Te registraste con éxito! Tu CUS: `{cus}`\nAhora podés usar /play, /join, /run."
                )
                # Continúa con el comando original (si aplica)
            # Si el usuario ya existía, simplemente ejecuta el comando
            return func(message, *args, **kwargs)
        return wrapper

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.reply_to(
            message,
            "🎮 Bienvenido al juego.\nEscribí algo para comenzar."
        )

    @bot.message_handler(commands=['ping'])
    def ping(message):
        bot.reply_to(message, "🏓 Pong")

    # Comandos que requieren registro (todos excepto start, ping y help)
    @bot.message_handler(commands=['play'])
    @require_registration
    def play(message):
        pass

    @bot.message_handler(commands=['extend'])
    @require_registration
    def extend(message):
        pass

    @bot.message_handler(commands=['run'])
    @require_registration
    def run(message):
        pass

    @bot.message_handler(commands=['cancel'])
    @require_registration
    def cancel(message):
        pass

    @bot.message_handler(commands=['off'])
    @require_registration
    def off(message):
        pass

    @bot.message_handler(commands=['join'])
    @require_registration
    def join(message):
        pass

    @bot.message_handler(commands=['info'])
    @require_registration
    def info(message):
        pass

    @bot.message_handler(commands=['token'])
    @require_registration
    def token(message):
        pass

    @bot.message_handler(commands=['help'])
    def help(message):
        help_text = (
            "🛠️ **Comandos de SuperAdmin:**\n"
            "/habilitar_grupo - Autoriza un grupo\n"
            "/tfadmin <id> - Convierte a superadmin\n"
            "/modadmin <id> - Convierte a moderador\n"
            "/untfadmin <id> - Quita superadmin\n"
            "/unmodadmin <id> - Quita moderador\n"
            "/mglist - Lista grupos autorizados\n"
            "/dntlist - Lista grupos deshabilitados\n"
            "/blacklist - Ver lista negra\n"
            "/blackusers <id> <motivo> - Añadir a lista negra\n\n"
            "📚 **Comandos públicos:**\n"
            "/start - Iniciar bot (solo privado)\n"
            "/help - Esta ayuda\n"
            "/play - Crear una sala de juego\n"
            "/cagon - Rendirse (pierdes 2 puntos)\n"
            "/info - Información y estadísticas propias\n"
            "/igroup - Estadísticas del grupo\n"
            "/top - Ranking local del grupo\n"
            "/mtop - Ranking global de jugadores\n"
            "/gtop - Ranking de grupos\n"
            "/ping - Verificar si el bot está vivo\n"
            "/cus - Ver tu CUS (solo privado)\n"
            "/recuperar - Recuperar cuenta (solo privado)\n"
            "/settings - Configuración (solo privado)"
        )
        bot.reply_to(message, help_text, parse_mode="Markdown")

    @bot.message_handler(commands=['cagon'])
    @require_registration
    def cagon(message):
        pass

    @bot.message_handler(commands=['igroup'])
    @require_registration
    def igroup(message):
        pass

    @bot.message_handler(commands=['top'])
    @require_registration
    def top(message):
        pass

    @bot.message_handler(commands=['mtop'])
    @require_registration
    def mtop(message):
        pass

    @bot.message_handler(commands=['gtop'])
    @require_registration
    def gtop(message):
        pass

    @bot.message_handler(commands=['cus'])
    @require_registration
    def cus(message):
        pass

    @bot.message_handler(commands=['recuperar'])
    @require_registration
    def recuperar(message):
        pass

    @bot.message_handler(commands=['settings'])
    @require_registration
    def settings(message):
        pass

    # Comandos de SuperAdmin (también requieren registro, pero luego verificarán permisos)
    @bot.message_handler(commands=['habilitar_grupo'])
    @require_registration
    def habilitar_grupo(message):
        pass

    @bot.message_handler(commands=['tfadmin'])
    @require_registration
    def tfadmin(message):
        pass

    @bot.message_handler(commands=['modadmin'])
    @require_registration
    def modadmin(message):
        pass

    @bot.message_handler(commands=['untfadmin'])
    @require_registration
    def untfadmin(message):
        pass

    @bot.message_handler(commands=['unmodadmin'])
    @require_registration
    def unmodadmin(message):
        pass

    @bot.message_handler(commands=['mglist'])
    @require_registration
    def mglist(message):
        pass

    @bot.message_handler(commands=['dntlist'])
    @require_registration
    def dntlist(message):
        pass

    @bot.message_handler(commands=['blacklist'])
    @require_registration
    def blacklist(message):
        pass

    @bot.message_handler(commands=['blackusers'])
    @require_registration
    def blackusers(message):
        pass

    # Manejador para mensajes de texto (no comandos)
    @bot.message_handler(func=lambda message: True)
    @require_registration
    def handle_message(message):
        # Aquí se puede llamar a cerebro
        from cerebro import procesar_mensaje
        respuesta = procesar_mensaje(message, supabase)
        bot.reply_to(message, respuesta)
