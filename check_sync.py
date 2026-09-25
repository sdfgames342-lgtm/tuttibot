import os
import importlib
import sys

# Configurar el entorno para que reconozca los módulos locales
sys.path.append(os.getcwd())

def ejecutar_auditoria():
    print("🔍 Iniciando auditoría de sincronización de módulos...")
    print("-" * 50)
    
    comandos_path = "commands"
    modulos = [f[:-3] for f in os.listdir(comandos_path) if f.endswith(".py") and f != "__init__.py"]
    
    exitos = 0
    errores = 0
    detalles_errores = []

    for mod in modulos:
        nombre_modulo = f"commands.{mod}"
        try:
            # Forzar la carga del módulo
            importlib.import_module(nombre_modulo)
            print(f"✅ {mod.ljust(15)}: Sincronizado")
            exitos += 1
        except ImportError as e:
            msg = f"❌ {mod.ljust(15)}: Error de Importación -> {e}"
            print(msg)
            detalles_errores.append(msg)
            errores += 1
        except Exception as e:
            msg = f"⚠️ {mod.ljust(15)}: Error Crítico -> {type(e).__name__}: {e}"
            print(msg)
            detalles_errores.append(msg)
            errores += 1

    print("-" * 50)
    print(f"RESUMEN: {exitos} operativos, {errores} fallidos.")
    
    if errores > 0:
        print("\nLista de funciones faltantes detectadas:")
        for err in detalles_errores:
            if "cannot import name" in err:
                print(f"  > {err.split('from')[0].split('name')[-1].strip()}")

if __name__ == "__main__":
    ejecutar_auditoria()

