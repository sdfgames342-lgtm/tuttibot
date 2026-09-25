#!/bin/bash
cd "$(dirname "$0")"

LOG_FILE="watchdog.log"
RESTART_COUNT=0
LAST_RESTART=0
MAX_RESTARTS=5
SLEEP_BETWEEN=30
COOLDOWN=300

while true; do
    if [ -f SHUTDOWN_FLAG ]; then
        echo "[$(date)] Watchdog detenido por flag SHUTDOWN_FLAG" >> "$LOG_FILE"
        exit 0
    fi

    if pgrep -f "python3 main.py" > /dev/null; then
        if [ $RESTART_COUNT -gt 0 ] && [ $(date +%s) -gt $((LAST_RESTART + COOLDOWN)) ]; then
            RESTART_COUNT=0
        fi
        sleep $SLEEP_BETWEEN
        continue
    fi

    echo "[$(date)] ⚠️ Itsuki caído. Reiniciando..." | tee -a "$LOG_FILE"

    if [ $RESTART_COUNT -ge $MAX_RESTARTS ]; then
        echo "[$(date)] 🛑 Demasiados reinicios. Esperando $COOLDOWN segundos..." | tee -a "$LOG_FILE"
        sleep $COOLDOWN
        RESTART_COUNT=0
    fi

    # Eliminar webhook por si acaso
    curl -s "https://api.telegram.org/bot$(grep TELEGRAM_TOKEN .env | cut -d= -f2)/deleteWebhook" > /dev/null 2>&1

    nohup python3 main.py > bot_runtime.log 2>&1 &

    RESTART_COUNT=$((RESTART_COUNT + 1))
    LAST_RESTART=$(date +%s)
    echo "[$(date)] ✅ Itsuki reiniciado (intento #$RESTART_COUNT)" | tee -a "$LOG_FILE"
    sleep $SLEEP_BETWEEN
done
