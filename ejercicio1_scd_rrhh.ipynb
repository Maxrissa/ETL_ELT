-- =============================================================================
-- EJERCICIO 1: Sistema SCD para Recursos Humanos
-- Motor: MySQL
-- Schema: Star Schema
-- Tablas: Dimensionales y Factuales con SCD Tipo 1, 2 y 3
-- =============================================================================
-- DESCRIPCION GENERAL:
--   Se construye un Data Warehouse para RRHH con dimensiones empleados,
--   departamentos y salarios. Se implementan los tres tipos de SCD:
--     - SCD Tipo 1: sobreescribe el valor (no guarda historia) -> sede empleado
--     - SCD Tipo 2: agrega fila nueva con fechas (historia completa) -> departamento
--     - SCD Tipo 3: guarda valor anterior en columna adicional -> salario
--   El schema es STAR porque la tabla de hechos apunta directamente a dimensiones
--   planas (no hay subdimensiones enlazadas = no snowflake).
--   Normalización: 3FN en tablas fuente, desnormalizado en dimensiones para performance.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 0. BASE DE DATOS
-- -----------------------------------------------------------------------------
DROP DATABASE IF EXISTS rrhh_dwh;
CREATE DATABASE rrhh_dwh CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE rrhh_dwh;

-- =============================================================================
-- 1. TABLAS FUENTE (Staging / OLTP simulado)
--    Representan los datos operacionales antes de transformar.
--    Normalizadas en 3FN: sin redundancia, cada atributo depende de PK.
-- =============================================================================

-- Tabla fuente: empleados
CREATE TABLE stg_empleados (
    empleado_id     INT             NOT NULL,
    nombre          VARCHAR(100)    NOT NULL,
    apellido        VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    UNIQUE,
    fecha_ingreso   DATE            NOT NULL,
    departamento    VARCHAR(80)     NOT NULL,
    cargo           VARCHAR(80)     NOT NULL,
    salario         DECIMAL(12,2)   NOT NULL,
    sede            VARCHAR(80)     NOT NULL,   -- cambia con SCD T1
    activo          TINYINT(1)      DEFAULT 1,
    PRIMARY KEY (empleado_id)
);

-- Tabla fuente: cambios de departamento (log operacional)
CREATE TABLE stg_cambios_departamento (
    cambio_id       INT             NOT NULL AUTO_INCREMENT,
    empleado_id     INT             NOT NULL,
    dept_anterior   VARCHAR(80),
    dept_nuevo      VARCHAR(80)     NOT NULL,
    fecha_cambio    DATE            NOT NULL,
    motivo          VARCHAR(200),
    PRIMARY KEY (cambio_id)
);

-- Tabla fuente: historial salarial (log operacional)
CREATE TABLE stg_historial_salario (
    historial_id    INT             NOT NULL AUTO_INCREMENT,
    empleado_id     INT             NOT NULL,
    salario_nuevo   DECIMAL(12,2)   NOT NULL,
    fecha_cambio    DATE            NOT NULL,
    tipo_ajuste     VARCHAR(50),    -- MERITO / PROMOCION / INFLACION
    PRIMARY KEY (historial_id)
);

-- =============================================================================
-- 2. DIMENSIONES DEL DWH (Star Schema)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- DIM_TIEMPO - Tabla dimensional de tiempo
-- Tipo: Dimensión estática/fija
-- Normalización: Desnormalizada (todos los atributos de fecha en una fila)
-- Relación con fact: 1:N (un día tiene muchos hechos)
-- -----------------------------------------------------------------------------
CREATE TABLE dim_tiempo (
    tiempo_sk       INT             NOT NULL AUTO_INCREMENT,  -- surrogate key
    fecha_full      DATE            NOT NULL,
    anio            SMALLINT        NOT NULL,
    trimestre       TINYINT         NOT NULL,
    mes             TINYINT         NOT NULL,
    nombre_mes      VARCHAR(20)     NOT NULL,
    semana_anio     TINYINT         NOT NULL,
    dia_semana      TINYINT         NOT NULL,
    nombre_dia      VARCHAR(20)     NOT NULL,
    es_fin_semana   TINYINT(1)      NOT NULL DEFAULT 0,
    PRIMARY KEY (tiempo_sk),
    UNIQUE KEY uq_fecha (fecha_full)
);

