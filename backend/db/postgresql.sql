-- Seleccionar la base de datos
\c gamc_db;
CREATE DATABASE gamc_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Bolivia.1252'
    LC_CTYPE = 'Spanish_Bolivia.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;
-- Tabla para datos de calidad del aire
CREATE TABLE aire (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sensor_id VARCHAR(50),
    temperatura DECIMAL(5,2),
    humedad DECIMAL(5,2),
    calidad_aire DECIMAL(6,2)
);

-- Tabla para datos de sonido
CREATE TABLE sonido (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sensor_id VARCHAR(50),
    nivel_ruido DECIMAL(6,2)
);

-- Tabla para datos soterrados
CREATE TABLE soterrado (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sensor_id VARCHAR(50),
    presion DECIMAL(6,2),
    vibracion DECIMAL(6,2)
);
