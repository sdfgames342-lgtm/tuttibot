# comandos.py
def registrar_comandos(bot, supabase):

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.reply_to(
            message,
            "🎮 Bienvenido al juego.\nEscribí algo para comenzar."
        )

    @bot.message_handler(commands=['ping'])
    def ping(message):
        bot.reply_to(message, "🏓 Pong")
