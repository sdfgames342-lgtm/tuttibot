"""Motor de pagos de Montecarlo con RTP ajustable."""

def obtener_rtp():
    from core.db import get_connection
    conn = get_connection()
    cur = conn.execute("SELECT valor FROM itsunario_limites WHERE clave = 'rtp_montecarlo'")
    row = cur.fetchone()
    conn.close()
    return float(row[0]) / 100.0 if row else 0.90

def calcular_premio(apuesta, probabilidad_real, rtp=None):
    """Premio bruto con margen de la casa aplicado."""
    if rtp is None:
        rtp = obtener_rtp()
    if probabilidad_real <= 0 or probabilidad_real > 1:
        return 0
    multiplicador = (1.0 / probabilidad_real) * rtp
    return int(apuesta * multiplicador)

def registrar_margen(user_id, monto_apostado, premio_pagado):
    """Registra el margen de la casa en el ledger."""
    margen = monto_apostado - premio_pagado  # positivo = ganancia del sistema
    if margen <= 0:
        return
    from core.db import get_connection
    conn = get_connection()
    conn.execute("INSERT INTO banco_ledger (user_id, monto, concepto) VALUES (?, ?, ?)",
                 (0, margen, "Margen Montecarlo"))
    conn.commit()
    conn.close()
