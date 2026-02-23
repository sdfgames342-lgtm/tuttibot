from core_datos import registrar_usuario

registrar_comandos(bot, supabase):

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.reply_to(
            message,
            "🎮 Bienvenido al juego.\nEscribí algo para comenzar."
        )

    @bot.message_handler(commands=['ping'])
    def ping(message):
        bot.reply_to(message, "🏓 Pong")

    # Comandos faltantes (sin lógica implementada)
    @bot.message_handler(commands=['play'])
    def play(message):
        pass

    @bot.message_handler(commands=['extend'])
    def extend(message):
        pass

    @bot.message_handler(commands=['run'])
    def run(message):
        pass

    @bot.message_handler(commands=['cancel'])
    def cancel(message):
        pass

    @bot.message_handler(commands=['off'])
    def off(message):
        pass

    @bot.message_handler(commands=['join'])
    def join(message):
        pass

    @bot.message_handler(commands=['info'])
    def info(message):
        pass

    @bot.message_handler(commands=['token'])
    def token(message):
        pass

    @bot.message_handler(commands=['help'])
    def help(message):
        pass

    @bot.message_handler(commands=['cagon'])
    def cagon(message):
        pass

    @bot.message_handler(commands=['igroup'])
    def igroup(message):
        pass

    @bot.message_handler(commands=['top'])
    def top(message):
        pass

    @bot.message_handler(commands=['mtop'])
    def mtop(message):
        pass

    @bot.message_handler(commands=['gtop'])
    def gtop(message):
        pass

    @bot.message_handler(commands=['cus'])
    def cus(message):
        pass

    @bot.message_handler(commands=['recuperar'])
    def recuperar(message):
        pass

    @bot.message_handler(commands=['settings'])
    def settings(message):
        pass

    # Comandos de SuperAdmin
    @bot.message_handler(commands=['habilitar_grupo'])
    def habilitar_grupo(message):
        pass

    @bot.message_handler(commands=['tfadmin'])
    def tfadmin(message):
        pass

    @bot.message_handler(commands=['modadmin'])
    def modadmin(message):
        pass

    @bot.message_handler(commands=['untfadmin'])
    def untfadmin(message):
        pass

    @bot.message_handler(commands=['unmodadmin'])
    def unmodadmin(message):
        pass

    @bot.message_handler(commands=['mglist'])
    def mglist(message):
        pass

    @bot.message_handler(commands=['dntlist'])
    def dntlist(message):
        pass

    @bot.message_handler(commands=['blacklist'])
    def blacklist(message):
        pass

    @bot.message_handler(commands=['blackusers'])
    def blackusers(message):
        pass
    def require_registration(func):
    def wrapper(message, *args, **kwargs):
        t_id = message.from_user.id
        chat_id = message.chat.id

        cus, registrado = registrar_usuario(supabase, t_id)

        if chat_id != t_id and registrado:
            # Si se registró nuevo usuario en grupo
            bot.reply_to(
                message,
                f"❌ Debes escribirme en privado para comenzar a jugar. Tu CUS: `{cus}`"
            )
            return
        elif registrado:
            # En privado
            bot.reply_to(
                message,
                f"✅ Te registraste con éxito! Tu CUS: `{cus}`\nAhora podés usar /play, /join, /run."
            )

        return func(message, *args, **kwargs)
    return wrapperdef        pass

    @bot.message_handler(commands=['info'])
    def info(message):
        pass

    @bot.message_handler(commands=['token'])
    def token(message):
        pass

    @bot.message_handler(commands=['help'])
    def help(message):
        pass

    @bot.message_handler(commands=['cagon'])
    def cagon(message):
        pass

    @bot.message_handler(commands=['igroup'])
    def igroup(message):
        pass

    @bot.message_handler(commands=['top'])
    def top(message):
        pass

    @bot.message_handler(commands=['mtop'])
    def mtop(message):
        pass

    @bot.message_handler(commands=['gtop'])
    def gtop(message):
        pass

    @bot.message_handler(commands=['cus'])
    def cus(message):
        pass

    @bot.message_handler(commands=['recuperar'])
    def recuperar(message):
        pass

    @bot.message_handler(commands=['settings'])
    def settings(message):
        pass

    # Comandos de SuperAdmin
    @bot.message_handler(commands=['habilitar_grupo'])
    def habilitar_grupo(message):
        pass

    @bot.message_handler(commands=['tfadmin'])
    def tfadmin(message):
        pass

    @bot.message_handler(commands=['modadmin'])
    def modadmin(message):
        pass

    @bot.message_handler(commands=['untfadmin'])
    def untfadmin(message):
        pass

    @bot.message_handler(commands=['unmodadmin'])
    def unmodadmin(message):
        pass

    @bot.message_handler(commands=['mglist'])
    def mglist(message):
        pass

    @bot.message_handler(commands=['dntlist'])
    def dntlist(message):
        pass

    @bot.message_handler(commands=['blacklist'])
    def blacklist(message):
        pass

    @bot.message_handler(commands=['blackusers'])
    def blackusers(message):
        pass
