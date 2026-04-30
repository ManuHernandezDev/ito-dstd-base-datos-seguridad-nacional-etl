import pandas as pd
from sqlalchemy import create_engine

# --- 1. CONFIGURACIÓN DE BASE DE DATOS ---
USUARIO = "postgres"
CONTRASENA = "TuContrasena" # Tu contraseña real
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
    # Leer base de Delitos
    df_delitos = pd.read_csv('datos_delictivos_no_normalizados.csv', encoding='utf-8')
    
    # Leer base de Accidentes ATUS
    df_atus = pd.read_csv('atus_anual_2024.csv', encoding='latin-1')
    
    print("Iniciando Transformación y Limpieza...")
    # --- 3. TRANSFORMACIÓN DE ATUS ---
    # Limpiar columnas con caracteres raros y crear columna de fecha YYYY-MM-DD
    df_atus.columns = df_atus.columns.str.strip()
    df_atus['ID_ENTIDAD'] = df_atus['ID_ENTIDAD'].astype(str).str.replace('\t', '').astype(int)
    
    # Crear columna fecha en ATUS uniendo ANIO, MES y DIA
    df_atus['fecha'] = pd.to_datetime(dict(year=df_atus.ANIO, month=df_atus.MES, day=df_atus.ID_DIA)).dt.strftime('%Y-%m-%d')
    
    # Aplicar Regla de Negocio: Mapeo de Estados
    df_atus['estado'] = df_atus['ID_ENTIDAD'].map(diccionario_estados)
    
    # --- 4. AGRUPACIÓN Y CRUCE (JOIN) ---
    print("Cruzando bases de datos por Estado y Fecha...")
    # Contar delitos por día y estado
    delitos_agrupados = df_delitos.groupby(['fecha', 'estado']).size().reset_index(name='total_delitos')
    
    # Contar accidentes por día y estado
    accidentes_agrupados = df_atus.groupby(['fecha', 'estado']).size().reset_index(name='total_accidentes')
    
    # INNER JOIN: Dejar solo donde hay registros de ambos el mismo día
    df_final = pd.merge(delitos_agrupados, accidentes_agrupados, on=['fecha', 'estado'], how='inner')
    
    # Calcular métrica sumada para el Dashboard
    df_final['total_emergencias'] = df_final['total_delitos'] + df_final['total_accidentes']
    
    # --- 5. CARGA ---
    print("Cargando a la Base de Datos PostgreSQL...")
    engine = create_engine(f"postgresql://{USUARIO}:{CONTRASENA}@{HOST}:{PUERTO}/{BASE_DATOS}")
    
    # Subir la tabla combinada a SQL
    df_final.to_sql('emergencias_nacionales_consolidado', engine, if_exists='replace', index=False)
    
    # Exportar a CSV para que Baru haga el Dashboard
    df_final.to_csv('base_emergencias_limpia.csv', index=False, encoding='utf-8')
    print("¡Éxito! Base de datos creada y archivo base_emergencias_limpia.csv generado.")

if __name__ == "__main__":
    ejecutar_etl()