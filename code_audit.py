#!/usr/bin/env python3
"""
ITSŲKI MAINFRAṀE AUDIT · v2.0 · DETECCIÓN REAL
Solo marca cadenas que son argumentos literales de funciones de salida.
Ignora claves de diccionario, f‑strings, formatos de log y URLs.
"""
import os, re, ast
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path.cwd()
REPORT_FILE = PROJECT_ROOT / "audit_report.log"

COMMANDS_DIR = "commands"

IGNORE_DIRS = {'__pycache__', '.git', 'itsuki-web', 'backups', 'logs', 'tools', 'itsuki-bot'}
EXCLUDE_FILES = {'code_audit.py', 'bot.py', 'activar_sizania.py', 'mainframe_validator.py',
                 'itsuki.py', 'main.py'}

PYTHON_EXT = '.py'
I18N_FUNCTIONS = {'obtener_texto', 'formatear_texto'}
SALIDA_FUNCS = {'safe_reply', 'send_message', 'send_photo', 'reply_to',
                'answer_callback_query', 'edit_message_text', 'edit_message_caption',
                'send_audio', 'send_video', 'send_document', 'send_voice',
                'msg_queue.put'}

HTML_TAG_RE = re.compile(r'<[a-zA-Z/][^>]*>')
URL_RE = re.compile(r'https?://\S+')
SQL_REAL_RE = re.compile(r'\b(SELECT\s+.*\bFROM|INSERT\s+INTO|UPDATE\s+.*\bSET|DELETE\s+FROM)\b', re.IGNORECASE)
STRUCTURAL_CHARS_RE = re.compile(r'[─┌┐└┘│╭╰⊛⟐⟪⟫✍╔╗╚╝║═]')

issues = {
    "hardcoded_strings": [],
    "missing_formatters": [],
    "html_in_strings": [],
    "commands_outside_commands": [],
    "duplicate_image_calls": [],
    "start_user_validation": [],
    "schema": [],
    "structure": [],
    "sql_outside_db": [],
    "visual_outside_decorators": [],
}
hardcoded_by_file = defaultdict(int)

statistics = {
    "total_files": 0, "total_py_files": 0, "total_lines": 0,
    "classes": 0, "functions": 0, "decorators": 0,
    "i18n_calls": 0, "formatter_calls": 0,
}

def color(text, code): return f"\033[{code}m{text}\033[0m"
def bold(s): return color(s, "1;37")
def yellow(s): return color(s, "1;33")
def green(s): return color(s, "1;32")
def cyan(s): return color(s, "1;36")

def inside_fstring(node):
    parent = getattr(node, 'parent', None)
    while parent is not None:
        if isinstance(parent, (ast.JoinedStr, ast.FormattedValue)):
            return True
        parent = getattr(parent, 'parent', None)
    return False

def is_argument_of_output(node):
    """Determina si el nodo Constant es un argumento directo de una función de salida."""
    parent = getattr(node, 'parent', None)
    if parent is None:
        return False
    if isinstance(parent, ast.Call):
        func = parent.func
        if isinstance(func, ast.Attribute) and func.attr in SALIDA_FUNCS:
            return True
        if isinstance(func, ast.Name) and func.id in SALIDA_FUNCS:
            return True
    return False