-- -----------------------------------------------------------------------------
-- DIM_DEPARTAMENTO - Tabla dimensional departamentos
-- Tipo: Dimensión con SCD TIPO 2 (historial completo de cambios)
-- Normalización: Desnormalizada para performance de consultas
-- Relación con fact: 1:N
-- SCD T2: cada cambio de departamento crea un NUEVO registro con nueva SK,
--         se mantienen fecha_inicio y fecha_fin, y flag es_actual.
-- -----------------------------------------------------------------------------
CREATE TABLE dim_departamento (
    dept_sk         INT             NOT NULL AUTO_INCREMENT,  -- surrogate key (SCD T2)
    dept_nk         INT             NOT NULL,                 -- natural key (empleado)
    nombre_dept     VARCHAR(80)     NOT NULL,
    division        VARCHAR(80),
    gerente         VARCHAR(100),
    ubicacion       VARCHAR(100),
    -- Campos SCD Tipo 2
    fecha_inicio    DATE            NOT NULL,
    fecha_fin       DATE,                                     -- NULL = registro vigente
    es_actual       TINYINT(1)      NOT NULL DEFAULT 1,
    PRIMARY KEY (dept_sk),
    INDEX idx_dept_nk (dept_nk),
    INDEX idx_dept_actual (dept_nk, es_actual)
);

-- -----------------------------------------------------------------------------
-- DIM_EMPLEADO - Tabla dimensional empleados (mezcla SCD T1 y T3)
-- Tipo: Dimensión principal
-- Normalización: Desnormalizada (atributos personales + cargo en una fila)
-- Relación con fact: 1:N
-- SCD T1: sede -> se sobreescribe, no se guarda historia
-- SCD T3: salario -> guarda salario_actual Y salario_anterior en columnas
-- -----------------------------------------------------------------------------
CREATE TABLE dim_empleado (
    empleado_sk         INT             NOT NULL AUTO_INCREMENT,  -- surrogate key
    empleado_nk         INT             NOT NULL,                  -- natural key (OLTP id)
    nombre              VARCHAR(100)    NOT NULL,
    apellido            VARCHAR(100)    NOT NULL,
    nombre_completo     VARCHAR(200)    GENERATED ALWAYS AS (CONCAT(nombre, ' ', apellido)) STORED,
    email               VARCHAR(150),
    fecha_ingreso       DATE            NOT NULL,
    cargo               VARCHAR(80)     NOT NULL,
    -- SCD Tipo 1: sede (sobreescribe sin historia)
    sede_actual         VARCHAR(80)     NOT NULL,
    -- SCD Tipo 3: salario (guarda actual + anterior)
    salario_actual      DECIMAL(12,2)   NOT NULL,
    salario_anterior    DECIMAL(12,2),                            -- NULL si no hubo cambio
    fecha_ultimo_ajuste DATE,
    tipo_ultimo_ajuste  VARCHAR(50),
    -- Control
    activo              TINYINT(1)      DEFAULT 1,
    fecha_creacion      DATETIME        DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (empleado_sk),
    UNIQUE KEY uq_empleado_nk (empleado_nk),
    INDEX idx_cargo (cargo),
    INDEX idx_sede (sede_actual)
);

