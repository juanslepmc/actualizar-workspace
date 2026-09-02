import pandas as pd
import unicodedata
import re
import os

def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).upper()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^A-Z0-9\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def normalizar_run(run):
    if pd.isna(run):
        return ""
    return str(run).replace('.', '').strip()

def normalizar_rbd(rbd):
    if pd.isna(rbd):
        return ""
    rbd_str = str(rbd).replace('.', '').strip()
    return rbd_str.split('-')[0]

def procesar_cuentas(nombre_archivo_a, nombre_archivo_b, directorio_base="", directorio_salida="Resultados"):
    
    ruta_a = os.path.join(directorio_base, nombre_archivo_a) if directorio_base else nombre_archivo_a
    ruta_b = os.path.join(directorio_base, nombre_archivo_b) if directorio_base else nombre_archivo_b
    
    def cargar_archivo(ruta):
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No se encontró el archivo en la ruta: {ruta}")
        
        if ruta.endswith('.xlsx') or ruta.endswith('.xls'):
            df = pd.read_excel(ruta, dtype={'RBD': str})
        else:
            df = pd.read_csv(ruta, dtype={'RBD': str})
            
        df.columns = df.columns.str.strip()
        return df

    df_a = cargar_archivo(ruta_a)
    df_b = cargar_archivo(ruta_b)

    # 1. Normalizar Archivo A
    df_a['First_Name_norm'] = df_a['First Name [Required]'].apply(normalizar_texto)
    df_a['Last_Name_norm'] = df_a['Last Name [Required]'].apply(normalizar_texto)
    df_a['RBD_norm'] = df_a['RBD'].apply(normalizar_rbd)
    df_a['Establecimiento_norm'] = df_a['Establecimiento'].apply(normalizar_texto)
    
    df_a['ID'] = (df_a['First_Name_norm'] + df_a['Last_Name_norm'] + df_a['RBD_norm']).str.replace(" ", "")
    df_a['ID_A'] = df_a['ID'] 

    # 2. Diccionarios
    mapeo_jardines_raw = {
        "Sala Cuna Jardín Infantil Abejita Dul": "7102015",
        "Sala Cuna Jardín Infantil Caracolitos": "7102014",
        "SALA CUNA JARDIN INFANTIL ANTONIO VARAS": "7201013",
        "SALA CUNA JARDIN INFANTIL BELLAVISTA": "7201005",
        "Sala Cuna Jardín Carita de Ángel": "7202003",
        "Sala Cuna Jardín Infantil Claro de Luna": "7201009",
        "Sala Cuna Jardín Infantil Los Grillitos de Porongo": "7201011",
        "Sala Cuna Jardín Infantil Mi Pequeño Mundo": "7104009",
        "Sala Cuna Jardín Infantil Lucerito de Esperanza": "7203003",
        "Sala Cuna Jardín Infantil La Casita en el Bosque": "7203001",
        "Sala Cuna Jardín Infantil Personitas": "7102010",
        "Sala Cuna Jardín Infantil Sol de Esperanza": "7203003",
    }
    
    mapeo_establecimientos_raw = {
        "LICEO DE CONSTITUCION": "Liceo Constitución",
        "LICEO TECNICO PROFESIONAL PUTU": "Liceo Bicentenario de Excelencia Técnico Profesional",
        "SALA CUNA JARDIN PERSONITAS DE SANTA OLGA": "Sala Cuna Jardín Infantil Personitas",
        "ESCUELA SAN ALFONSO CANELILLO": "Escuela San Alfonso de Canelillo",
        "LICEO CLAUDINA URRUTIA DE LAVIN": "Liceo de Anticipación Claudina Urrutia de Lavín",
        "SALA CUNA JARDIN INFANTIL LOS GRILLITOS": "Sala Cuna Jardín Infantil Los Grillitos de Porongo",
        "SALA CUNA JARDIN ABEJITA DUL": "Sala Cuna Jardín Infantil Abejita Dul",
        "ESCUELA JOSE MUÑOZ LABRA (ex Rincon de Pilen)": "Escuela José Dolores Muñoz Labra - Ex Rincón de Pilen",
        "ESCUELA JOSE RIVAS HERNANDEZ": "Escuela José Rivas Hernández de Cardonal",
        "ESCUELA MARIANO LATORRE": "Escuela Penitenciaria Mariano Latorre",
        "SALA CUNA JARDIN LA CASITA EN EL BOSQUE": "Sala Cuna Jardín Infantil La Casita en el Bosque",
        "SALA CUNA JARDIN CARACOLITOS": "Sala Cuna Jardín Infantil Caracolitos",
        "SALA CUNA JARDIN INFANTIL CARITA DE ANGEL": "Sala Cuna Jardín Carita de Ángel"
    }

    mapeo_jardines = {normalizar_texto(k).replace(" ", ""): v for k, v in mapeo_jardines_raw.items()}
    # Se normalizan tanto las llaves como los valores para un cruce impecable
    mapeo_est_norm = {normalizar_texto(k): normalizar_texto(v) for k, v in mapeo_establecimientos_raw.items()}

    # Función de evaluación bidireccional de establecimientos
    def son_mismos_establecimientos(est_a, est_b):
        if est_a == est_b:
            return True
        if mapeo_est_norm.get(est_a) == est_b:
            return True
        if mapeo_est_norm.get(est_b) == est_a:
            return True
        return False

    # 3. Normalizar Archivo B
    df_b['Nombres_norm'] = df_b['Nombres'].apply(normalizar_texto)
    df_b['Ap_Paterno_norm'] = df_b['Apellido Paterno'].apply(normalizar_texto)
    df_b['Ap_Materno_norm'] = df_b['Apellido Materno'].apply(normalizar_texto)
    df_b['Centro_Costo_norm'] = df_b['Centro Costo'].apply(normalizar_texto)
    
    def rellenar_rbd_jardin(row):
        rbd_actual = str(row.get('RBD', '')).strip()
        if pd.isna(row.get('RBD')) or rbd_actual == "" or rbd_actual == "nan":
            cc_sin_espacios = str(row['Centro_Costo_norm']).replace(" ", "")
            if cc_sin_espacios in mapeo_jardines:
                return mapeo_jardines[cc_sin_espacios]
        return row['RBD']
        
    df_b['RBD'] = df_b.apply(rellenar_rbd_jardin, axis=1)
    df_b['RBD_norm'] = df_b['RBD'].apply(normalizar_rbd)
    df_b['RUN_norm'] = df_b['R.U.N'].apply(normalizar_run)
    
    df_b['ID'] = (df_b['Nombres_norm'] + df_b['Ap_Paterno_norm'] + df_b['Ap_Materno_norm'] + df_b['RBD_norm']).str.replace(" ", "")
    df_b['ID_B'] = df_b['ID'] 

    # 4. Cruce de datos
    df_merge = pd.merge(df_a, df_b, on='ID', how='outer', indicator=True)
    df_match = df_merge[df_merge['_merge'] == 'both'].copy()
    
    def determinar_ou(row):
        if son_mismos_establecimientos(row['Establecimiento_norm'], row['Centro_Costo_norm']):
            return row['Org Unit Path [Required]']
        else:
            comuna = row.get('Comuna', '')
            comuna = "" if pd.isna(comuna) else str(comuna)
            
            rbd_n = row.get('RBD_norm_y', row.get('RBD_norm', ''))
            cc_n = row.get('Centro_Costo_norm', '')
            tipo = row.get('Tipo', '')
            tipo = "" if pd.isna(tipo) else str(tipo)
            
            return f"/Comunas/{comuna}/{rbd_n} {cc_n}/{tipo}"

    if not df_match.empty:
        df_match['Employee ID'] = df_match['RUN_norm']
        df_match['Org Unit Path [Required]'] = df_match.apply(determinar_ou, axis=1)
        
        # Ahora detectará correctamente si son equivalentes según tu diccionario y no mostrará un falso traslado
        df_match['Nuevo Establecimiento'] = df_match.apply(
            lambda row: row['Centro Costo'] if not son_mismos_establecimientos(row['Establecimiento_norm'], row['Centro_Costo_norm']) else "", axis=1
        )

    # 5. Estructurar archivos de salida
    def estructurar_salida(df, origen):
        out = pd.DataFrame()
        if origen == 'both':
            out['First Name [Required]'] = df['First Name [Required]']
            out['Last Name [Required]'] = df['Last Name [Required]']
            out['Email Address [Required]'] = df['Email Address [Required]']
            out['Employee ID'] = df['Employee ID']
            out['Org Unit Path [Required]'] = df['Org Unit Path [Required]']
            out['RBD'] = df.get('RBD_x', df.get('RBD', ''))
            out['Establecimiento'] = df['Establecimiento']
            out['Nuevo Establecimiento'] = df.get('Nuevo Establecimiento', "")
            out['ID_A'] = df['ID_A']
            out['ID_B'] = df['ID_B']
        elif origen == 'A':
            out['First Name [Required]'] = df['First Name [Required]']
            out['Last Name [Required]'] = df['Last Name [Required]']
            out['Email Address [Required]'] = df['Email Address [Required]']
            out['Employee ID'] = df['Employee ID'] if 'Employee ID' in df.columns else ""
            out['Org Unit Path [Required]'] = df['Org Unit Path [Required]']
            out['Org Unit Path nuevo [Required]'] = "/Archivados Funcionarios"
            out['RBD'] = df.get('RBD_x', df.get('RBD', ''))
            out['Establecimiento'] = df['Establecimiento']
            out['ID_A'] = df['ID_A']
            out['ID_B'] = df['ID_B']
        elif origen == 'B':
            out['First Name [Required]'] = df['Nombres']
            out['Last Name [Required]'] = df['Apellido Paterno'].fillna('') + " " + df['Apellido Materno'].fillna('')
            out['Email Address [Required]'] = ""
            out['Employee ID'] = df['RUN_norm']
            out['Org Unit Path [Required]'] = "" 
            out['RBD'] = df.get('RBD_norm_y', df.get('RBD_norm', ''))
            out['Establecimiento'] = df['Centro Costo']
            out['ID_A'] = df['ID_A']
            out['ID_B'] = df['ID_B']
            
        if not out.empty:
            out['Last Name [Required]'] = out['Last Name [Required]'].str.strip()
        return out

    out_match = estructurar_salida(df_match, 'both')
    out_solo_a = estructurar_salida(df_merge[df_merge['_merge'] == 'left_only'].copy(), 'A')
    out_solo_b = estructurar_salida(df_merge[df_merge['_merge'] == 'right_only'].copy(), 'B')

    # 6. Exportar y Estadísticas
    os.makedirs(directorio_salida, exist_ok=True)
    out_match.to_excel(os.path.join(directorio_salida, 'coincidencias.xlsx'), index=False)
    out_solo_a.to_excel(os.path.join(directorio_salida, 'solo_a_eliminar.xlsx'), index=False)
    out_solo_b.to_excel(os.path.join(directorio_salida, 'solo_b_nuevos.xlsx'), index=False)
    
    cambios_est = len(out_match[out_match['Nuevo Establecimiento'] != ""]) if not out_match.empty else 0
    nuevos = len(out_solo_b)
    eliminar = len(out_solo_a)

    print("\n--- RESUMEN DEL PROCESO ---")
    print(f"✅ Funcionarios con cambio de establecimiento detectado: {cambios_est}")
    print(f"➕ Funcionarios que se deben agregar (Solo B): {nuevos}")
    print(f"➖ Funcionarios que se deben eliminar/archivar (Solo A): {eliminar}")
    print(f"📁 Archivos guardados en la carpeta '{directorio_salida}'")


if __name__ == "__main__":
    procesar_cuentas(
        nombre_archivo_a="archivos/uso_workspace.xlsx", 
        nombre_archivo_b="archivos/dotacion_actualizada.xlsx",
        directorio_base="" 
    )
