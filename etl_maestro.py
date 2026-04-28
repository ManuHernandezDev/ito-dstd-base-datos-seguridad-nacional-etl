import pandas as pd
from sqlalchemy import create_engine

# ==================== CONFIGURACION DE BASE DE DATOS ====================
USUARIO = "postgres"
CONTRASENA = "Max22161097" 
HOST = "127.0.0.1"
PUERTO = "5432"
BASE_DATOS = "bd_plataforma_mexico" # Creen esta base en pgAdmin antes de correr el script

def ejecutar_etl_completo():
    URL_DB = f"postgresql://{USUARIO}:{CONTRASENA}@{HOST}:{PUERTO}/{BASE_DATOS}"
    engine = create_engine(URL_DB)
    
    print("Iniciando fase de EXTRACCION...")
    # 1. Extraer Base Propia (100k registros)
    df_propia = pd.read_csv('datos_delictivos_no_normalizados.csv', encoding='utf-8')
    df_propia.columns = [str(c).strip().lower() for c in df_propia.columns]
    
    # 2. Extraer Base Externa FGJ CDMX (138k registros)
    df_externa = pd.read_csv('carpetasFGJ_2024.csv', encoding='utf-8')
    df_externa.columns = [str(c).strip().lower() for c in df_externa.columns]
    
    print(f"Bases cargadas en memoria: Propia ({len(df_propia)} filas), Externa ({len(df_externa)} filas)")

    # ==================== FASE DE TRANSFORMACION Y UNION ====================
    print("Realizando la TRANSFORMACION (Limpieza y Union)...")
    
    # Para poder unir dos bases masivas sin que la PC explote, las agrupamos por fecha
    # Cuantos delitos hubo por dia en nuestra base vs la externa
    conteo_propia = df_propia.groupby('fecha').size().reset_index(name='total_delitos_propia')
    conteo_externa = df_externa.groupby('fecha_hecho').size().reset_index(name='total_delitos_externa')
    
    # Aqui esta el "JOIN" que pide la profesora (Unir base externa con la propia)
    df_combinada = pd.merge(
        conteo_propia, 
        conteo_externa, 
        left_on='fecha', 
        right_on='fecha_hecho', 
        how='inner' # Solo dias donde hubo delitos en ambas bases
    )
    
    # ==================== FASE DE CARGA ====================
    print("Iniciando fase de CARGA hacia PostgreSQL...")
    
    # Subimos las tablas crudas para que Power BI tenga todos los detalles
    df_propia.to_sql('tabla_delitos_propia', engine, if_exists='replace', index=False)
    df_externa.to_sql('tabla_delitos_externa', engine, if_exists='replace', index=False)
    
    # Subimos la tabla combinada que demuestra la union
    df_combinada.to_sql('vista_delitos_combinada', engine, if_exists='replace', index=False)
    
    print("EXITO! ETL Finalizado. Las bases estan listas en PostgreSQL.")
    # Exportar la tabla final combinada para usarla en Looker Studio o cualquier otro software
    print("Exportando tabla final para el equipo...")
    df_combinada.to_csv('base_final_para_looker.csv', index=False, encoding='utf-8')
    print("¡Archivo 'base_final_para_looker.csv' creado con éxito!")

if __name__ == "__main__":
    ejecutar_etl_completo()