-- =============================================================================
-- 3. TABLA DE HECHOS (FACT TABLE)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- FACT_RRHH_SNAPSHOT - Snapshot mensual del estado de cada empleado
-- Tipo: Factual tipo Snapshot periódico
-- Normalización: Desnormalizada (FK a dimensiones)
-- Schema: STAR (FK directo a dim_empleado, dim_departamento, dim_tiempo)
-- Granularidad: 1 fila por empleado por mes
-- Métricas: salario, dias_en_cargo, variacion_salarial
-- Relaciones:
--   fact -> dim_empleado     (N:1)
--   fact -> dim_departamento (N:1) -> versión SCD T2 vigente en ese momento
--   fact -> dim_tiempo       (N:1)
-- -----------------------------------------------------------------------------
CREATE TABLE fact_rrhh_snapshot (
    snapshot_sk             INT             NOT NULL AUTO_INCREMENT,
    -- Foreign Keys (Star Schema)
    empleado_sk             INT             NOT NULL,
    dept_sk                 INT             NOT NULL,
    tiempo_sk               INT             NOT NULL,
    -- Métricas degeneradas (SCD info embebida)
    salario_mes             DECIMAL(12,2)   NOT NULL,
    variacion_salarial_pct  DECIMAL(8,4),                 -- % cambio vs mes anterior
    dias_en_departamento    INT,
    es_nuevo_ingreso        TINYINT(1)      DEFAULT 0,
    es_cambio_dept          TINYINT(1)      DEFAULT 0,
    es_aumento_salarial     TINYINT(1)      DEFAULT 0,
    PRIMARY KEY (snapshot_sk),
    CONSTRAINT fk_snap_empleado    FOREIGN KEY (empleado_sk) REFERENCES dim_empleado(empleado_sk),
    CONSTRAINT fk_snap_dept        FOREIGN KEY (dept_sk)     REFERENCES dim_departamento(dept_sk),
    CONSTRAINT fk_snap_tiempo      FOREIGN KEY (tiempo_sk)   REFERENCES dim_tiempo(tiempo_sk),
    INDEX idx_snap_empleado (empleado_sk),
    INDEX idx_snap_dept     (dept_sk),
    INDEX idx_snap_tiempo   (tiempo_sk)
);

-- =============================================================================
-- 4. CARGA DE DATOS - Staging
-- =============================================================================

INSERT INTO stg_empleados VALUES
(1, 'Carlos',   'Mendoza',  'cmendoza@corp.com',  '2020-01-15', 'Tecnología',   'Dev Senior',       75000.00, 'Ciudad de México', 1),
(2, 'Ana',      'García',   'agarcia@corp.com',   '2019-03-10', 'Ventas',       'Ejecutiva Sr',     65000.00, 'Guadalajara',      1),
(3, 'Roberto',  'López',    'rlopez@corp.com',    '2021-06-01', 'Finanzas',     'Analista',         55000.00, 'Ciudad de México', 1),
(4, 'María',    'Sánchez',  'msanchez@corp.com',  '2018-09-20', 'RRHH',         'Coordinadora',     60000.00, 'Monterrey',        1),
(5, 'Javier',   'Torres',   'jtorres@corp.com',   '2022-02-14', 'Tecnología',   'Dev Junior',       45000.00, 'Guadalajara',      1);

INSERT INTO stg_cambios_departamento (empleado_id, dept_anterior, dept_nuevo, fecha_cambio, motivo) VALUES
(1, 'Tecnología',  'Arquitectura',  '2022-06-01', 'Promoción interna'),
(2, 'Ventas',      'Marketing',     '2023-01-15', 'Reestructuración'),
(1, 'Arquitectura','CTO Office',    '2023-09-01', 'Proyecto estratégico'),
(3, 'Finanzas',    'Contraloría',   '2023-04-01', 'Reestructuración');

INSERT INTO stg_historial_salario (empleado_id, salario_nuevo, fecha_cambio, tipo_ajuste) VALUES
(1, 82000.00, '2022-06-01', 'PROMOCION'),
(1, 90000.00, '2023-09-01', 'MERITO'),
(2, 70000.00, '2023-01-15', 'PROMOCION'),
(3, 60000.00, '2023-06-01', 'INFLACION'),
(4, 67000.00, '2022-12-01', 'MERITO'),
(5, 50000.00, '2023-03-01', 'MERITO');

-- =============================================================================
-- 5. CARGA dim_tiempo (rango 2018-2024)
-- =============================================================================

