-- ELT 
-- Base de datos

DROP DATABASE IF EXISTS empresa_elt;

CREATE DATABASE empresa_elt
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE empresa_elt;

SET SQL_SAFE_UPDATES = 0;

-- Extract

CREATE TABLE stg_clientes (
    cliente_id INT,
    nombre     VARCHAR(100),
    ciudad     VARCHAR(100),
    edad       INT
);

CREATE TABLE stg_productos (
    producto_id INT,
    producto    VARCHAR(100),
    categoria   VARCHAR(100),
    precio      DECIMAL(10,2)
);

CREATE TABLE stg_empleados (
    empleado_id  INT,
    nombre       VARCHAR(100),
    departamento VARCHAR(100)
);

CREATE TABLE stg_ventas (
    venta_id    INT,
    cliente_id  INT,
    producto_id INT,
    empleado_id INT,
    cantidad    INT
);

-- Datos clientes

INSERT INTO stg_clientes VALUES
(1, 'Carlos', 'San Salvador', 25),
(2, 'Ana',    'Santa Ana',    30),
(3, NULL,     'San Miguel',   22),
(4, 'Pedro',  'La Libertad',  40),
(4, 'Pedro',  'La Libertad',  40);

-- Datos productos

INSERT INTO stg_productos VALUES
(1, 'Laptop', 'Tecnologia', 1200),
(2, 'Mouse',  'Tecnologia', 25),
(3, 'Silla',  'Muebles', 150),
(4, NULL,     'Tecnologia', 75);

-- Datos empleados

INSERT INTO stg_empleados VALUES
(1, 'Maria', 'Ventas'),
(2, 'Jose',  'Ventas'),
(3, NULL,    'Marketing');

-- Datos ventas

INSERT INTO stg_ventas VALUES
(1, 1, 1, 1, 2),
(2, 2, 2, 1, 5),
(3, 3, 3, 2, 1),
(4, 4, 1, 2, 1),
(5, 1, 2, 1, 3);

-- Load

CREATE TABLE elt_clientes AS
SELECT *
FROM stg_clientes;

CREATE TABLE elt_productos AS
SELECT *
FROM stg_productos;

CREATE TABLE elt_empleados AS
SELECT *
FROM stg_empleados;

CREATE TABLE elt_ventas (
    venta_id    INT,
    cliente_id  INT,
    producto_id INT,
    empleado_id INT,
    cantidad    INT,
    precio      DECIMAL(10,2),
    total       DECIMAL(10,2)
);

INSERT INTO elt_ventas (
    venta_id,
    cliente_id,
    producto_id,
    empleado_id,
    cantidad
)
SELECT
    venta_id,
    cliente_id,
    producto_id,
    empleado_id,
    cantidad
FROM stg_ventas;

-- Transform

-- Limpiar nombres null clientes

UPDATE elt_clientes
SET nombre = 'Sin Nombre'
WHERE nombre IS NULL;

-- Eliminar duplicados clientes

CREATE TABLE clientes_temp AS
SELECT DISTINCT *
FROM elt_clientes;

DROP TABLE elt_clientes;

RENAME TABLE clientes_temp TO elt_clientes;

-- Limpiar nombres null productos

UPDATE elt_productos
SET producto = 'Producto Desconocido'
WHERE producto IS NULL;

-- Limpiar nombres null empleados

UPDATE elt_empleados
SET nombre = 'Sin Nombre'
WHERE nombre IS NULL;

-- Calcular metricas ventas

UPDATE elt_ventas v
JOIN elt_productos p
    ON v.producto_id = p.producto_id
SET
    v.precio = p.precio,
    v.total  = v.cantidad * p.precio;

-- Snowflake schema

-- Dimension ciudad

CREATE TABLE dim_ciudad (
    ciudad_id INT AUTO_INCREMENT PRIMARY KEY,
    ciudad    VARCHAR(100) UNIQUE
);

