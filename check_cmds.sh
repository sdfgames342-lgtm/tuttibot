#!/bin/bash
echo -e "\033[1;36m🔍 ANALIZANDO ESTADO DE COMANDOS Y DB...\033[0m"

# 1. Verificar cuál base de datos es la real
DB_TUTTE=$(du -h tutte_game.db | cut -f1)
DB_TUTTI=$(du -h tutti_game.db | cut -f1)
echo -e "\n📦 Bases de datos detectadas:"
echo -e "   - tutte_game.db: $DB_TUTTE"
echo -e "   - tutti_game.db: $DB_TUTTI"

# 2. Buscar imports rotos o archivos faltantes en los comandos
echo -e "\n🛠️ Verificando integridad de archivos .py en commands/:"
for file in commands/*.py; do
    python3 -m py_compile "$file" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "   ✅ $(basename $file): Sintaxis OK"
    else
        echo -e "   ❌ $(basename $file): ERROR DE SINTAXIS"
    fi
done

# 3. Detectar discrepancias en la tabla 'jugadores' (La más usada)
echo -e "\n📊 Verificando tabla 'jugadores' en tutte_game.db:"
sqlite3 tutte_game.db "PRAGMA table_info(jugadores);" | cut -d'|' -f2 > cols_tutte.txt
sqlite3 tutti_game.db "PRAGMA table_info(jugadores);" | cut -d'|' -f2 > cols_tutti.txt

diff cols_tutte.txt cols_tutti.txt > /dev/null
if [ $? -ne 0 ]; then
    echo -e "   ⚠️ ALERTA: Las bases de datos tienen columnas distintas."
else
    echo -e "   ✅ Estructura de tablas consistente."
fi

# 4. Listar comandos que podrían fallar por falta de columnas en DB
echo -e "\n🕵️ Buscando posibles fallos por columnas faltantes:"
for col in "premium_status" "afinidad" "sudo_level"; do
    grep -q "$col" cols_tutte.txt
    if [ $? -ne 0 ]; then
        echo -e "   ❌ Falta '$col' en DB. Comandos que usan esto fallarán."
        grep -l "$col" commands/*.py | xargs -n1 basename | sed 's/^/      -> /'
    fi
done

rm cols_tutte.txt cols_tutti.txt
