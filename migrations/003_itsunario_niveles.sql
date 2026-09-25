-- Añadir columna de nivel (si no se hizo)
ALTER TABLE itsunario ADD COLUMN nivel_ranking INTEGER DEFAULT 0;

-- Insertar más límites
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('max_fichas_apuesta', 500);
INSERT OR IGNORE INTO itsunario_limites (clave, valor) VALUES ('min_fichas_apuesta', 1);
