import pandas as pd
from sqlalchemy import create_engine
import os

# --- 1. CONFIGURACIÓN DE BASE DE DATOS ---
USUARIO = "postgres"
CONTRASENA = "Max22161097" # Tu contraseña real
HOST = "127.0.0.1"
PUERTO = "5432"
BASE_DATOS = "bd_emergencias_nacional" # Nombre de la base en pg admin o mysql

# Diccionario Oficial INEGI para transformar el archivo ATUS
diccionario_estados = {
    1: 'Aguascalientes', 2: 'Baja California', 3: 'Baja California Sur', 4: 'Campeche',
    5: 'Coahuila de Zaragoza', 6: 'Colima', 7: 'Chiapas', 8: 'Chihuahua', 
    9: 'Ciudad de México', 10: 'Durango', 11: 'Guanajuato', 12: 'Guerrero', 
    13: 'Hidalgo', 14: 'Jalisco', 15: 'México', 16: 'Michoacán de Ocampo', 
    17: 'Morelos', 18: 'Nayarit', 19: 'Nuevo León', 20: 'Oaxaca', 
    21: 'Puebla', 22: 'Querétaro', 23: 'Quintana Roo', 24: 'San Luis Potosí', 
    25: 'Sinaloa', 26: 'Sonora', 27: 'Tabasco', 28: 'Tamaulipas', 
    29: 'Tlaxcala', 30: 'Veracruz de Ignacio de la Llave', 31: 'Yucatán', 32: 'Zacatecas'
}

def ejecutar_etl():
    print("Iniciando Extracción de Datos...")
    
    # --- 2. EXTRACCIÓN ---
    # Leer base histórica de Delitos (Contiene 2020 a 2025)
    print("Cargando base masiva de delitos...")
    df_delitos = pd.read_csv('datos_delictivos_no_normalizados.csv', encoding='utf-8', low_memory=False)
    
    # Leer e integrar múltiples bases de Accidentes ATUS (2020 a 2025)
    anios_atus = [2020, 2021, 2022, 2023, 2024, 2025]
    lista_df_atus = []
    
    for anio in anios_atus:
        nombre_archivo = f'atus_anual_{anio}.csv'
        if os.path.exists(nombre_archivo):
            print(f"Encontrado y cargando: {nombre_archivo}...")
            df_temp = pd.read_csv(nombre_archivo, encoding='latin-1', low_memory=False)
            lista_df_atus.append(df_temp)
        else:
            print(f"Advertencia: El archivo {nombre_archivo} no se encontró en la carpeta. Se omitirá.")
            
    if not lista_df_atus:
        print("ERROR CRÍTICO: No se encontró ningún archivo ATUS para procesar.")
        return
        
    # Unir todos los años de ATUS en un solo DataFrame masivo
    df_atus = pd.concat(lista_df_atus, ignore_index=True)
    print(f"Consolidación ATUS terminada. Total de registros viales: {len(df_atus)}")
    
    print("Iniciando Transformación y Limpieza...")
    print("Iniciando Transformación y Limpieza...")
    # --- 3. TRANSFORMACIÓN DE ATUS ---
    df_atus.columns = df_atus.columns.str.strip()
    df_atus['ID_ENTIDAD'] = df_atus['ID_ENTIDAD'].astype(str).str.replace('\t', '').astype(int)
    
    # ---------------------------------------------------------
    # NUEVO: FORZAR A NÚMERO (Limpia textos raros de años viejos)
    # ---------------------------------------------------------
    df_atus['ID_DIA'] = pd.to_numeric(df_atus['ID_DIA'], errors='coerce')
    df_atus['MES'] = pd.to_numeric(df_atus['MES'], errors='coerce')
    df_atus['ANIO'] = pd.to_numeric(df_atus['ANIO'], errors='coerce')
    
    # VACUNA INEGI: Filtrar registros válidos (descarta los NaN creados arriba y los días 99)
    df_atus = df_atus[(df_atus['ID_DIA'] <= 31) & (df_atus['MES'] <= 12)]
    
    # Crear columna fecha manejando errores (coerce convierte fechas inválidas en NaT)
    df_atus['fecha'] = pd.to_datetime(
        dict(year=df_atus.ANIO, month=df_atus.MES, day=df_atus.ID_DIA), 
        errors='coerce'
    )
    # Tirar los registros que no pudieron convertirse a fecha válida y dar formato
    df_atus = df_atus.dropna(subset=['fecha'])
    df_atus['fecha'] = df_atus['fecha'].dt.strftime('%Y-%m-%d')
    
    # Mapeo de Estados
    df_atus['estado'] = df_atus['ID_ENTIDAD'].map(diccionario_estados)
    
    # --- 4. AGRUPACIÓN Y CRUCE (JOIN) ---
    print("Agrupando y cruzando bases de datos por Estado y Fecha...")
    delitos_agrupados = df_delitos.groupby(['fecha', 'estado']).size().reset_index(name='total_delitos')
    accidentes_agrupados = df_atus.groupby(['fecha', 'estado']).size().reset_index(name='total_accidentes')
    
    df_final = pd.merge(delitos_agrupados, accidentes_agrupados, on=['fecha', 'estado'], how='inner')
    df_final['total_emergencias'] = df_final['total_delitos'] + df_final['total_accidentes']
    
    # --- 5. CARGA ---
    print(f"Cargando {len(df_final)} registros históricos a PostgreSQL...")
    engine = create_engine(f"postgresql://{USUARIO}:{CONTRASENA}@{HOST}:{PUERTO}/{BASE_DATOS}")
    
    # if_exists='replace' borrará tu tabla actual de 2024 y la recreará con todo el histórico 2020-2025
    df_final.to_sql('emergencias_nacionales_consolidado', engine, if_exists='replace', index=False)
    
    df_final.to_csv('base_emergencias_limpia.csv', index=False, encoding='utf-8')
    print("¡Éxito total! Datamart histórico creado y archivo base_emergencias_limpia.csv actualizado.")

if __name__ == "__main__":
    ejecutar_etl()