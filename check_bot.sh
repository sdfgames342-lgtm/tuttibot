#!/bin/bash
echo "--- Reporte de Procesos Itsuki ---"
PY_PROC=$(pgrep -f "python3 main.py")
WD_PROC=$(pgrep -f "watchdog.sh")

if [ -z "$PY_PROC" ]; then
    echo "✅ Bot: Offline"
else
    echo "⚠️  Bot: Activo (PID: $PY_PROC)"
fi

if [ -z "$WD_PROC" ]; then
    echo "✅ Watchdog: Offline"
else
    echo "⚠️  Watchdog: Activo (PID: $WD_PROC)"
fi

if [ ! -z "$PY_PROC" ] || [ ! -z "$WD_PROC" ]; then
    echo -e "\nPara limpiar todo usa: pkill -f watchdog.sh && pkill -9 python"
fi