INSERT INTO dim_ciudad (ciudad)
SELECT DISTINCT ciudad
FROM elt_clientes;

-- Dimension cliente

CREATE TABLE dim_cliente (
    cliente_id INT PRIMARY KEY,
    nombre     VARCHAR(100),
    edad       INT,
    ciudad_id  INT,

    FOREIGN KEY (ciudad_id)
        REFERENCES dim_ciudad(ciudad_id)
);

INSERT INTO dim_cliente (
    cliente_id,
    nombre,
    edad,
    ciudad_id
)
SELECT
    c.cliente_id,
    c.nombre,
    c.edad,
    ci.ciudad_id
FROM elt_clientes c
JOIN dim_ciudad ci
    ON c.ciudad = ci.ciudad;

-- Dimension categoria

CREATE TABLE dim_categoria (
    categoria_id INT AUTO_INCREMENT PRIMARY KEY,
    categoria    VARCHAR(100) UNIQUE
);

INSERT INTO dim_categoria (categoria)
SELECT DISTINCT categoria
FROM elt_productos;

-- Dimension producto

CREATE TABLE dim_producto (
    producto_id  INT PRIMARY KEY,
    producto     VARCHAR(100),
    precio       DECIMAL(10,2),
    categoria_id INT,

    FOREIGN KEY (categoria_id)
        REFERENCES dim_categoria(categoria_id)
);

INSERT INTO dim_producto (
    producto_id,
    producto,
    precio,
    categoria_id
)
SELECT
    p.producto_id,
    p.producto,
    p.precio,
    c.categoria_id
FROM elt_productos p
JOIN dim_categoria c
    ON p.categoria = c.categoria;

-- Dimension departamento

CREATE TABLE dim_departamento (
    departamento_id INT AUTO_INCREMENT PRIMARY KEY,
    departamento    VARCHAR(100) UNIQUE
);

INSERT INTO dim_departamento (departamento)
SELECT DISTINCT departamento
FROM elt_empleados;

-- Dimension empleado

CREATE TABLE dim_empleado (
    empleado_id     INT PRIMARY KEY,
    nombre          VARCHAR(100),
    departamento_id INT,

    FOREIGN KEY (departamento_id)
        REFERENCES dim_departamento(departamento_id)
);

INSERT INTO dim_empleado (
    empleado_id,
    nombre,
    departamento_id
)
SELECT
    e.empleado_id,
    e.nombre,
    d.departamento_id
FROM elt_empleados e
JOIN dim_departamento d
    ON e.departamento = d.departamento;

-- Tabla fact

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
SELECT *
FROM elt_ventas;

-- Kpi ingreso total

SELECT
    SUM(total) AS ingreso_total
FROM fact_ventas;

-- Kpi promedio ventas

SELECT
    AVG(total) AS promedio_venta
FROM fact_ventas;

-- Kpi ventas por ciudad

SELECT
    ci.ciudad,
    SUM(f.total) AS ventas
FROM fact_ventas f
JOIN dim_cliente c
    ON f.cliente_id = c.cliente_id
JOIN dim_ciudad ci
    ON c.ciudad_id = ci.ciudad_id
GROUP BY ci.ciudad;

-- Kpi ventas por categoria

SELECT
    cat.categoria,
    SUM(f.total) AS ingresos
FROM fact_ventas f
JOIN dim_producto p
    ON f.producto_id = p.producto_id
JOIN dim_categoria cat
    ON p.categoria_id = cat.categoria_id
GROUP BY cat.categoria;

-- Kpi rendimiento empleados

SELECT
    e.nombre,
    d.departamento,
    SUM(f.total) AS ventas_generadas
FROM fact_ventas f
JOIN dim_empleado e
    ON f.empleado_id = e.empleado_id
JOIN dim_departamento d
    ON e.departamento_id = d.departamento_id
GROUP BY e.nombre, d.departamento
ORDER BY ventas_generadas DESC;