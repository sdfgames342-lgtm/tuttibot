import ast
import os

def auditar_archivo(path):
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    
    errores = []
    for node in ast.walk(tree):
        # Buscar llamadas a bot.send_message o safe_reply
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id
            
            if func_name in ["send_message", "safe_reply", "reply_to"]:
                # Verificar keywords (argumentos con nombre)
                for kw in node.keywords:
                    if func_name == "send_message" and kw.arg == "caption":
                        errores.append(f"❌ [LÍNEA {node.lineno}] 'caption' en mensaje de texto.")
                    if kw.arg == "raw":
                        errores.append(f"⚠️ [LÍNEA {node.lineno}] Argumento 'raw' detectado (Legacy).")
    return errores

print("🔍 INICIANDO AUDITORÍA DE SINTAXIS DINÁMICA...")
base_path = "./commands"
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith(".py"):
            full_path = os.path.join(root, file)
            errs = auditar_archivo(full_path)
            if errs:
                print(f"\nArchivo: {full_path}")
                for e in errs: print(e)