DROP PROCEDURE IF EXISTS sp_fill_dim_tiempo;
DELIMITER $$
CREATE PROCEDURE sp_fill_dim_tiempo(IN p_start DATE, IN p_end DATE)
BEGIN
    DECLARE v_date DATE DEFAULT p_start;
    WHILE v_date <= p_end DO
        INSERT IGNORE INTO dim_tiempo (
            fecha_full, anio, trimestre, mes, nombre_mes,
            semana_anio, dia_semana, nombre_dia, es_fin_semana
        ) VALUES (
            v_date,
            YEAR(v_date),
            QUARTER(v_date),
            MONTH(v_date),
            DATE_FORMAT(v_date,'%M'),
            WEEK(v_date, 3),
            DAYOFWEEK(v_date),
            DATE_FORMAT(v_date,'%W'),
            IF(DAYOFWEEK(v_date) IN (1,7), 1, 0)
        );
        SET v_date = DATE_ADD(v_date, INTERVAL 1 DAY);
    END WHILE;
END$$
DELIMITER ;

CALL sp_fill_dim_tiempo('2018-01-01', '2024-12-31');

-- =============================================================================
-- 6. ETL → dim_departamento con SCD TIPO 2
--    Proceso:
--      a) Cargar estado inicial de cada empleado desde stg_empleados
--      b) Para cada cambio en stg_cambios_departamento:
--         - Cerrar fila anterior (fecha_fin = fecha_cambio - 1, es_actual=0)
--         - Insertar nueva fila (es_actual=1, fecha_inicio=fecha_cambio)
-- =============================================================================

-- Carga inicial (estado base de stg_empleados)
INSERT INTO dim_departamento (dept_nk, nombre_dept, division, gerente, ubicacion, fecha_inicio, fecha_fin, es_actual)
SELECT
    e.empleado_id,
    e.departamento,
    CASE
        WHEN e.departamento IN ('Tecnología','Arquitectura','CTO Office') THEN 'Tecnología y Sistemas'
        WHEN e.departamento IN ('Ventas','Marketing')                     THEN 'Comercial'
        WHEN e.departamento IN ('Finanzas','Contraloría')                 THEN 'Administración'
        ELSE 'Corporativo'
    END AS division,
    NULL   AS gerente,
    e.sede AS ubicacion,
    e.fecha_ingreso AS fecha_inicio,
    NULL            AS fecha_fin,
    1               AS es_actual
FROM stg_empleados e;

-- SCD T2: Procesar cambios de departamento
-- Paso 1: Cerrar registros actuales que van a cambiar
UPDATE dim_departamento dd
JOIN stg_cambios_departamento sc ON sc.empleado_id = dd.dept_nk
    AND dd.es_actual = 1
    AND dd.nombre_dept = sc.dept_anterior
SET
    dd.fecha_fin  = DATE_SUB(sc.fecha_cambio, INTERVAL 1 DAY),
    dd.es_actual  = 0;

-- Paso 2: Insertar nuevas versiones (una por cambio)
INSERT INTO dim_departamento (dept_nk, nombre_dept, division, gerente, ubicacion, fecha_inicio, fecha_fin, es_actual)
SELECT
    sc.empleado_id,
    sc.dept_nuevo,
    CASE
        WHEN sc.dept_nuevo IN ('Tecnología','Arquitectura','CTO Office') THEN 'Tecnología y Sistemas'
        WHEN sc.dept_nuevo IN ('Ventas','Marketing')                     THEN 'Comercial'
        WHEN sc.dept_nuevo IN ('Finanzas','Contraloría')                 THEN 'Administración'
        ELSE 'Corporativo'
    END,
    NULL,
    e.sede,
    sc.fecha_cambio,
    NULL,
    1
FROM stg_cambios_departamento sc
JOIN stg_empleados e ON e.empleado_id = sc.empleado_id
ORDER BY sc.cambio_id;

-- =============================================================================
-- 7. ETL → dim_empleado con SCD TIPO 1 (sede) y SCD TIPO 3 (salario)
--    Limpieza de datos:
--      - TRIM() en texto
--      - COALESCE para nulos
--      - Email en minúsculas
-- =============================================================================

