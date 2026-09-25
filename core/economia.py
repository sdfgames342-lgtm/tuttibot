"""
Motor de simulación macroeconómica para Itsuki EdTech.
Basado en la Teoría Cuantitativa del Dinero (Fisher) y la Ecuación de Fisher.
"""
import sqlite3, datetime, logging
from core.db import get_connection, get_config, set_config

logger = logging.getLogger(__name__)

def calcular_masa_monetaria():
    """Suma total de saldos de todos los usuarios."""
    conn = get_connection()
    cur = conn.execute("SELECT COALESCE(SUM(monto), 0) FROM banco_ledger")
    total = cur.fetchone()[0]
    cur = conn.execute("SELECT COALESCE(SUM(tokens * 100), 0) FROM itsunario")
    total += cur.fetchone()[0]
    conn.close()
    return total

def calcular_velocidad_circulacion():
    """Promedio de transferencias diarias en los últimos 7 días."""
    conn = get_connection()
    cur = conn.execute("""
        SELECT COALESCE(COUNT(*), 0) FROM banco_ledger
        WHERE concepto LIKE 'Transferencia%' AND fecha >= date('now', '-7 days')
    """)
    transacciones = cur.fetchone()[0]
    conn.close()
    return transacciones / 7.0 if transacciones > 0 else 0.0

def calcular_inflacion():
    """
    Índice de inflación basado en la Teoría Cuantitativa del Dinero.
    M * V = P * T → P = (M * V) / T
    T (transacciones reales) lo estimamos como el consumo de servicios del bot (comisiones, etc.).
    La inflación es el cambio porcentual de P respecto a la medición anterior.
    """
    M = calcular_masa_monetaria()
    V = calcular_velocidad_circulacion()
    T = max(1, V * 0.8)  # Estimación: el 80% de la velocidad son transacciones reales
    P_actual = (M * V) / T
    
    P_anterior = float(get_config('inflacion_actual') or 0)
    if P_anterior == 0:
        inflacion = 0.0
    else:
        inflacion = ((P_actual - P_anterior) / P_anterior) * 100
    
    set_config('masa_monetaria', str(int(M)))
    set_config('velocidad_circulacion', str(round(V, 2)))
    set_config('inflacion_actual', str(round(P_actual, 2)))
    set_config('ultima_actualizacion_inflacion', datetime.datetime.now().isoformat())
    
    return round(inflacion, 2)

def calcular_tasa_interes():
    """
    Ecuación de Fisher: i = r + π
    i = tasa nominal, r = tasa real (base 2%), π = inflación esperada
    """
    inflacion = float(get_config('inflacion_actual') or 0)
    tasa_real = 2.0  # Tasa real base del 2%
    tasa_nominal = tasa_real + inflacion
    return max(0.5, round(tasa_nominal, 2))  # Mínimo 0.5% para evitar tasa negativa

def actualizar_indicadores():
    """Ejecuta el cálculo diario de inflación y ajusta tasas."""
    inflacion = calcular_inflacion()
    tasa = calcular_tasa_interes()
    set_config('tasa_interes_actual', str(tasa))
    logger.info(f"Indicadores actualizados: inflación {inflacion}%, tasa interés {tasa}%")
    return inflacion, tasa
