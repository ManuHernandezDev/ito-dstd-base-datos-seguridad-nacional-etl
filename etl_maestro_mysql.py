import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# ==================== CONFIGURACION DE BASE DE DATOS ====================
USUARIO = "root"  # o el usuario que uses en MySQL
CONTRASENA = quote_plus("E@e$l@c@d3m7s1") 
HOST = "127.0.0.1"
PUERTO = "3306"
BASE_DATOS = "bd_plataforma_mexico"  # Crear antes en MySQL


def ejecutar_etl_completo():
    # IMPORTANTE: necesitas instalar pymysql -> pip install pymysql
    URL_DB = f"mysql+pymysql://{USUARIO}:{CONTRASENA}@{HOST}:{PUERTO}/{BASE_DATOS}"
    engine = create_engine(URL_DB)
    
    print("Iniciando fase de EXTRACCION...")
    
    # 1. Base propia
    df_propia = pd.read_csv('datos_delictivos_no_normalizados.csv', encoding='utf-8')
    df_propia.columns = [str(c).strip().lower() for c in df_propia.columns]
    
    # 2. Base externa
    df_externa = pd.read_csv('carpetasFGJ_2024.csv', encoding='utf-8')
    df_externa.columns = [str(c).strip().lower() for c in df_externa.columns]
    
    print(f"Bases cargadas: Propia ({len(df_propia)} filas), Externa ({len(df_externa)} filas)")

    # ==================== TRANSFORMACION ====================
    print("Transformando datos...")
    
    conteo_propia = df_propia.groupby('fecha').size().reset_index(name='total_delitos_propia')
    conteo_externa = df_externa.groupby('fecha_hecho').size().reset_index(name='total_delitos_externa')
    
    df_combinada = pd.merge(
        conteo_propia, 
        conteo_externa, 
        left_on='fecha', 
        right_on='fecha_hecho', 
        how='inner'
    )
    
    # ==================== CARGA ====================
    print("Cargando a MySQL...")
    
    df_propia.to_sql('tabla_delitos_propia', engine, if_exists='replace', index=False)
    df_externa.to_sql('tabla_delitos_externa', engine, if_exists='replace', index=False)
    df_combinada.to_sql('vista_delitos_combinada', engine, if_exists='replace', index=False)
    
    print("EXITO! ETL completado en MySQL.")

if __name__ == "__main__":
    ejecutar_etl_completo()