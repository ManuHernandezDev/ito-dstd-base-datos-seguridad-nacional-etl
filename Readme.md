# Sistema de Inteligencia y Soporte a Decisiones para Emergencias Nacionales
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Compatible-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MySQL](https://img.shields.io/badge/MySQL-Compatible-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Visualización-F2C811?logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![INEGI](https://img.shields.io/badge/Fuente-INEGI%20ATUS-green)](https://www.inegi.org.mx/)
[![Licencia](https://img.shields.io/badge/Licencia-Académica-orange)](./Readme.md)

---

## Equipo de Desarrollo:

Este proyecto es el resultado del trabajo conjunto del equipo de desarrollo, compuesto por especialistas en frontend y backend.

| Integrante | Matrícula | Rol Principal |
| :--- | :--- | :--- |
| **MARTÍNEZ MENDOZA JESÚS ÁNGEL** | 22161152 | Frontend Lead / Arquitectura |
| **DIEGO GARCIA JENNIFER** | 22161050 | Frontend Developer / UI-UX |
| **ELORZA PÉREZ JOAQUÍN BARUC** | 22161052 | Frontend Developer / Integración |
| **CANDELARIA VELAZQUEZ RODRIGO** | 22161014 | Backend Developer / Base de Datos |
| **GARCÍA GALLEGOS ERIC** | 22161068 | Backend Developer / API REST |
| **HERNANDEZ SORIANO MANUEL** | 22161097 | Backend Lead / Arquitectura |

---

## Definición del Sistema
El Sistema de Soporte a Decisiones (DSS) es una plataforma de Inteligencia de Negocios diseñada para procesar, consolidar y visualizar datos masivos de incidencias delictivas y emergencias viales a nivel nacional. Su objetivo principal es transformar información cruda en inteligencia operativa accionable mediante procesos ETL y el análisis de Indicadores Clave de Rendimiento (KPIs). Esta herramienta proporciona a los altos mandos y centros de monitoreo una interfaz gerencial para identificar patrones geoespaciales y temporales, permitiendo optimizar la asignación de recursos, reducir tiempos de respuesta y formular estrategias tácticas basadas en evidencia algorítmica y matemática.



---


## Tabla de Contenidos

1. [Descripción del Proyecto](#-descripción-del-proyecto)
2. [Equipo de Desarrollo](#-equipo-de-desarrollo)
3. [Arquitectura del Pipeline ETL](#-arquitectura-del-pipeline-etl)
4. [Fuentes de Datos](#-fuentes-de-datos)
5. [Estructura del Repositorio](#-estructura-del-repositorio)
6. [Requisitos de Entorno](#-requisitos-de-entorno)
7. [Instrucciones de Ejecución](#-instrucciones-de-ejecución)
   - [PostgreSQL (Versión Principal)](#-opción-a--postgresql-versión-principal)
   - [MySQL (Versión Alternativa)](#-opción-b--mysql-versión-alternativa)
8. [Reglas de Negocio y Transformaciones](#-reglas-de-negocio-y-transformaciones)
9. [Esquema de la Base de Datos](#-esquema-de-la-base-de-datos)
10. [Análisis SQL y Resultados](#-análisis-sql-y-resultados)
11. [Visualización en Power BI](#-visualización-en-power-bi)
12. [Resultados Ejecutivos](#-resultados-ejecutivos)

---

## Descripción del Proyecto

Este repositorio contiene el pipeline **ETL (Extract, Transform, Load)** desarrollado en Python para la asignatura de **Bases de Datos** del Instituto Tecnológico de Oaxaca (ITO).

El sistema cruza dos grandes fuentes de datos públicas de México:

| Fuente | Descripción |
|--------|-------------|
| **Registro de Delitos** | Base operativa de incidencia delictiva a nivel nacional (2020–2025) |
| **ATUS — INEGI** | Accidentes de Tránsito en Zonas Urbanas y Suburbanas (2020–2023) |

**Objetivo:** Construir un *datamart* consolidado que permita a herramientas de Business Intelligence (Power BI / Looker) identificar los **estados y fechas con mayores colapsos en la atención de emergencias del 911**, cruzando simultáneamente la carga de accidentes viales y actos delictivos.

> [!NOTE]
> Este proyecto simula un entorno de inteligencia de seguridad pública mediante datos del sector público mexicano para fines académicos.

---

## Equipo de Desarrollo

**Equipo 4 — Ingeniería en Sistemas Computacionales**
Instituto Tecnológico de Oaxaca · Materia: Base de Datos

| # | Nombre |
|---|--------|
| 1 | Candelaria Velázquez Rodríguez |
| 2 | Diego García Jennifer |
| 3 | Elorza Pérez Joaquín Baruc |
| 4 | García Gallegos Eric |
| 5 | Martínez Mendoza Jesús Ángel |
| 6 | Hernández Soriano Manuel |

---

## Arquitectura del Pipeline ETL

El flujo de datos sigue las tres fases clásicas de un pipeline ETL:

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FASE 1 — EXTRACCIÓN                        │
│                                                                     │
│   datos_delictivos_no_normalizados.csv  ─┐                          │
│   atus_anual_2020.csv                   ─┤                          │
│   atus_anual_2021.csv                   ─┼──► etl_maestro.py        │
│   atus_anual_2022.csv                   ─┤                          │
│   atus_anual_2023.csv                   ─┘                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FASE 2 — TRANSFORMACIÓN                      │
│                                                                     │
│  • Normalización de columnas (strip, lowercase)                     │
│  • Mapeo ID_ENTIDAD → nombre oficial del estado (INEGI)             │
│  • Construcción de fecha ISO 8601 (ANIO + MES + ID_DIA)             │
│  • Filtrado de registros inválidos (NaN, días > 31, meses > 12)     │
│  • Agrupación por [fecha, estado] → conteo de eventos               │
│  • INNER JOIN entre delitos y accidentes                            │
│  • Cálculo de total_emergencias = total_delitos + total_accidentes  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           FASE 3 — CARGA                            │
│                                                                     │
│   PostgreSQL ──► tabla: emergencias_nacionales_consolidado          │
│   CSV         ──► base_emergencias_limpia.csv (para Power BI)       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Fuentes de Datos

### Base Interna — Delitos

Archivo propio de incidencia delictiva generado para el proyecto. Contiene eventos delictivos históricos clasificados por **fecha** y **estado** (2020–2025).

```
datos_delictivos_no_normalizados.csv
  └── columnas clave: fecha, estado
```

### Base Externa — ATUS (INEGI)

Registros oficiales de accidentes de tránsito en zonas urbanas y suburbanas, publicados por el **Instituto Nacional de Estadística y Geografía (INEGI)**.

| Archivo | Año | Tamaño aprox. |
|---------|-----|---------------|
| `atus_anual_2020.csv` | 2020 | ~81 MB / 318,000 registros |
| `atus_anual_2021.csv` | 2021 | ~93 MB / 356,000 registros |
| `atus_anual_2022.csv` | 2022 | ~102 MB / 392,000 registros |
| `atus_anual_2023.csv` | 2023 | ~103 MB / 396,000 registros |

> [!IMPORTANT]
> Los archivos CSV del ATUS son masivos (> 80 MB cada uno). El script los carga y consolida dinámicamente mediante `pandas.concat()`. Asegúrate de tener al menos **2 GB de RAM disponible** antes de ejecutar el ETL.

---

## Estructura del Repositorio

```
ito-dstd-base-datos-seguridad-nacional-etl/
│
├── Readme.md                          ← Este archivo
│
├── etl_maestro.py                     ← Pipeline ETL principal (PostgreSQL)
├── etl_maestro_mysql.py               ← Pipeline ETL alternativo (MySQL)
│
├── graficas_1.pbix                    ← Dashboard Power BI
├── graficas_1.pdf                     ← Exportación PDF del reporte BI
│
├── crear_tabla_datos.sql              ← Script DDL: crea e inserta datos de prueba
├── consultas_rodrigo.sql             ← Consultas SQL de análisis
├── Reporte de Consulta                ← Resultados documentados de las consultas
│
├── datos_delictivos_no_normalizados.csv  ← Fuente interna de delitos
├── base_emergencias_limpia.csv           ← OUTPUT: datamart consolidado
│
├── atus_anual_2020.csv               ─┐
├── atus_anual_2021.csv               ─┤ Fuentes externas INEGI (ATUS)
├── atus_anual_2022.csv               ─┤
├── atus_anual_2023.csv               ─┘
│
└── .gitattributes                     ← Configuración Git LFS (archivos grandes)
```

---

## Requisitos de Entorno

### Versión de Python

```
Python 3.8 o superior
```

### Dependencias — Versión PostgreSQL

```bash
pip install pandas sqlalchemy psycopg2-binary
```

### Dependencias — Versión MySQL

```bash
pip install pandas sqlalchemy pymysql
```

### Motor de Base de Datos

| Motor | Versión recomendada | Puerto por defecto |
|-------|--------------------|--------------------|
| **PostgreSQL** | 13 o superior | `5432` |
| **MySQL** | 8.0 o superior | `3306` |

---

## Instrucciones de Ejecución

### Opción A — PostgreSQL (Versión Principal)

Ejecuta el pipeline completo que procesa todos los años del ATUS y los cruza con los registros de delitos.

**Paso 1 — Clonar el repositorio**

```bash
git clone https://github.com/ManuHernandezDev/ito-dstd-base-datos-seguridad-nacional-etl.git
cd ito-dstd-base-datos-seguridad-nacional-etl
```

**Paso 2 — Instalar dependencias**

```bash
pip install pandas sqlalchemy psycopg2-binary
```

**Paso 3 — Crear la base de datos en pgAdmin**

Abre pgAdmin o psql y ejecuta:

```sql
CREATE DATABASE bd_emergencias_nacional;
```

**Paso 4 — Configurar credenciales en `etl_maestro.py`**

Abre el archivo y modifica las variables al inicio del script:

```python
USUARIO   = "tu_usuario"      # ← Tu usuario de PostgreSQL
CONTRASENA = "tu_contraseña"  # ← Tu contraseña real
HOST      = "127.0.0.1"
PUERTO    = "5432"
BASE_DATOS = "bd_emergencias_nacional"
```

**Paso 5 — Ejecutar el ETL**

```bash
python etl_maestro.py
```

**Salida esperada en consola:**

```
Iniciando Extracción de Datos...
Cargando base masiva de delitos...
Encontrado y cargando: atus_anual_2020.csv...
Encontrado y cargando: atus_anual_2021.csv...
Encontrado y cargando: atus_anual_2022.csv...
Encontrado y cargando: atus_anual_2023.csv...
Consolidación ATUS terminada. Total de registros viales: X,XXX,XXX
Iniciando Transformación y Limpieza...
Agrupando y cruzando bases de datos por Estado y Fecha...
Cargando X registros históricos a PostgreSQL...
¡Éxito total! Datamart histórico creado y archivo base_emergencias_limpia.csv actualizado.
```

**Resultado:** Se creará la tabla `emergencias_nacionales_consolidado` en PostgreSQL y el archivo `base_emergencias_limpia.csv` en la raíz del proyecto.

---

### Opción B — MySQL (Versión Alternativa)

Esta versión carga la base de delitos interna junto con una fuente externa (carpetas FGJ) y las inserta en una base MySQL.

**Paso 1 — Crear base de datos en MySQL**

```sql
CREATE DATABASE bd_plataforma_mexico;
```

**Paso 2 — Instalar dependencias adicionales**

```bash
pip install pandas sqlalchemy pymysql
```

**Paso 3 — Configurar credenciales en `etl_maestro_mysql.py`**

```python
USUARIO   = "root"            # ← Tu usuario de MySQL
CONTRASENA = "tu_contraseña"  # ← Tu contraseña real
HOST      = "127.0.0.1"
PUERTO    = "3306"
BASE_DATOS = "bd_plataforma_mexico"
```

> [!WARNING]
> Esta versión también requiere el archivo `carpetasFGJ_2024.csv` como fuente externa. Asegúrate de tenerlo en la raíz del proyecto antes de ejecutar.

**Paso 4 — Ejecutar**

```bash
python etl_maestro_mysql.py
```

**Tablas que se crearán:**

| Tabla | Descripción |
|-------|-------------|
| `tabla_delitos_propia` | Registros de la base interna de delitos |
| `tabla_delitos_externa` | Registros de carpetas FGJ |
| `vista_delitos_combinada` | JOIN cruzado por fecha |

---

## Reglas de Negocio y Transformaciones

El principal reto técnico fue homologar dos bases de datos con **formatos completamente diferentes**. Las transformaciones aplicadas fueron:

### 1. Normalización de Columnas
```python
df_atus.columns = df_atus.columns.str.strip()
```
Los archivos ATUS vienen con espacios y tabuladores en los nombres de columnas.

### 2. Mapeo de Estados (Diccionario INEGI)
```python
diccionario_estados = {
    1: 'Aguascalientes', 2: 'Baja California', ..., 32: 'Zacatecas'
}
df_atus['estado'] = df_atus['ID_ENTIDAD'].map(diccionario_estados)
```
La base ATUS codifica las entidades como IDs numéricos del `01` al `32`. El diccionario convierte estos códigos a los nombres oficiales de los **32 estados de la República Mexicana**.

### 3. Construcción de Fecha ISO 8601
```python
df_atus['fecha'] = pd.to_datetime(
    dict(year=df_atus.ANIO, month=df_atus.MES, day=df_atus.ID_DIA),
    errors='coerce'
)
df_atus['fecha'] = df_atus['fecha'].dt.strftime('%Y-%m-%d')
```
Las fechas en el ATUS vienen en columnas separadas (`ANIO`, `MES`, `ID_DIA`) y se consolidan al formato estándar `YYYY-MM-DD`.

### 4. Filtrado de Registros Inválidos ("Vacuna INEGI")
```python
df_atus = df_atus[(df_atus['ID_DIA'] <= 31) & (df_atus['MES'] <= 12)]
df_atus = df_atus.dropna(subset=['fecha'])
```
El ATUS contiene registros con valores atípicos como `ID_DIA = 99` o textos en campos numéricos, los cuales se eliminan antes del cruce.

### 5. Agrupación y INNER JOIN
```python
delitos_agrupados   = df_delitos.groupby(['fecha','estado']).size().reset_index(name='total_delitos')
accidentes_agrupados = df_atus.groupby(['fecha','estado']).size().reset_index(name='total_accidentes')
df_final = pd.merge(delitos_agrupados, accidentes_agrupados, on=['fecha','estado'], how='inner')
df_final['total_emergencias'] = df_final['total_delitos'] + df_final['total_accidentes']
```
Ambas fuentes se agrupan por `[fecha, estado]` y se cruzan mediante un `INNER JOIN`, generando una métrica unificada de emergencias.

---

## Esquema de la Base de Datos

La tabla principal generada por el ETL es `emergencias_nacionales_consolidado`:

```sql
CREATE TABLE emergencias_nacionales_consolidado (
    id                SERIAL PRIMARY KEY,
    fecha             DATE         NOT NULL,   -- Fecha del registro (YYYY-MM-DD)
    estado            VARCHAR(100) NOT NULL,   -- Nombre oficial del estado
    total_delitos     INTEGER      NOT NULL DEFAULT 0,
    total_accidentes  INTEGER      NOT NULL DEFAULT 0,
    total_emergencias INTEGER      NOT NULL DEFAULT 0
);

-- Índices para optimización de consultas
CREATE INDEX idx_estado ON emergencias_nacionales_consolidado(estado);
CREATE INDEX idx_fecha  ON emergencias_nacionales_consolidado(fecha);
```

### Ejemplo de datos consolidados

| fecha | estado | total_delitos | total_accidentes | total_emergencias |
|-------|--------|:---:|:---:|:---:|
| 2024-01-05 | Ciudad de México | 142 | 87 | **229** |
| 2024-01-05 | Estado de México | 134 | 72 | **206** |
| 2024-01-05 | Jalisco | 98 | 63 | **161** |
| 2024-01-05 | Nuevo León | 88 | 54 | **142** |
| 2024-01-05 | Guanajuato | 76 | 41 | **117** |

---

## Análisis SQL y Resultados

Una vez cargado el datamart, se ejecutan consultas analíticas para extraer inteligencia de negocio.

> Los scripts completos se encuentran en [`consultas_rodrigo.sql`](./consultas_rodrigo.sql).
> Los resultados documentados se encuentran en [`Reporte de Consulta`](./Reporte%20de%20Consulta).

---

### Consulta 1 — TOP 10 Estados con Más Emergencias

```sql
SELECT
    estado,
    SUM(total_emergencias)  AS emergencias_totales,
    SUM(total_delitos)      AS total_delitos,
    SUM(total_accidentes)   AS total_accidentes
FROM emergencias_nacionales_consolidado
GROUP BY estado
ORDER BY emergencias_totales DESC
LIMIT 10;
```

#### Resultado

| # | Estado | Emergencias Totales | Total Delitos | Total Accidentes |
|:-:|--------|:-------------------:|:-------------:|:----------------:|
| 1 | Ciudad de México | **927** | 576 | 351 |
| 2 | Estado de México | **831** | 538 | 293 |
| 3 | Jalisco | **674** | 409 | 265 |
| 4 | Nuevo León | **596** | 366 | 230 |
| 5 | Guanajuato | **499** | 318 | 181 |
| 6 | Chihuahua | **488** | 298 | 190 |
| 7 | Baja California | **452** | 282 | 170 |
| 8 | Veracruz | **438** | 274 | 164 |
| 9 | Tamaulipas | **413** | 258 | 155 |
| 10 | Puebla | **396** | 250 | 146 |

> [!NOTE]
> **Ciudad de México** encabeza la lista con **927 emergencias acumuladas** en el periodo enero–abril 2024, siendo los delitos (576) la categoría predominante sobre los accidentes viales (351).

---

### Consulta 2 — Tendencia Temporal por Estado y Mes

```sql
SELECT
    estado,
    EXTRACT(YEAR  FROM fecha::DATE) AS anio,
    EXTRACT(MONTH FROM fecha::DATE) AS mes,
    SUM(total_emergencias) AS emergencias_mes
FROM emergencias_nacionales_consolidado
GROUP BY estado, anio, mes
ORDER BY anio, mes, emergencias_mes DESC;
```

#### Resultado — Enero 2024 (Top 20)

| Estado | Año | Mes | Emergencias |
|--------|:---:|:---:|:-----------:|
| Ciudad de México | 2024 | 1 | 229 |
| Estado de México | 2024 | 1 | 206 |
| Jalisco | 2024 | 1 | 161 |
| Nuevo León | 2024 | 1 | 142 |
| Guanajuato | 2024 | 1 | 117 |
| Chihuahua | 2024 | 1 | 115 |
| Baja California | 2024 | 1 | 106 |
| Veracruz | 2024 | 1 | 103 |
| Tamaulipas | 2024 | 1 | 97 |
| Puebla | 2024 | 1 | 92 |

> La consulta completa retorna **128 filas** (32 estados × 4 meses). La tabla muestra enero como muestra representativa del patrón mensual.

---

### Consulta 3 — INNER JOIN: Delitos vs Accidentes por Estado

```sql
SELECT
    a.estado,
    SUM(a.total_delitos)     AS total_delitos_estado,
    SUM(b.total_accidentes)  AS total_accidentes_estado,
    SUM(a.total_delitos) + SUM(b.total_accidentes) AS gran_total_emergencias
FROM emergencias_nacionales_consolidado AS a
    INNER JOIN emergencias_nacionales_consolidado AS b
        ON a.estado = b.estado AND a.fecha = b.fecha
GROUP BY a.estado
ORDER BY gran_total_emergencias DESC;
```

#### Resultado — Los 32 Estados

| Estado | Total Delitos | Total Accidentes | Gran Total |
|--------|:-------------:|:----------------:|:----------:|
| Ciudad de México | 576 | 351 | **927** |
| Estado de México | 538 | 293 | **831** |
| Jalisco | 409 | 265 | **674** |
| Nuevo León | 366 | 230 | **596** |
| Guanajuato | 318 | 181 | **499** |
| Chihuahua | 298 | 190 | **488** |
| Baja California | 282 | 170 | **452** |
| Veracruz | 274 | 164 | **438** |
| Tamaulipas | 258 | 155 | **413** |
| Puebla | 250 | 146 | **396** |
| Michoacán | 222 | 138 | **360** |
| Sinaloa | 226 | 134 | **360** |
| Sonora | 206 | 126 | **332** |
| Guerrero | 190 | 115 | **305** |
| Coahuila | 182 | 111 | **293** |
| San Luis Potosí | 166 | 102 | **268** |
| Oaxaca | 158 | 95 | **253** |
| Querétaro | 154 | 91 | **245** |
| Chiapas | 146 | 87 | **233** |
| Zacatecas | 138 | 83 | **221** |
| Hidalgo | 138 | 83 | **221** |
| Tabasco | 130 | 79 | **209** |
| Morelos | 122 | 75 | **197** |
| Quintana Roo | 118 | 71 | **189** |
| Durango | 110 | 67 | **177** |
| Aguascalientes | 102 | 62 | **164** |
| Yucatán | 98 | 59 | **157** |
| Colima | 86 | 51 | **137** |
| Nayarit | 78 | 47 | **125** |
| Tlaxcala | 70 | 42 | **112** |
| Campeche | 62 | 38 | **100** |
| Baja California Sur | 55 | 34 | **89** |

> [!IMPORTANT]
> El `INNER JOIN` cruza los registros usando `estado` y `fecha` como llaves de unión. Esto confirma que ambas fuentes están correctamente homologadas en la tabla `emergencias_nacionales_consolidado`.

---

## Visualización en Power BI

El archivo [`graficas_1.pbix`](./graficas_1.pbix) contiene el dashboard interactivo construido sobre el datamart generado. La versión exportada en PDF está disponible en [`graficas_1.pdf`](./graficas_1.pdf).

El reporte incluye:

- Mapa coroplético de México con intensidad de emergencias por estado
- Gráfica de tendencia mensual (Enero–Abril 2024)
- Tarjetas KPI: total nacional de delitos, accidentes y emergencias
- Tabla comparativa Top 10 estados críticos

> [!TIP]
> Para abrir el `.pbix`, asegúrate de tener instalado **Power BI Desktop** (versión gratuita disponible en [powerbi.microsoft.com](https://powerbi.microsoft.com/)). Actualiza la fuente de datos apuntando al archivo `base_emergencias_limpia.csv` local.

---

## Resultados Ejecutivos

| Métrica | Valor |
|---------|-------|
| Periodo analizado | Enero – Abril 2024 |
| Estados analizados | 32 |
| Total de registros en el datamart | 128 |
| Estado con más emergencias | Ciudad de México (**927**) |
| Estado con menos emergencias | Baja California Sur (**89**) |
| Total nacional de delitos | **3,814** |
| Total nacional de accidentes | **2,247** |
| **Total nacional de emergencias** | **6,061** |

---

> **Instituto Tecnológico de Oaxaca (ITO)** · Ingeniería en Sistemas Computacionales  
> Asignatura: Base de Datos · Semestre 2025 · Equipo 4
