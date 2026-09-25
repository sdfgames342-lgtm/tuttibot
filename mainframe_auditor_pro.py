import os
import sys
import ast
import importlib
import sqlite3
import json
from pathlib import Path

# --- CONFIGURACIÓN DE ENTORNO ---
sys.path.append(os.getcwd())
BASE_DIR = Path.cwd()
COMMANDS_DIR = BASE_DIR / "commands"
CORE_DB = BASE_DIR / "core" / "db.py"
DB_PATH = BASE_DIR / "main_database.db"

class MainframeAuditor:
    def __init__(self):
        self.report = {
            "status": "PASS",
            "db_integrity": {},
            "modules": {},
            "dead_commands": []
        }

    def log(self, icon, msg):
        print(f"{icon} {msg}")

    def audit_db_layer(self):
        self.log("🗄️", "Verificando Capa de Datos...")
        try:
            import core.db as db
            required_funcs = ['get_db', 'conectar', 'inicializar_db', 'limpiar_ruleta_expirada']
            missing = [f for f in required_funcs if not hasattr(db, f)]
            
            if missing:
                self.log("❌", f"Funciones faltantes en core/db.py: {missing}")
                return False
            
            # Test de conexión real
            conn = db.conectar()
            self.log("✅", "Conexión a DB establecida.")
            conn.close()
            return True
        except Exception as e:
            self.log("❌", f"Error crítico en DB: {e}")
            return False

    def audit_commands_registration(self):
        self.log("🚀", "Iniciando Escaneo Dinámico de Comandos...")
        from telebot import TeleBot
        mock_bot = TeleBot("123:MOCK")
        
        # Encontrar todos los .py en commands/
        py_files = list(COMMANDS_DIR.rglob("*.py"))
        for pf in py_files:
            if pf.name == "__init__.py": continue
            
            # Convertir path a modulo (ej: commands.minigames.ruleta)
            rel_path = pf.relative_to(BASE_DIR)
            mod_name = str(rel_path).replace(os.sep, ".").replace(".py", "")
            
            try:
                # Limpiar handlers antes de cada import
                mock_bot.message_handlers = []
                module = importlib.import_module(mod_name)
                
                # REGLA DE ORO: Si el módulo tiene 'register_..._handlers', hay que llamarlo
                reg_func = [f for f in dir(module) if f.startswith("register_")]
                
                if reg_func:
                    for f in reg_func:
                        getattr(module, f)(mock_bot)
                
                # Contar comandos registrados
                cmds = []
                for handler in mock_bot.message_handlers:
                    if 'commands' in handler['filters']:
                        cmds.extend(handler['filters']['commands'])
                
                if cmds:
                    self.log("✅", f"{mod_name.ljust(30)} -> Comandos: {cmds}")
                else:
                    self.log("⚠️", f"{mod_name.ljust(30)} -> NO REGISTRA COMANDOS (Sordo)")
                    self.report["dead_commands"].append(mod_name)

            except Exception as e:
                self.log("🔥", f"{mod_name.ljust(30)} -> CRASH: {e}")

    def check_hardcoded_strings(self):
        self.log("🔍", "Buscando Strings sin i18n (Hardcoded)...")
        # Simulación de tu code_audit.py
        pass

    def run(self):
        print("\n" + "="*50)
        print("   ITSUKI MAINFRAME - AUDITORÍA PROFESIONAL v3.0")
        print("="*50 + "\n")
        
        db_ok = self.audit_db_layer()
        print("-" * 50)
        self.audit_commands_registration()
        print("-" * 50)
        
        if self.report["dead_commands"]:
            print(f"\n🛑 ALERTA: {len(self.report['dead_commands'])} módulos no están escuchando.")
            print("Tip: Verificá que loader.py llame a las funciones register_...")
        else:
            print("\n🎉 TODO OK: El sistema es coherente.")

if __name__ == "__main__":
    auditor = MainframeAuditor()
    auditor.run()
