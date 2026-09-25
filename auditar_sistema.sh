#!/bin/bash

echo "🧹 1. Eliminando caché de Python (__pycache__) recursivamente..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

echo "🔍 2. Analizando discrepancias en core/db.py..."
DB_FILE="core/db.py"
COM_DIR="commands"

# Extraer funciones declaradas actualmente en db.py
grep "def " "$DB_FILE" | sed 's/def //g' | cut -d'(' -f1 | tr -d ' ' | sort | uniq > declaradas.txt

# Extraer lo que los comandos REALMENTE intentan importar
grep -h "from core.db import" "$COM_DIR"/*.py | sed 's/from core.db import //g' | tr ',' '\n' | tr -d ' ' | sort | uniq > requeridas.txt

echo "-----------------------------------------------"
echo "❌ FUNCIONES REQUERIDAS QUE NO ESTÁN EN DB.PY:"
echo "-----------------------------------------------"
comm -23 requeridas.txt declaradas.txt

echo "-----------------------------------------------"
echo "🛠️ 3. Generando parche automático para core/db.py..."
