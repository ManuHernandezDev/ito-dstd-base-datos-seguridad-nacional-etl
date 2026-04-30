-- ============================================================
-- CONSULTAS SQL - PUNTO 2: ANÁLISIS DE EMERGENCIAS NACIONALES
-- Autor: Rodrigo Candelaria Velazquez
-- Tabla fuente: emergencias_nacionales_consolidado
-- Base de datos: bd_emergencias_nacional (PostgreSQL)
-- ============================================================


-- CONSULTA 1: TOP 10 estados con más emergencias totales
-- Agrupa todos los registros por estado y suma sus emergencias
SELECT
    estado,
    SUM(total_emergencias)  AS emergencias_totales,
    SUM(total_delitos)      AS total_delitos,
    SUM(total_accidentes)   AS total_accidentes
FROM
    emergencias_nacionales_consolidado
GROUP BY
    estado
ORDER BY
    emergencias_totales DESC
LIMIT 10;


-- CONSULTA 2: Emergencias por estado y mes (tendencia temporal)
SELECT
    estado,
    EXTRACT(YEAR  FROM fecha::DATE) AS anio,
    EXTRACT(MONTH FROM fecha::DATE) AS mes,
    SUM(total_emergencias) AS emergencias_mes
FROM
    emergencias_nacionales_consolidado
GROUP BY
    estado, anio, mes
ORDER BY
    anio, mes, emergencias_mes DESC;


-- CONSULTA 3: JOIN entre delitos y accidentes por estado
-- Demuestra la unión de ambas métricas para identificar zonas críticas
SELECT
    a.estado,
    SUM(a.total_delitos)     AS total_delitos_estado,
    SUM(b.total_accidentes)  AS total_accidentes_estado,
    SUM(a.total_delitos) + SUM(b.total_accidentes) AS gran_total_emergencias
FROM
    emergencias_nacionales_consolidado AS a
    INNER JOIN emergencias_nacionales_consolidado AS b
        ON a.estado = b.estado AND a.fecha = b.fecha
GROUP BY
    a.estado
ORDER BY
    gran_total_emergencias DESC;
