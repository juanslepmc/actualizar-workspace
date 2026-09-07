import pandas as pd
import unicodedata
import re
import os

# Encabezados oficiales de Google Workspace (29 columnas)
PLANTILLA_WORKSPACE_COLUMNAS = [
    'First Name [Required]', 'Last Name [Required]', 'Email Address [Required]', 
    'Password [Required]', 'Password Hash Function [UPLOAD ONLY]', 'Org Unit Path [Required]', 
    'New Primary Email [UPLOAD ONLY]', 'Recovery Email', 'Home Secondary Email', 
    'Work Secondary Email', 'Recovery Phone [MUST BE IN THE E.164 FORMAT]', 'Work Phone', 
    'Home Phone', 'Mobile Phone', 'Work Address', 'Home Address', 'Employee ID', 
    'Employee Type', 'Employee Title', 'Manager Email', 'Department', 'Cost Center', 
    'Building ID', 'Floor Name', 'Floor Section', 'Change Password at Next Sign-In', 
    'New Status [UPLOAD ONLY]', 'New Licenses [UPLOAD ONLY]', 
    'Advanced Protection Program enrollment'
]

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

def transformar_legislacion(valor):
    if pd.isna(valor):
        return ""
    val_norm = normalizar_texto(valor)
    if "ASISTENTES DE LA EDUCACION" in val_norm:
        return "Asistentes Educación"
    elif "ESTATUTO DOCENTE" in val_norm:
        return "Docentes"
    return str(valor).strip()

def sanitizar_nombre_archivo(nombre):
    """
    Limpia el nombre del establecimiento para usarlo como nombre de archivo válido en el sistema.
    """
    if pd.isna(nombre) or str(nombre).strip() == "":
        return "Sin_Establecimiento"
    nombre_clean = re.sub(r'[\\/*?:"<>|]', "", str(nombre))
    nombre_clean = re.sub(r'\s+', ' ', nombre_clean).strip()
    return nombre_clean if nombre_clean else "Sin_Establecimiento"

def formatear_csv_workspace(df_datos, mapping_cols=None, valores_fijos=None):
    """
    Genera el formato CSV exacto de Google Workspace (29 columnas).
    """
    out_df = pd.DataFrame('', index=range(len(df_datos)), columns=PLANTILLA_WORKSPACE_COLUMNAS)
    
    if mapping_cols:
        for col_tpl, col_src in mapping_cols.items():
            if col_src in df_datos.columns:
                out_df[col_tpl] = df_datos[col_src].fillna('').values
                
    if valores_fijos:
        for col_tpl, val in valores_fijos.items():
            out_df[col_tpl] = val
            
    return out_df

