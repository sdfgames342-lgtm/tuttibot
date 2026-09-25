-- Parámetros de asimetría cambiaria
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('token_a_ficha_tasa', 10);
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('token_a_ficha_comision', 0);
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('token_a_ficha_limite_diario', 0);  -- 0 = sin límite

INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('ficha_a_token_tasa', 10);
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('ficha_a_token_comision', 10);   -- 10%
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('ficha_a_token_limite_diario', 100);

-- Parámetros de inflación
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('inflacion_actual', 0);
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('masa_monetaria', 0);
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('velocidad_circulacion', 0);
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('ultima_actualizacion_inflacion', '');

-- Tabla para inversiones a plazo fijo
CREATE TABLE IF NOT EXISTS inversiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    capital INTEGER NOT NULL,
    tasa_aplicada REAL NOT NULL,
    periodos INTEGER NOT NULL,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP,
    activa INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);
