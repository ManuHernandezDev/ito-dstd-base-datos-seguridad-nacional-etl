# Guía de Ejecución: Sistema ETL y Visualización de Seguridad Nacional

Este documento detalla el proceso técnico para la implementación del flujo **ETL (Extract, Transform, Load)** y la posterior analítica de datos mediante **Business Intelligence**. El proyecto integra bases de datos masivas del sector público con registros de autoría propia para simular un entorno de inteligencia de seguridad.

## 1. Equipo 4

```
   Integrantes:
- Candelaria Velazquez Rodriguez.
- Diego García Jennifer.
- García Gallegos Eric
- Elorza Perez Joaquín Baruc
- Martínez Mendoza Jesús Angel
- Hernández Soriano Manuel
```

---

## 2. Descripción de las Fuentes de Datos

Para cumplir con el requisito de volumen, se procesaron un total de **238,630 registros**:

1.  **Base Externa (`carpetasFGJ_2024.csv`)**: 138,630 registros de la Fiscalía General de Justicia de la CDMX.
2.  **Base Propia (`datos_delictivos_no_normalizados.csv`)**: 100,000 registros estructurados por el equipo para el análisis de perfiles delictivos.

---

## 3. Arquitectura del Proceso ETL

### Fase 1: Extracción (Extract)

Se utilizó la librería **Pandas** de Python para la lectura de archivos planos (CSV). Esta fase garantiza la ingesta masiva de datos que superan los 20,000 registros solicitados.

### Fase 2: Transformación (Transform)

Se realizaron las siguientes operaciones mediante programación:

- **Normalización**: Conversión de encabezados a minúsculas y eliminación de espacios en blanco.
- **Limpieza**: Formateo de columnas temporales (`datetime`).
- **Unión (Merge)**: Se ejecutó un **Inner Join** entre ambas bases de datos utilizando la columna `fecha` como llave primaria de cruce. Esto permite correlacionar la incidencia delictiva externa con los registros operativos del equipo.

### Fase 3: Carga (Load)

Los datos transformados se inyectaron en un servidor local de **PostgreSQL** mediante el motor `SQLAlchemy`. Se generaron tres tablas principales:

- `tabla_delitos_propia`
- `tabla_delitos_externa`
- `vista_delitos_combinada` (Resultado de la unión técnica).
- 
---

## 4. Instrucciones de Ejecución

### Requisitos Previos

- **PostgreSQL**: Contar con un servidor activo y la base de datos `bd_plataforma_mexico` creada.
- **Python 3.x**: Librerías necesarias instaladas:
  ```bash
  pip install pandas sqlalchemy psycopg2-binary
  ```

### Pasos para Reproducir

1.  **Clonar el repositorio** y asegurarse de que los archivos CSV estén en la raíz.
2.  **Ejecutar el script principal**:
    ```bash
    python etl_maestro.py
    ```
3.  **Verificación**: Abrir pgAdmin y confirmar que las tablas se encuentran pobladas con los miles de registros.
4.  **Conexión a Power BI**:
    - Abrir el archivo de Power BI incluido.
    - Configurar el origen de datos hacia la base de datos local de PostgreSQL.

---

## 5. Visualización y KPIs (Power BI)

El dashboard final presenta cuatro formatos de gráficas esenciales para la toma de decisiones:

1.  **Tendencia Temporal (Gráfico de Líneas)**: Comparativa de delitos diarios entre ambas bases de datos unidas.
2.  **Distribución Geográfica (Mapa)**: Localización de delitos por Entidad Federativa.
3.  **Categorización de Delitos (Gráfico de Anillos)**: Desglose porcentual de la incidencia según la Fiscalía.
4.  **Indicadores de Volumen (Tarjetas)**: Conteo total de registros para validar la escala masiva del proyecto (>200k datos).

---

**Fecha de Entrega:** Lunes, 27 de Abril de 2026.
**Institución:** Instituto Tecnológico de Oaxaca (ITO).