def estructurar_salida_excel(df, origen):
    """
    Estructura los DataFrames informativos para trazabilidad en Excel (.xlsx).
    """
    out = pd.DataFrame()
    if df.empty:
        return out

    if origen == 'both':
        out['First Name [Required]'] = df.get('First Name [Required]', '')
        out['Last Name [Required]'] = df.get('Last Name [Required]', '')
        out['Email Address [Required]'] = df.get('Email Address [Required]', '')
        out['Employee ID'] = df.get('Employee ID', df.get('RUN_norm', ''))
        out['Tipo'] = df['Tipo_x'] if 'Tipo_x' in df.columns else df.get('Tipo', '')
        out['Org Unit Path [Required]'] = df.get('Org Unit Path [Required]', '')
        out['RBD'] = df['RBD_x'] if 'RBD_x' in df.columns else df.get('RBD', '')
        out['Establecimiento'] = df.get('Establecimiento', '')
        out['Nuevo Establecimiento'] = df.get('Nuevo Establecimiento', '')
        out['ID_A'] = df.get('ID_A', '')
        out['ID_B'] = df.get('ID_B', '')
    elif origen == 'A':
        out['First Name [Required]'] = df.get('First Name [Required]', '')
        out['Last Name [Required]'] = df.get('Last Name [Required]', '')
        out['Email Address [Required]'] = df.get('Email Address [Required]', '')
        out['Employee ID'] = df.get('Employee ID', '')
        out['Tipo'] = df['Tipo_x'] if 'Tipo_x' in df.columns else df.get('Tipo', '')
        out['Org Unit Path [Required]'] = df.get('Org Unit Path [Required]', '')
        out['Org Unit Path nuevo [Required]'] = "/Archivados Funcionarios"
        out['RBD'] = df['RBD_x'] if 'RBD_x' in df.columns else df.get('RBD', '')
        out['Establecimiento'] = df.get('Establecimiento', '')
        out['ID_A'] = df.get('ID_A', '')
        out['ID_B'] = df.get('ID_B', '')
    elif origen == 'B':
        out['First Name [Required]'] = df.get('Nombres', '')
        out['Last Name [Required]'] = (df.get('Apellido Paterno', pd.Series()).fillna('') + " " + df.get('Apellido Materno', pd.Series()).fillna('')).str.strip()
        out['Email Address [Required]'] = ""
        out['Employee ID'] = df.get('RUN_norm', '')
        
        col_legis = df['Legislación Laboral_y'] if 'Legislación Laboral_y' in df.columns else df.get('Legislación Laboral', pd.Series())
        out['Tipo'] = col_legis.apply(transformar_legislacion) if isinstance(col_legis, pd.Series) else ""
        
        out['Org Unit Path [Required]'] = "" 
        rbd_b = df['RBD_norm_y'] if 'RBD_norm_y' in df.columns else df.get('RBD_norm', '')
        out['RBD'] = rbd_b
        out['Establecimiento'] = df.get('Centro Costo', '')
        out['ID_A'] = df.get('ID_A', '')
        out['ID_B'] = df.get('ID_B', '')

    if 'Last Name [Required]' in out.columns and not out.empty:
        out['Last Name [Required]'] = out['Last Name [Required]'].astype(str).str.strip()

    return out

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

    # 2. Diccionarios de mapeo
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
    mapeo_est_norm = {normalizar_texto(k): normalizar_texto(v) for k, v in mapeo_establecimientos_raw.items()}

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
            
            tipo = row.get('Tipo_x', row.get('Tipo', ''))
            tipo = "" if pd.isna(tipo) else str(tipo)
            
            return f"/Comunas/{comuna}/{rbd_n} {cc_n}/{tipo}"

    if not df_match.empty:
        df_match['Employee ID'] = df_match['RUN_norm']
        df_match['Org Unit Path [Required]'] = df_match.apply(determinar_ou, axis=1)
        
        df_match['Nuevo Establecimiento'] = df_match.apply(
            lambda row: row['Centro Costo'] if not son_mismos_establecimientos(row['Establecimiento_norm'], row['Centro_Costo_norm']) else "", axis=1
        )

    df_solo_a = df_merge[df_merge['_merge'] == 'left_only'].copy()
    df_solo_b = df_merge[df_merge['_merge'] == 'right_only'].copy()

    # 5. Generar DataFrames informativos para trazabilidad (Excel)
    excel_coincidencias = estructurar_salida_excel(df_match, 'both')
    excel_solo_a_eliminar = estructurar_salida_excel(df_solo_a, 'A')
    excel_solo_b_nuevos = estructurar_salida_excel(df_solo_b, 'B')

    # 6. Generar estructuras CSV consolidadas para Google Workspace (29 columnas)
    csv_match = formatear_csv_workspace(
        df_match,
        mapping_cols={
            'First Name [Required]': 'First Name [Required]',
            'Last Name [Required]': 'Last Name [Required]',
            'Email Address [Required]': 'Email Address [Required]',
            'Org Unit Path [Required]': 'Org Unit Path [Required]',
            'Employee ID': 'RUN_norm'
        }
    )

    csv_solo_a_eliminar = formatear_csv_workspace(
        df_solo_a,
        mapping_cols={
            'First Name [Required]': 'First Name [Required]',
            'Last Name [Required]': 'Last Name [Required]',
            'Email Address [Required]': 'Email Address [Required]',
            'Employee ID': 'Employee ID'
        },
        valores_fijos={
            'Org Unit Path [Required]': '/Archivados Funcionarios',
            'New Licenses [UPLOAD ONLY]': '1010070004',
            'New Status [UPLOAD ONLY]': 'Archived'
        }
    )

    # 7. Exportar los 5 archivos generales
    os.makedirs(directorio_salida, exist_ok=True)
    
    excel_coincidencias.to_excel(os.path.join(directorio_salida, 'coincidencias.xlsx'), index=False)
    excel_solo_a_eliminar.to_excel(os.path.join(directorio_salida, 'solo_a_eliminar.xlsx'), index=False)
    excel_solo_b_nuevos.to_excel(os.path.join(directorio_salida, 'solo_b_nuevos.xlsx'), index=False)

    csv_match.to_csv(os.path.join(directorio_salida, 'match.csv'), index=False, encoding='utf-8')
    csv_solo_a_eliminar.to_csv(os.path.join(directorio_salida, 'solo_a_eliminar.csv'), index=False, encoding='utf-8')

    # 8. GENERAR CARPETAS SEPARADAS POR ESTABLECIMIENTO
    dir_separados = os.path.join(directorio_salida, 'separados')
    dir_match_sep = os.path.join(dir_separados, 'match')
    dir_eliminar_sep = os.path.join(dir_separados, 'eliminar')

    os.makedirs(dir_match_sep, exist_ok=True)
    os.makedirs(dir_eliminar_sep, exist_ok=True)

    # 8.1 Separar CSVs de MATCH por establecimiento
    if not df_match.empty:
        # Usar el Centro Costo actualizado de B o el Establecimiento original de A
        df_match['Establecimiento_Grupo'] = df_match['Centro Costo'].fillna('').astype(str)
        df_match['Establecimiento_Grupo'] = df_match['Establecimiento_Grupo'].replace('', pd.NA).fillna(df_match['Establecimiento'])

        count_match_files = 0
        for est_nombre, grupo in df_match.groupby('Establecimiento_Grupo'):
            csv_sub_match = formatear_csv_workspace(
                grupo,
                mapping_cols={
                    'First Name [Required]': 'First Name [Required]',
                    'Last Name [Required]': 'Last Name [Required]',
                    'Email Address [Required]': 'Email Address [Required]',
                    'Org Unit Path [Required]': 'Org Unit Path [Required]',
                    'Employee ID': 'RUN_norm'
                }
            )
            nombre_file = f"{sanitizar_nombre_archivo(est_nombre)}.csv"
            csv_sub_match.to_csv(os.path.join(dir_match_sep, nombre_file), index=False, encoding='utf-8')
            count_match_files += 1

    # 8.2 Separar CSVs de ELIMINAR por establecimiento
    if not df_solo_a.empty:
        count_eliminar_files = 0
        for est_nombre, grupo in df_solo_a.groupby('Establecimiento'):
            csv_sub_eliminar = formatear_csv_workspace(
                grupo,
                mapping_cols={
                    'First Name [Required]': 'First Name [Required]',
                    'Last Name [Required]': 'Last Name [Required]',
                    'Email Address [Required]': 'Email Address [Required]',
                    'Employee ID': 'Employee ID'
                },
                valores_fijos={
                    'Org Unit Path [Required]': '/Archivados Funcionarios',
                    'New Licenses [UPLOAD ONLY]': '1010070004',
                    'New Status [UPLOAD ONLY]': 'Archived'
                }
            )
            nombre_file = f"{sanitizar_nombre_archivo(est_nombre)}.csv"
            csv_sub_eliminar.to_csv(os.path.join(dir_eliminar_sep, nombre_file), index=False, encoding='utf-8')
            count_eliminar_files += 1

    # 9. Resumen en consola
    cambios_est = len(df_match[df_match['Nuevo Establecimiento'] != ""]) if not df_match.empty else 0
    
    print("\n--- RESUMEN DEL PROCESO ---")
    print(f"✅ Coincidencias procesadas: {len(df_match)} (Con cambio de colegio: {cambios_est})")
    print(f"➕ Funcionarios a agregar (Solo B): {len(df_solo_b)}")
    print(f"➖ Funcionarios a eliminar/archivar (Solo A): {len(df_solo_a)}")
    print(f"\n📁 Archivos principales generados en '{directorio_salida}':")
    print("  Excel (.xlsx): coincidencias.xlsx | solo_a_eliminar.xlsx | solo_b_nuevos.xlsx")
    print("  CSV (.csv):   match.csv | solo_a_eliminar.csv")
    print(f"\n📂 Archivos individuales generados en '{dir_separados}':")
    print(f"  • {count_match_files} archivos creados en: separados/match/")
    print(f"  • {count_eliminar_files} archivos creados en: separados/eliminar/")

if __name__ == "__main__":
    procesar_cuentas(
        nombre_archivo_a="archivos/uso_workspace.xlsx", 
        nombre_archivo_b="archivos/dotacion_actualizada.xlsx",
        directorio_base="" 
    )