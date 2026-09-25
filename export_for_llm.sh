#!/usr/bin/env bash
# Exporta la estructura y código fuente del bot Itsuki Mainframe para LLMs.
# Uso: bash export_for_llm.sh
# Salida: itsuki_export.txt

OUT="itsuki_export.txt"
echo "📦 Generando $OUT ..."

{
  echo "============================================================"
  echo " ITSŲKI MAINFRAṀE - FULL PROJECT EXPORT"
  echo " Generated: $(date)"
  echo "============================================================"
  echo ""

  echo "📁 DIRECTORY TREE"
  echo "----------------"
  tree -a --noreport -I '__pycache__|*.pyc|*.o|*.so' .
  echo ""

  # ── Archivos raíz ──
  for f in main.py Procfile requirements.txt schema.sql; do
    if [ -f "$f" ]; then
      echo ""
      echo "═══════════════════════════════════════════════"
      echo " FILE: $f"
      echo "═══════════════════════════════════════════════"
      cat "$f"
    fi
  done

  # ── core/ ──
  echo ""
  echo "──────────────────────────────────"
  echo " CORE MODULES"
  echo "──────────────────────────────────"
  for f in core/*.py; do
    echo ""
    echo "══════════ $f ══════════"
    cat "$f"
  done

  # ── utils/ ──
  echo ""
  echo "──────────────────────────────────"
  echo " UTILS"
  echo "──────────────────────────────────"
  for f in utils/*.py; do
    echo ""
    echo "══════════ $f ══════════"
    cat "$f"
  done

  # ── commands/ (principales y subcarpetas) ──
  echo ""
  echo "──────────────────────────────────"
  echo " COMMANDS"
  echo "──────────────────────────────────"
  for f in commands/*.py commands/*/*.py; do
    if [ -f "$f" ]; then
      echo ""
      echo "══════════ $f ══════════"
      cat "$f"
    fi
  done

  # ── migrations/ ──
  echo ""
  echo "──────────────────────────────────"
  echo " MIGRATIONS"
  echo "──────────────────────────────────"
  for f in migrations/*.sql; do
    [ -f "$f" ] || continue
    echo ""
    echo "══════════ $f ══════════"
    cat "$f"
  done

  # ── idiomas JSON ──
  echo ""
  echo "──────────────────────────────────"
  echo " I18N FILES"
  echo "──────────────────────────────────"
  for f in idiomas/*.json; do
    echo ""
    echo "══════════ $f ══════════"
    cat "$f"
  done

  # ── Tests / auditoría ──
  echo ""
  echo "──────────────────────────────────"
  echo " TESTS & AUDIT"
  echo "──────────────────────────────────"
  for f in test_bot.py code_audit.py db_verifier.py; do
    if [ -f "$f" ]; then
      echo ""
      echo "══════════ $f ══════════"
      cat "$f"
    fi
  done

  # ── Resumen técnico ──
  echo ""
  echo "──────────────────────────────────"
  echo " TECHNICAL SUMMARY"
  echo "──────────────────────────────────"
  echo "Architecture: Modular plugin system (commands/), SQLite DB (19 tables), i18n JSON, RTP-based casino, COBOL bank."
  echo "Key modules:"
  echo "  core/db.py       - Database access layer"
  echo "  core/loader.py    - Dynamic command loader"
  echo "  core/kernel.py    - System threads"
  echo "  core/economia.py  - Inflation / interest engine"
  echo "  commands/montecarlo/ - Card games (War, Blackjack, Truco, etc.)"
  echo "  commands/tuttifrutti/ - Word game"
  echo "  commands/minigames/   - Exams, duels, traveling book"
  echo "  commands/banca/       - COBOL-powered banking"
  echo "  utils/idiomas.py      - i18n engine"
  echo "  utils/decorators.py   - Visual ledger"
  echo "  utils/message_styles.py - Font rendering"
  echo ""
  echo "Database tables: jugadores, partidas, respuestas, calculo_puntos, control_grupos, config_bot,"
  echo "    metricas_marketing, log_eventos, stickers_cartas, partidas_guerra, partida_jugadores,"
  echo "    partida_categorias, itsunario, itsunario_canjes, itsunario_limites, banco_ledger, inversiones"
  echo ""
  echo "Economy: Itsunario tokens (earned via streaks/levels), fichas (casino chips),"
  echo "    asymmetric exchange, inflation-adjusted interest, RTP 90% on casino games."
  echo ""
  echo "Run with: python3 main.py"
  echo ""
  echo "─ End of export ─"
} > "$OUT"

echo "✅ Exportado a $OUT"
