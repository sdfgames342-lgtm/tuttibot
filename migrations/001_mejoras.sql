-- Vistas de conveniencia
CREATE VIEW IF NOT EXISTS v_grupos_activos AS
SELECT * FROM control_grupos WHERE estado = 'ACTIVO';

CREATE VIEW IF NOT EXISTS v_ranking_jugadores AS
SELECT user_id, nombre, puntos_historicos
FROM jugadores ORDER BY puntos_historicos DESC;

-- Normalización de partidas (elimina JSON en columnas)
CREATE TABLE IF NOT EXISTS partida_jugadores (
    chat_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    nombre TEXT,
    PRIMARY KEY (chat_id, user_id),
    FOREIGN KEY (chat_id) REFERENCES partidas(chat_id),
    FOREIGN KEY (user_id) REFERENCES jugadores(user_id)
);

CREATE TABLE IF NOT EXISTS partida_categorias (
    chat_id TEXT NOT NULL,
    orden INTEGER NOT NULL,
    categoria TEXT NOT NULL,
    PRIMARY KEY (chat_id, orden),
    FOREIGN KEY (chat_id) REFERENCES partidas(chat_id)
);

-- Migrar datos existentes desde las columnas JSON
INSERT OR REPLACE INTO partida_jugadores (chat_id, user_id, nombre)
SELECT p.chat_id, CAST(j.key AS INTEGER), j.value
FROM partidas p, json_each(p.jugadores) j
WHERE p.jugadores IS NOT NULL AND p.jugadores != '';

INSERT OR REPLACE INTO partida_categorias (chat_id, orden, categoria)
SELECT p.chat_id, CAST(c.key AS INTEGER), c.value
FROM partidas p, json_each(p.categorias) c
WHERE p.categorias IS NOT NULL AND p.categorias != '';
