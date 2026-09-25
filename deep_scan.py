import os
import importlib
import sys
from telebot import TeleBot

# Mock de Token para la prueba
bot = TeleBot("12345:MOCK_TOKEN")

def auditoria_profesional():
    sys.path.append(os.getcwd())
    print(f"🚀 INICIANDO AUDITORÍA DINÁMICA DE COMANDOS")
    print("="*60)

    comandos_path = "commands"
    # Escaneo recursivo para incluir carpetas como banca, montecarlo, etc.
    modulos_encontrados = []
    for root, dirs, files in os.walk(comandos_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(os.path.join(root, file), os.getcwd())
                mod_path = rel_path.replace(os.sep, ".").replace(".py", "")
                modulos_encontrados.append(mod_path)

    for mod_path in modulos_encontrados:
        # Limpiar handlers antes de cargar el siguiente módulo
        bot.message_handlers = []
        
        try:
            # Intentamos cargar el módulo inyectando nuestro bot mock
            # Nota: Esto asume que tus archivos hacen 'from core.loader import bot' 
            # o reciben el bot de alguna forma.
            module = importlib.import_module(mod_path)
            
            # Extraer comandos registrados en este archivo
            comandos_registrados = []
            if hasattr(bot, 'message_handlers'):
                for handler in bot.message_handlers:
                    if 'commands' in handler['filters']:
                        comandos_registrados.extend(handler['filters']['commands'])
            
            status = "✅ OK" if comandos_registrados else "⚠️ NO CMDS"
            print(f"{status} | Módulo: {mod_path.ljust(30)}")
            
            if comandos_registrados:
                print(f"      └─ Comandos: {', '.join(['/' + c for c in comandos_registrados])}")

        except Exception as e:
            print(f"❌ ERROR | Módulo: {mod_path.ljust(30)}")
            print(f"      └─ Motivo: {str(e)}")

    print("="*60)
    print("Auditoría finalizada.")

if __name__ == "__main__":
    # Necesitamos asegurar que el entorno sea similar al de ejecución real
    # Si core.db necesita inicializarse, se hace aquí.
    from core.db import inicializar_db
    inicializar_db()
    auditoria_profesional()