INSERT INTO dim_empleado (
    empleado_nk, nombre, apellido, email, fecha_ingreso, cargo,
    sede_actual,
    salario_actual, salario_anterior, fecha_ultimo_ajuste, tipo_ultimo_ajuste, activo
)
SELECT
    e.empleado_id,
    TRIM(e.nombre),
    TRIM(e.apellido),
    LOWER(TRIM(e.email)),
    e.fecha_ingreso,
    TRIM(e.cargo),
    -- SCD T1: sede actual (se sobreescribirá si cambia, sin historia)
    TRIM(e.sede),
    -- SCD T3: salario_actual = salario vigente, salario_anterior = NULL al inicio
    COALESCE(ultimo.salario_nuevo, e.salario),
    CASE WHEN ultimo.salario_nuevo IS NOT NULL THEN e.salario ELSE NULL END,
    ultimo.fecha_cambio,
    ultimo.tipo_ajuste,
    e.activo
FROM stg_empleados e
LEFT JOIN (
    -- Último ajuste salarial por empleado
    SELECT h1.*
    FROM stg_historial_salario h1
    WHERE h1.historial_id = (
        SELECT MAX(h2.historial_id)
        FROM stg_historial_salario h2
        WHERE h2.empleado_id = h1.empleado_id
    )
) ultimo ON ultimo.empleado_id = e.empleado_id;

-- =============================================================================
-- 8. SIMULACION SCD T1: Cambio de sede (sobreescribe, SIN historia)
--    Carlos Mendoza se traslada a Monterrey
-- =============================================================================

UPDATE dim_empleado
SET sede_actual = 'Monterrey'
WHERE empleado_nk = 1;

-- =============================================================================
-- 9. ETL → fact_rrhh_snapshot
--    Carga snapshot por empleado por mes en que ocurrieron eventos
-- =============================================================================

INSERT INTO fact_rrhh_snapshot (
    empleado_sk, dept_sk, tiempo_sk,
    salario_mes, variacion_salarial_pct,
    dias_en_departamento, es_nuevo_ingreso, es_cambio_dept, es_aumento_salarial
)
SELECT
    de.empleado_sk,
    dd.dept_sk,
    dt.tiempo_sk,
    de.salario_actual                                                    AS salario_mes,
    CASE
        WHEN de.salario_anterior IS NOT NULL AND de.salario_anterior > 0
        THEN ROUND(((de.salario_actual - de.salario_anterior) / de.salario_anterior) * 100, 4)
        ELSE NULL
    END                                                                  AS variacion_salarial_pct,
    DATEDIFF(COALESCE(dd.fecha_fin, CURDATE()), dd.fecha_inicio)        AS dias_en_departamento,
    IF(YEAR(se.fecha_ingreso) = YEAR(dd.fecha_inicio) AND
       MONTH(se.fecha_ingreso) = MONTH(dd.fecha_inicio), 1, 0)          AS es_nuevo_ingreso,
    IF(dd.fecha_inicio > se.fecha_ingreso, 1, 0)                        AS es_cambio_dept,
    IF(de.salario_anterior IS NOT NULL, 1, 0)                           AS es_aumento_salarial
FROM dim_empleado de
JOIN stg_empleados se       ON se.empleado_id = de.empleado_nk
JOIN dim_departamento dd    ON dd.dept_nk = de.empleado_nk AND dd.es_actual = 1
JOIN dim_tiempo dt          ON dt.fecha_full = LAST_DAY(CURDATE());

-- =============================================================================
-- 10. ANALISIS Y KPIs
-- =============================================================================

-- A) Comparación SCD: Historial completo de departamentos por empleado (SCD T2)
SELECT
    de.nombre_completo                              AS empleado,
    dd.nombre_dept                                  AS departamento,
    dd.division,
    dd.fecha_inicio,
    COALESCE(dd.fecha_fin, '9999-12-31')            AS fecha_fin,
    dd.es_actual,
    DATEDIFF(COALESCE(dd.fecha_fin, CURDATE()), dd.fecha_inicio) AS dias_en_dept
