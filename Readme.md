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

### 1. (E) - Extracción (Extract)

La extracción es el proceso de tomar los datos crudos desde su origen (los archivos planos) y subirlos a la memoria de la computadora para poder manipularlos.

**Cómo se aplicó en el proyecto:**

- **Herramienta:** Utilizamos el lenguaje **Python** junto con la librería **Pandas**, que está optimizada para manejar grandes volúmenes de datos.
- **La acción técnica:** Mediante la función `pd.read_csv()`, el script "leyó" dos archivos masivos directamente hacia estructuras de datos llamadas _DataFrames_:
  1.  La **base propia** (`datos_delictivos_no_normalizados.csv`) con **100,000 registros**.
  2.  La **base externa** (`carpetasFGJ_2024.csv`) con **138,630 registros**.
- **El logro:** Con este solo paso, demostraron la capacidad de ingestar más de 238,000 filas de datos de golpe, cumpliendo y superando el requisito de "al menos 20 mil datos" de la docente.

### 2. (T) - Transformación (Transform)

Aquí es donde ocurre la verdadera "magia" de la ingeniería de datos. La transformación consiste en limpiar, homologar y, lo más importante, cruzar la información para que tenga sentido.

**Cómo se aplicó en el proyecto:**
Se realizaron tres transformaciones clave en el código:

- **Normalización de metadatos:** Los nombres de las columnas en los archivos originales venían con formatos distintos. El script aplicó una comprensión de listas en Python (`[str(c).strip().lower() for c in df.columns]`) para quitar espacios y pasar todo a minúsculas, evitando errores de sintaxis en la base de datos.
- **Agrupación (Agregación):** Dado que cruzar 238,000 filas directamente puede ser pesado, el script utilizó la función `.groupby()` para contar cuántos delitos ocurrieron cada día en ambas bases.
- **El Cruce (Merge/Join):** Para cumplir la instrucción de _"Referenciar unir la base externa y la que nosotros creamos"_, el script ejecutó un **Inner Join** utilizando la función `pd.merge()`. Tomó la columna `fecha` de tu base propia y la comparó con la columna `fecha_hecho` de la Fiscalía. El resultado fue una nueva tabla consolidada que muestra únicamente los días donde hubo actividad en ambos registros.

### 3. (L) - Carga (Load)

La carga es el destino final. Es tomar esos datos limpios y transformados, y depositarlos en un sistema de almacenamiento robusto para que las herramientas de visualización (como Power BI o Looker Studio) puedan consumirlos.

**Cómo se aplicó en el proyecto:**

- **Herramienta:** Se utilizó **SQLAlchemy** (un ORM de Python) para crear un puente de conexión (`create_engine`) hacia el servidor local de **PostgreSQL**.
- **La acción técnica:** A través del comando `.to_sql()`, Python automatizó la creación de tres tablas directamente en el motor de base de datos, sin tener que escribir sentencias `CREATE TABLE` a mano:
  1.  `tabla_delitos_propia` (Los datos crudos del equipo).
  2.  `tabla_delitos_externa` (Los datos crudos de la FGJ).
  3.  `vista_delitos_combinada` (El resultado de la transformación matemática).
- **Exportación de respaldo:** Como paso adicional de seguridad en la arquitectura, el sistema también exportó un archivo físico (`base_final_para_looker.csv`) para permitir la integración en la nube con Google Looker Studio, saltando las restricciones de firewall del servidor local.

### Resumen:

_"Nuestro proceso ETL automatizó la lectura de más de 230,000 registros mediante Pandas. Transformamos la data normalizando encabezados y ejecutando un Inner Join algorítmico por fecha, para finalmente cargar el resultado en un servidor relacional PostgreSQL usando SQLAlchemy, dejando la data lista para su consumo en software de Business Intelligence."_

---

**Fecha de Entrega:** Lunes, 27 de Abril de 2026.
**Institución:** Instituto Tecnológico de Oaxaca (ITO).