def add_parents(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

def analyze_python_file(filepath):
    rel = filepath.relative_to(PROJECT_ROOT)
    if 'tools/' in str(rel):
        return
    with open(filepath, 'r', errors='ignore') as f:
        content = f.read()
        lines = content.splitlines()
    statistics['total_lines'] += len(lines)
    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError:
        return
    add_parents(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            statistics['classes'] += 1
        elif isinstance(node, ast.FunctionDef):
            statistics['functions'] += 1
            statistics['decorators'] += len(node.decorator_list)

        if isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value.strip()) > 3:
            val = node.value
            lineno = node.lineno
            if inside_fstring(node):
                continue
            if not is_argument_of_output(node):
                continue
            if '{' in val or '}' in val:
                continue
            if URL_RE.search(val):
                continue
            if SQL_REAL_RE.search(val):
                continue
            if val in ('HTML', 'Markdown', 'video', 'audio', 'document', 'voice'):
                continue

            issues["hardcoded_strings"].append((str(rel), lineno, 0, val[:70].replace('\n', ' ')))
            hardcoded_by_file[str(rel)] += 1

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            fname = node.func.attr
            if fname in SALIDA_FUNCS:
                statistics['formatter_calls'] += 1
                if fname in ('send_message', 'send_photo'):
                    if lineno <= len(lines):
                        if 'safe_reply' not in lines[lineno-1]:
                            issues["missing_formatters"].append((str(rel), lineno, 0, f"Llamada directa a {fname} sin safe_reply"))

        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if HTML_TAG_RE.search(node.value):
                if lineno <= len(lines) and ('parse_mode' in lines[lineno-1].lower() and 'html' in lines[lineno-1].lower()):
                    continue
                issues["html_in_strings"].append((str(rel), lineno, 0, node.value[:70].replace('\n', ' ')))

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in I18N_FUNCTIONS:
            statistics['i18n_calls'] += 1

    if f'/{COMMANDS_DIR}/' not in str(filepath.as_posix()):
        for i, line in enumerate(lines, start=1):
            if re.search(r'@\w+\.message_handler\(commands\s*=\s*\[', line):
                issues["commands_outside_commands"].append((str(rel), i, 0, line.strip()))

def add_parents(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

def analyze_schema_sql():
    pass

def analyze_structure():
    main_py = PROJECT_ROOT / 'main.py'
    if main_py.exists() and main_py.stat().st_size > 5120:
        issues["structure"].append("main.py supera 5KB.")

def print_header():
    print(bold("\n┌" + "─"*70 + "┐"))
    print(bold("│") + cyan(" ITSŲKI AUDIT · v2.0 · SOLO SALIDA REAL ") + bold("│"))
    print(bold("└" + "─"*70 + "┘\n"))

def print_section(title, lst, icon="⚠️", full=False):
    if not lst: return
    print(yellow(f"\n{icon} {title} ({len(lst)} incidencias)"))
    max_items = len(lst) if full else 10
    for item in lst[:max_items]:
        if isinstance(item, str): print(f"   ▶ {item}")
        else: print(f"   ▶ {item[0]}:{item[1]} → {item[3]}")
    if not full and len(lst) > max_items: print(f"   ... y {len(lst)-max_items} más")

def main():
    print_header()
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith(PYTHON_EXT) and file not in EXCLUDE_FILES:
                fp = Path(root) / file
                statistics['total_py_files'] += 1
                analyze_python_file(fp)
    statistics['total_files'] = sum(1 for _ in PROJECT_ROOT.rglob('*') if _.is_file() and not any(p in IGNORE_DIRS for p in _.parts))
    analyze_schema_sql()
    analyze_structure()

    print(green("\n📊 ESTADÍSTICAS GENERALES"))
    for k, v in statistics.items(): print(f"   {k.replace('_',' ')}: {v}")

    if hardcoded_by_file:
        total = sum(hardcoded_by_file.values())
        print(yellow(f"\n⚠️ Cadenas hardcodeadas reales (sin i18n): {total} total"))
        print("   Ranking por archivo:")
        for file, count in sorted(hardcoded_by_file.items(), key=lambda x: x[1], reverse=True):
            print(f"   ▶ {file}: {count}")
    else:
        print(green("   ✅ No se detectaron cadenas hardcodeadas."))

    print_section("Envíos sin safe_reply", issues["missing_formatters"], "🚫")
    print_section("Comandos fuera de 'commands/'", issues["commands_outside_commands"], "📂")

    total_issues = sum(len(v) for v in issues.values()) + sum(hardcoded_by_file.values())
    print(bold(f"\n🔎 {total_issues} incidencias encontradas en total."))

    with open(REPORT_FILE, 'w') as f:
        f.write("ITSUKI AUDIT REPORT v2.0\n" + "="*60 + "\n")
        f.write(f"Python files analizados: {statistics['total_py_files']}\n")
        if hardcoded_by_file:
            f.write("\n[Cadenas hardcodeadas reales]\n")
            for file, count in sorted(hardcoded_by_file.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {file}: {count}\n")
        for k, lst in issues.items():
            if lst:
                f.write(f"\n[{k}]\n")
                for item in lst:
                    if isinstance(item, str): f.write(f"  - {item}\n")
                    else: f.write(f"  {item[0]}:{item[1]} -> {item[3]}\n")
    print(cyan(f"📄 Reporte guardado en {REPORT_FILE}"))

if __name__ == "__main__":
    main()