FROM dim_departamento dd
JOIN dim_empleado de ON de.empleado_nk = dd.dept_nk
ORDER BY de.empleado_nk, dd.fecha_inicio;

-- B) Evolución salarial (SCD T3: actual vs anterior)
SELECT
    nombre_completo,
    cargo,
    sede_actual                                     AS sede_actual_scd_t1,
    salario_anterior                                AS salario_previo_scd_t3,
    salario_actual                                  AS salario_vigente_scd_t3,
    CASE
        WHEN salario_anterior IS NOT NULL
        THEN CONCAT(ROUND(((salario_actual - salario_anterior) / salario_anterior)*100, 2), '%')
        ELSE 'Sin cambio registrado'
    END                                             AS variacion_pct,
    fecha_ultimo_ajuste,
    tipo_ultimo_ajuste
FROM dim_empleado
ORDER BY variacion_pct DESC;

-- C) Snapshot mensual con dimensiones (análisis Star Schema)
SELECT
    dt.anio,
    dt.nombre_mes,
    de.nombre_completo,
    de.cargo,
    de.sede_actual,
    dd.nombre_dept,
    dd.division,
    fs.salario_mes,
    fs.variacion_salarial_pct,
    fs.dias_en_departamento,
    IF(fs.es_nuevo_ingreso=1,'SÍ','NO')            AS nuevo_ingreso,
    IF(fs.es_cambio_dept=1,'SÍ','NO')              AS cambio_dept,
    IF(fs.es_aumento_salarial=1,'SÍ','NO')         AS aumento_salarial
FROM fact_rrhh_snapshot fs
JOIN dim_empleado    de ON de.empleado_sk = fs.empleado_sk
JOIN dim_departamento dd ON dd.dept_sk    = fs.dept_sk
JOIN dim_tiempo      dt ON dt.tiempo_sk   = fs.tiempo_sk
ORDER BY dt.fecha_full, de.nombre_completo;

-- D) Cambios organizacionales - cuántos movimientos por división
SELECT
    dd.division,
    COUNT(*) AS total_versiones_scd_t2,
    SUM(dd.es_actual) AS registros_vigentes,
    COUNT(*) - SUM(dd.es_actual) AS registros_historicos
FROM dim_departamento dd
GROUP BY dd.division
ORDER BY total_versiones_scd_t2 DESC;

-- E) Promedio salarial por departamento actual
SELECT
    dd.nombre_dept,
    dd.division,
    COUNT(de.empleado_sk)               AS empleados,
    ROUND(AVG(de.salario_actual), 2)    AS salario_promedio,
    MIN(de.salario_actual)              AS salario_minimo,
    MAX(de.salario_actual)              AS salario_maximo
FROM dim_empleado de
JOIN dim_departamento dd ON dd.dept_nk = de.empleado_nk AND dd.es_actual = 1
GROUP BY dd.nombre_dept, dd.division
ORDER BY salario_promedio DESC;

-- F) Comparación entre tipos SCD
SELECT 'SCD Tipo 1' AS tipo_scd,
       'sede_actual en dim_empleado' AS ubicacion,
       'Sobreescribe sin historia. Solo valor actual visible.' AS descripcion,
       COUNT(*) AS registros_afectados
FROM dim_empleado WHERE sede_actual IS NOT NULL

UNION ALL

SELECT 'SCD Tipo 2',
       'dim_departamento (múltiples filas por empleado)',
       'Nueva fila por cada cambio. Historia completa con fecha_inicio/fin.',
       COUNT(*)
FROM dim_departamento WHERE es_actual = 0

UNION ALL

SELECT 'SCD Tipo 3',
       'salario_actual + salario_anterior en dim_empleado',
       'Dos columnas: valor actual y valor inmediato anterior.',
       COUNT(*)
FROM dim_empleado WHERE salario_anterior IS NOT NULL;
