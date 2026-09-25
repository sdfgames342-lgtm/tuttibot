import ast
import os

def obtener_imports_db(archivo):
    funciones = []
    with open(archivo, 'r') as f:
        tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == 'core.db':
                for n in node.names:
                    funciones.append(n.name)
    return funciones

db_actual = []
with open('core/db.py', 'r') as f:
    tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            db_actual.append(node.name)

print(f"🔍 Analizando comandos...")
faltantes = set()
for cmd in os.listdir('commands'):
    if cmd.endswith('.py') and cmd != '__init__.py':
        try:
            reqs = obtener_imports_db(f'commands/{cmd}')
            for r in reqs:
                if r not in db_actual:
                    faltantes.add(r)
        except:
            continue

if faltantes:
    print(f"❌ FALTAN ESTAS FUNCIONES EN db.py:")
    for f in sorted(faltantes):
        if f != 'FRASES_GLOBALES':
            print(f"def {f}(*args, **kwargs): return None")
else:
    print("✅ Todo parece estar en orden.")
