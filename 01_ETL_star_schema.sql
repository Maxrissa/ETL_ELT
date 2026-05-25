-- ETL 

DROP DATABASE IF EXISTS empresa_etl;

CREATE DATABASE empresa_etl
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE empresa_etl;

-- ============================================================
-- EXTRACT
-- Tablas staging
-- ============================================================

DROP TABLE IF EXISTS stg_clientes;
CREATE TABLE stg_clientes (
    cliente_id INT,
    nombre     VARCHAR(100),
    ciudad     VARCHAR(100),
    edad       INT
);

DROP TABLE IF EXISTS stg_productos;
CREATE TABLE stg_productos (
    producto_id INT,
    producto    VARCHAR(100),
    categoria   VARCHAR(100),
    precio      DECIMAL(10,2)
);

DROP TABLE IF EXISTS stg_empleados;
CREATE TABLE stg_empleados (
    empleado_id  INT,
    nombre       VARCHAR(100),
    departamento VARCHAR(100)
);

DROP TABLE IF EXISTS stg_ventas;
CREATE TABLE stg_ventas (
    venta_id    INT,
    cliente_id  INT,
    producto_id INT,
    empleado_id INT,
    cantidad    INT
);

-- ============================================================
-- INSERTAR DATOS CRUDOS
-- ============================================================

INSERT INTO stg_clientes VALUES
(1, 'Carlos', 'San Salvador', 25),
(2, 'Ana',    'Santa Ana',    30),
(3, NULL,     'San Miguel',   22),
(4, 'Pedro',  'La Libertad',  40),
(4, 'Pedro',  'La Libertad',  40);

INSERT INTO stg_productos VALUES
(1, 'Laptop', 'Tecnologia', 1200),
(2, 'Mouse',  'Tecnologia',   25),
(3, 'Silla',  'Muebles',     150),
(4, NULL,     'Tecnologia',   75);

INSERT INTO stg_empleados VALUES
(1, 'Maria', 'Ventas'),
(2, 'Jose',  'Ventas'),
(3, NULL,    'Marketing');

INSERT INTO stg_ventas VALUES
(1, 1, 1, 1, 2),
(2, 2, 2, 1, 5),
(3, 3, 3, 2, 1),
(4, 4, 1, 2, 1),
(5, 1, 2, 1, 3);

-- ============================================================
-- TRANSFORM
-- Limpieza de datos
-- ============================================================

DROP TABLE IF EXISTS clientes_clean;
CREATE TABLE clientes_clean AS
SELECT DISTINCT
    cliente_id,
    COALESCE(nombre, 'Sin Nombre') AS nombre,
    ciudad,
    edad
FROM stg_clientes;

DROP TABLE IF EXISTS productos_clean;
CREATE TABLE productos_clean AS
SELECT DISTINCT
    producto_id,
    COALESCE(producto, 'Producto Desconocido') AS producto,
    categoria,
    precio
FROM stg_productos;

DROP TABLE IF EXISTS empleados_clean;
CREATE TABLE empleados_clean AS
SELECT DISTINCT
    empleado_id,
    COALESCE(nombre, 'Sin Nombre') AS nombre,
    departamento
FROM stg_empleados;

DROP TABLE IF EXISTS ventas_transformadas;
CREATE TABLE ventas_transformadas AS
SELECT
    v.venta_id,
    v.cliente_id,
    v.producto_id,
    v.empleado_id,
    v.cantidad,
    p.precio,
    (v.cantidad * p.precio) AS total
FROM stg_ventas v
JOIN productos_clean p
    ON v.producto_id = p.producto_id;

-- ============================================================
-- LOAD
-- STAR SCHEMA
-- ============================================================

-- =========================
-- DIM CLIENTE
-- =========================

DROP TABLE IF EXISTS dim_cliente;

CREATE TABLE dim_cliente (
    cliente_id INT PRIMARY KEY,
    nombre     VARCHAR(100),
    ciudad     VARCHAR(100),
    edad       INT
);

INSERT INTO dim_cliente
SELECT *
FROM clientes_clean;

-- =========================
-- DIM PRODUCTO
-- =========================

DROP TABLE IF EXISTS dim_producto;

CREATE TABLE dim_producto (
    producto_id INT PRIMARY KEY,
    producto    VARCHAR(100),
    categoria   VARCHAR(100),
    precio      DECIMAL(10,2)
);

INSERT INTO dim_producto
SELECT *
FROM productos_clean;

-- =========================
-- DIM EMPLEADO
-- =========================

DROP TABLE IF EXISTS dim_empleado;

CREATE TABLE dim_empleado (
    empleado_id  INT PRIMARY KEY,
    nombre       VARCHAR(100),
    departamento VARCHAR(100)
);

INSERT INTO dim_empleado
SELECT *
FROM empleados_clean;

-- =========================
-- FACT VENTAS
-- =========================

DROP TABLE IF EXISTS fact_ventas;

CREATE TABLE fact_ventas (
    venta_id    INT PRIMARY KEY,
    cliente_id  INT,
    producto_id INT,
    empleado_id INT,
    cantidad    INT,
    precio      DECIMAL(10,2),
    total       DECIMAL(10,2),

    FOREIGN KEY (cliente_id)
        REFERENCES dim_cliente(cliente_id),

    FOREIGN KEY (producto_id)
        REFERENCES dim_producto(producto_id),

    FOREIGN KEY (empleado_id)
        REFERENCES dim_empleado(empleado_id)
);

INSERT INTO fact_ventas
SELECT
    venta_id,
    cliente_id,
    producto_id,
    empleado_id,
    cantidad,
    precio,
    total
FROM ventas_transformadas;

-- ============================================================
-- KPIs
-- ============================================================

-- Total ingresos
SELECT
    SUM(total) AS ingreso_total
FROM fact_ventas;

-- Promedio ventas
SELECT
    AVG(total) AS promedio_venta
FROM fact_ventas;

-- Ventas por ciudad
SELECT
    c.ciudad,
    SUM(f.total) AS ventas
FROM fact_ventas f
JOIN dim_cliente c
    ON f.cliente_id = c.cliente_id
GROUP BY c.ciudad;

-- Top clientes
SELECT
    c.nombre AS cliente,
    SUM(f.total) AS total_comprado
FROM fact_ventas f
JOIN dim_cliente c
    ON f.cliente_id = c.cliente_id
GROUP BY c.nombre
ORDER BY total_comprado DESC;

-- Ventas por categoría
SELECT
    p.categoria,
    SUM(f.total) AS ingresos
FROM fact_ventas f
JOIN dim_producto p
    ON f.producto_id = p.producto_id
GROUP BY p.categoria;

-- Rendimiento empleados
SELECT
    e.nombre AS empleado,
    SUM(f.total) AS ventas_generadas
FROM fact_ventas f
JOIN dim_empleado e
    ON f.empleado_id = e.empleado_id
GROUP BY e.nombre
ORDER BY ventas_generadas DESC;