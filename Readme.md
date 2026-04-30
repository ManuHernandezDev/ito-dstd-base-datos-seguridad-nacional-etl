# Guía de Ejecución y Sistema ETL: Consolidación de Emergencias Nacionales

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

## Descripción del Proyecto

Este repositorio contiene el pipeline ETL (Extract, Transform, Load) desarrollado en Python para cruzar registros masivos de Delitos a nivel nacional con la base de datos de Accidentes de Tránsito en Zonas Urbanas y Suburbanas (ATUS) de INEGI.

El objetivo es suministrar un datamart consolidado a herramientas de Business Intelligence (Power BI/Looker) para identificar los estados y fechas con mayores colapsos en la atención de emergencias del 911.

## Requisitos de Entorno

- Python 3.8 o superior.
- Servidor local de PostgreSQL.
- Librerías: `pandas`, `sqlalchemy`, `psycopg2-binary`.

## Instrucciones de Ejecución (Para el Equipo)

1. Clonar este repositorio en su máquina local.
2. Asegurarse de tener en la raíz los archivos originales (`datos_delictivos_no_normalizados.csv` y `atus_anual_2024.csv`).
3. Crear una base de datos vacía en pgAdmin llamada `bd_emergencias_nacional`.
4. Abrir `etl_emergencias.py`, modificar las credenciales de conexión (`USUARIO` y `CONTRASENA`) según su configuración local.
5. Ejecutar el script:
   ```bash
   python etl_emergencias.py
   ```
6. El script realizará la transformación de catálogos INEGI, ejecutará el cruce y creará la tabla `emergencias_nacionales_consolidado` en PostgreSQL. Además, generará el archivo físico `base_emergencias_limpia.csv` para uso en la fase de visualización.

## Texto para reporte

**2. Fase de Extracción y Transformación Programada**
Para el desarrollo de este proyecto, se implementó un script en Python utilizando la librería `pandas` para procesar de forma masiva dos fuentes de datos independientes.

**Reglas de Negocio Aplicadas (Limpieza):**
El principal reto de la transformación fue lograr el cruce (JOIN) entre la base operativa de delitos y la base de Accidentes Viales (ATUS). La base ATUS presentaba la entidad federativa codificada en un catálogo numérico (ID_ENTIDAD del 01 al 32) y las fechas desglosadas en múltiples columnas (Año, Mes, Día).

En la etapa de transformación mediante código, se aplicó un diccionario de equivalencias (Mapeo) para convertir los IDs numéricos del INEGI a los nombres oficiales de los 32 estados de la República en formato texto. Adicionalmente, se concatenaron y formatearon las columnas temporales para generar un formato estándar ISO 8601 (`YYYY-MM-DD`).
Una vez homologadas ambas llaves de cruce (`fecha` y `estado`), se realizó un `INNER JOIN` para obtener el conteo consolidado de emergencias por zona geográfica.
