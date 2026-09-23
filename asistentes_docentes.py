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

ESTABLECIMIENTO_EXCLUIDO = "SERVICIO LOCAL MAULE COSTA P02"

# Diccionario Oficial de Establecimientos (68 RBDs)
DICCIONARIO_ESTABLECIMIENTOS_DEFAULT = {
    "3170": {"nombre": "CENTRO EDUCACIONAL CONSTITUCIÓN", "comuna": "Constitucion"},
    "3544": {"nombre": "COLEGIO BLANCO ENCALADA", "comuna": "Cauquenes"},
    "3552": {"nombre": "ESCUELA ADOLFO QUIROZ HERNANDEZ", "comuna": "Cauquenes"},
    "3541": {"nombre": "ESCUELA ANIBAL PINTO", "comuna": "Cauquenes"},
    "3632": {"nombre": "ESCUELA ANTONIETA LEON VERDUGO", "comuna": "Chanco"},
    "3545": {"nombre": "ESCUELA ARTISTICA BARRIO ESTACION", "comuna": "Cauquenes"},
    "3179": {"nombre": "ESCUELA BARRANQUILLAS", "comuna": "Constitucion"},
    "3616": {"nombre": "ESCUELA BENITO MANCILLA PEREZ", "comuna": "Pelluhue"},
    "3611": {"nombre": "ESCUELA BLANCA BUSTOS CASTILLO", "comuna": "Pelluhue"},
    "3604": {"nombre": "ESCUELA CABRERIA", "comuna": "Cauquenes"},
    "3623": {"nombre": "ESCUELA CARRERAS CORTAS", "comuna": "Chanco"},
    "3187": {"nombre": "ESCUELA CARRIZALILLO", "comuna": "Constitucion"},
    "3169": {"nombre": "ESCUELA CERRO ALTO JOSE OPAZO DIAZ", "comuna": "Constitucion"},
    "16506": {"nombre": "ESCUELA CHACARILLAS", "comuna": "Constitucion"},
    "3586": {"nombre": "ESCUELA CHORRILLOS", "comuna": "Cauquenes"},
    "3554": {"nombre": "ESCUELA CLORINDO ALVEAR", "comuna": "Cauquenes"},
    "3185": {"nombre": "ESCUELA COSTA BLANCA", "comuna": "Constitucion"},
    "3548": {"nombre": "ESCUELA ECOLOGICA ROSITA OHIGGINS", "comuna": "Cauquenes"},
    "3198": {"nombre": "ESCUELA EDUARDO MACHADO CORSI", "comuna": "Constitucion"},
    "3602": {"nombre": "ESCUELA EL TROZO", "comuna": "Cauquenes"},
    "3631": {"nombre": "ESCUELA EMA VASQUEZ GUTIERREZ", "comuna": "Chanco"},
    "3166": {"nombre": "ESCUELA ENRIQUE DONN MULLER", "comuna": "Constitucion"},
    "3615": {"nombre": "ESCUELA ESCRITORA MARCELA PAZ", "comuna": "Pelluhue"},
    "3537": {"nombre": "ESCUELA ESPECIAL HORIZONTE", "comuna": "Cauquenes"},
    "3625": {"nombre": "ESCUELA GABRIELA MISTRAL", "comuna": "Chanco"},
    "3610": {"nombre": "ESCUELA GLADYS CANALES PAREDES", "comuna": "Pelluhue"},
    "3564": {"nombre": "ESCUELA HECTOR SILVESTRE PAIVA MANRIQUEZ", "comuna": "Cauquenes"},
    "3546": {"nombre": "ESCUELA INDEPENDENCIA", "comuna": "Cauquenes"},
    "3569": {"nombre": "ESCUELA JAVIERA CARRERA", "comuna": "Cauquenes"},
    "3579": {"nombre": "ESCUELA JOSE MUÑOZ LABRA (ex Rincon de Pilen)", "comuna": "Cauquenes"},
    "3614": {"nombre": "ESCUELA JOSE RIVAS HERNANDEZ", "comuna": "Pelluhue"},
    "3176": {"nombre": "ESCUELA JUNQUILLAR", "comuna": "Constitucion"},
    "3596": {"nombre": "ESCUELA LA CAPILLA DE PILEN ALTO", "comuna": "Cauquenes"},
    "3174": {"nombre": "ESCUELA LAS CORRIENTES", "comuna": "Constitucion"},
    "3636": {"nombre": "ESCUELA LOANCO", "comuna": "Chanco"},
    "3551": {"nombre": "ESCUELA LOS CONQUISTADORES", "comuna": "Cauquenes"},
    "3619": {"nombre": "ESCUELA LOS HEROES", "comuna": "Chanco"},
    "3624": {"nombre": "ESCUELA LOS PEUMOS", "comuna": "Chanco"},
    "3177": {"nombre": "ESCUELA MARIA INES MAROMILLAS", "comuna": "Constitucion"},
    "3134": {"nombre": "ESCUELA MARIA OLGA VEGA VEGA", "comuna": "Empedrado"},
    "3186": {"nombre": "ESCUELA MIGUEL FAUNDEZ MORALES", "comuna": "Constitucion"},
    "3599": {"nombre": "ESCUELA MIXTA ATENEA", "comuna": "Cauquenes"},
    "3555": {"nombre": "ESCUELA OCTAVIO PALMA PEREZ", "comuna": "Cauquenes"},
    "3622": {"nombre": "ESCUELA PAHUIL", "comuna": "Chanco"},
    "3580": {"nombre": "ESCUELA PEDERNALES", "comuna": "Cauquenes"},
    "3130": {"nombre": "ESCUELA PEDRO ANTONIO TEJOS TEJOS", "comuna": "Empedrado"},
    "3573": {"nombre": "ESCUELA PEDRO DE VALDIVIA", "comuna": "Cauquenes"},
    "3549": {"nombre": "ESCUELA PORONGO", "comuna": "Cauquenes"},
    "3550": {"nombre": "ESCUELA PURISIMA CONCEPCION DE POCILLAS", "comuna": "Cauquenes"},
    "3633": {"nombre": "ESCUELA QUINIPATO", "comuna": "Chanco"},
    "3626": {"nombre": "ESCUELA RELOCA", "comuna": "Chanco"},
    "3630": {"nombre": "ESCUELA RICARDO SALGADO", "comuna": "Chanco"},
    "3190": {"nombre": "ESCUELA RURAL QUEBRADA VERDE", "comuna": "Constitucion"},
    "3612": {"nombre": "ESCUELA SAN ALFONSO CANELILLO", "comuna": "Pelluhue"},
    "3621": {"nombre": "ESCUELA SAN AMBROSIO", "comuna": "Chanco"},
    "3191": {"nombre": "ESCUELA SANTA AURORA DE CARRIZAL", "comuna": "Constitucion"},
    "3168": {"nombre": "ESCUELA SUPERIOR NUEVA BILBAO", "comuna": "Constitucion"},
    "3189": {"nombre": "ESCUELA TERESA CONSUELO", "comuna": "Constitucion"},
    "3538": {"nombre": "LICEO ANTONIO VARAS", "comuna": "Cauquenes"},
    "16751": {"nombre": "LICEO BICENTENARIO DE CAUQUENES", "comuna": "Cauquenes"},
    "3539": {"nombre": "LICEO CLAUDINA URRUTIA DE LAVIN", "comuna": "Cauquenes"},
    "3165": {"nombre": "LICEO DE CONSTITUCION", "comuna": "Constitucion"},
    "3618": {"nombre": "LICEO FEDERICO ALBERT FAUPP", "comuna": "Chanco"},
    "3609": {"nombre": "LICEO PELLUHUE", "comuna": "Pelluhue"},
    "3540": {"nombre": "LICEO POLITECNICO PEDRO AGUIRRE CERDA", "comuna": "Cauquenes"},
    "3173": {"nombre": "LICEO RURAL ENRIQUE MAC IVER", "comuna": "Constitucion"},
    "3128": {"nombre": "LICEO SAN IGNACIO", "comuna": "Empedrado"},
    "3172": {"nombre": "LICEO TECNICO PROFESIONAL PUTU", "comuna": "Constitucion"}
}

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
    if pd.isna(nombre) or str(nombre).strip() == "":
        return "Sin_Establecimiento"
    nombre_clean = re.sub(r'[\\/*?:"<>|]', "", str(nombre))
    nombre_clean = re.sub(r'\s+', ' ', nombre_clean).strip()
    return nombre_clean if nombre_clean else "Sin_Establecimiento"

def estandarizar_y_asegurar_columnas(df, columnas_requeridas, mapeo_alias=None):
    df.columns = df.columns.astype(str).str.strip()
    
    if mapeo_alias:
        renombrar = {}
        for col in df.columns:
            col_clean = str(col).strip().lower()
            if col_clean in mapeo_alias and mapeo_alias[col_clean] not in df.columns:
                renombrar[col] = mapeo_alias[col_clean]
        df = df.rename(columns=renombrar)
        
    for col_req in columnas_requeridas:
        if col_req not in df.columns:
            df[col_req] = ""
            
    return df

def formatear_csv_workspace(df_datos, mapping_cols=None, valores_fijos=None):
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
        out['Estado'] = df.apply(
            lambda r: "Cambio de Establecimiento" if str(r.get('Nuevo Establecimiento', '')).strip() != "" else "Sin Cambios", 
            axis=1
        )
        out['Tipo Contrato'] = df['Tipo Contrato_y'] if 'Tipo Contrato_y' in df.columns else df.get('Tipo Contrato', '')
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
        out['Tipo Contrato'] = df['Tipo Contrato_y'] if 'Tipo Contrato_y' in df.columns else df.get('Tipo Contrato', '')
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
            
        return df

    df_a = cargar_archivo(ruta_a)
    df_b = cargar_archivo(ruta_b)

    alias_a = {'employee id': 'Employee ID', 'employee id [upload only]': 'Employee ID', 'rut': 'Employee ID', 'run': 'Employee ID'}
    cols_req_a = ['First Name [Required]', 'Last Name [Required]', 'Email Address [Required]', 'Employee ID', 'RBD', 'Establecimiento', 'Tipo', 'Org Unit Path [Required]']
    df_a = estandarizar_y_asegurar_columnas(df_a, cols_req_a, alias_a)

    alias_b = {'r.u.n': 'R.U.N', 'run': 'R.U.N', 'rut': 'R.U.N'}
    cols_req_b = ['Nombres', 'Apellido Paterno', 'Apellido Materno', 'R.U.N', 'RBD', 'Centro Costo', 'Legislación Laboral', 'Tipo Contrato', 'Comuna']
    df_b = estandarizar_y_asegurar_columnas(df_b, cols_req_b, alias_b)

    df_a = df_a[df_a['Establecimiento'].apply(normalizar_texto) != ESTABLECIMIENTO_EXCLUIDO].copy()
    df_b = df_b[df_b['Centro Costo'].apply(normalizar_texto) != ESTABLECIMIENTO_EXCLUIDO].copy()

    df_a['First_Name_norm'] = df_a['First Name [Required]'].apply(normalizar_texto)
    df_a['Last_Name_norm'] = df_a['Last Name [Required]'].apply(normalizar_texto)
    df_a['RBD_norm'] = df_a['RBD'].apply(normalizar_rbd)
    df_a['Establecimiento_norm'] = df_a['Establecimiento'].apply(normalizar_texto)
    df_a['Employee_ID_norm'] = df_a['Employee ID'].apply(normalizar_run)
    df_a['ID'] = df_a['Employee_ID_norm']
    df_a['ID_A'] = df_a['ID']

    mask_sin_emp_id = df_a['Employee ID'].isna() | (df_a['Employee ID'].astype(str).str.strip() == '')
    df_sin_emp_id = df_a[mask_sin_emp_id].copy()
    df_a_valido = df_a[~mask_sin_emp_id].copy()

    mapeo_jardines_raw = {
        "Sala Cuna Jardín Infantil Abejita Dul": "7102015",
        "Sala Cuna Jardín Infantil Caracolitos": "7102014",
        "SALA CUNA JARDIN INFANTIL ANTONIO VARAS": "7201013",
        "SALA CUNA JARDIN INFANTIL BELLAVISTA": "7201005",
        "Sala Cuna Jardín Carita de Ángel": "7202003",
        "Sala Cuna Jardín Infantil Claro de Luna": "7201009",
        "Sala Cuna Jardín Infantil Los Grillitos de Porongo": "7201011",
        "Sala Cuna Jardín Infantil Mi Pequeño Mundo": "7104009",
        "Sala Cuna Jardín Infantil Lucerito de Esperanza": "7201010",
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
    df_b['ID'] = df_b['RUN_norm']
    df_b['ID_B'] = df_b['ID']

    df_b['ID'] = df_b['ID'].replace('', pd.NA)

    df_merge = pd.merge(df_a_valido, df_b, on='ID', how='outer', indicator=True)
    df_match = df_merge[df_merge['_merge'] == 'both'].copy()
    
    def determinar_ou(row):
        if son_mismos_establecimientos(row['Establecimiento_norm'], row['Centro_Costo_norm']):
            return row['Org Unit Path [Required]']
        else:
            rbd_n = str(row.get('RBD_norm_y', row.get('RBD_norm', ''))).strip()
            
            comuna = ""
            if rbd_n in DICCIONARIO_ESTABLECIMIENTOS_DEFAULT:
                comuna = DICCIONARIO_ESTABLECIMIENTOS_DEFAULT[rbd_n]["comuna"]
            else:
                val_com = row.get('Comuna', row.get('Comuna_y', ''))
                comuna = "" if pd.isna(val_com) else str(val_com).strip()
            
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

    df_match_cambiados = df_match[df_match['Nuevo Establecimiento'] != ""].copy() if not df_match.empty else pd.DataFrame()

    df_solo_a = df_merge[df_merge['_merge'] == 'left_only'].copy()
    df_solo_b = df_merge[df_merge['_merge'] == 'right_only'].copy()

    excel_coincidencias = estructurar_salida_excel(df_match, 'both')
    excel_solo_a_eliminar = estructurar_salida_excel(df_solo_a, 'A')
    excel_solo_b_nuevos = estructurar_salida_excel(df_solo_b, 'B')

    csv_match = formatear_csv_workspace(
        df_match_cambiados,
        mapping_cols={
            'First Name [Required]': 'First Name [Required]',
            'Last Name [Required]': 'Last Name [Required]',
            'Email Address [Required]': 'Email Address [Required]',
            'Org Unit Path [Required]': 'Org Unit Path [Required]',
            'Employee ID': 'RUN_norm'
        },
        valores_fijos={
            'Password [Required]': '****'
        }
    )

    # Agregada la contraseña '****' para las cuentas a eliminar / archivar
    csv_solo_a_eliminar = formatear_csv_workspace(
        df_solo_a,
        mapping_cols={
            'First Name [Required]': 'First Name [Required]',
            'Last Name [Required]': 'Last Name [Required]',
            'Email Address [Required]': 'Email Address [Required]',
            'Employee ID': 'Employee ID'
        },
        valores_fijos={
            'Password [Required]': '****',
            'Org Unit Path [Required]': '/Archivados Funcionarios',
            'New Licenses [UPLOAD ONLY]': '1010070004',
            'New Status [UPLOAD ONLY]': 'Archived'
        }
    )

    os.makedirs(directorio_salida, exist_ok=True)
    
    excel_coincidencias.to_excel(os.path.join(directorio_salida, 'coincidencias.xlsx'), index=False)
    excel_solo_a_eliminar.to_excel(os.path.join(directorio_salida, 'solo_a_eliminar.xlsx'), index=False)
    excel_solo_b_nuevos.to_excel(os.path.join(directorio_salida, 'solo_b_nuevos.xlsx'), index=False)

    csv_match.to_csv(os.path.join(directorio_salida, 'match.csv'), index=False, encoding='utf-8')
    csv_solo_a_eliminar.to_csv(os.path.join(directorio_salida, 'solo_a_eliminar.csv'), index=False, encoding='utf-8')

    if not df_sin_emp_id.empty:
        excel_sin_emp_id = estructurar_salida_excel(df_sin_emp_id, 'A')
        csv_sin_emp_id = formatear_csv_workspace(
            df_sin_emp_id,
            mapping_cols={
                'First Name [Required]': 'First Name [Required]',
                'Last Name [Required]': 'Last Name [Required]',
                'Email Address [Required]': 'Email Address [Required]',
                'Employee ID': 'Employee ID'
            },
            valores_fijos={
                'Password [Required]': '****',
                'Org Unit Path [Required]': '/Archivados Funcionarios',
                'New Licenses [UPLOAD ONLY]': '1010070004',
                'New Status [UPLOAD ONLY]': 'Archived'
            }
        )
        excel_sin_emp_id.to_excel(os.path.join(directorio_salida, 'sin_employee_id.xlsx'), index=False)
        csv_sin_emp_id.to_csv(os.path.join(directorio_salida, 'sin_employee_id.csv'), index=False, encoding='utf-8')

    dir_separados = os.path.join(directorio_salida, 'separados')
    dir_match_sep = os.path.join(dir_separados, 'match')
    dir_eliminar_sep = os.path.join(dir_separados, 'eliminar')

    os.makedirs(dir_match_sep, exist_ok=True)
    os.makedirs(dir_eliminar_sep, exist_ok=True)

    count_match_files = 0
    if not df_match_cambiados.empty:
        df_match_cambiados['Establecimiento_Grupo'] = df_match_cambiados['Centro Costo'].fillna('').astype(str)
        df_match_cambiados['Establecimiento_Grupo'] = df_match_cambiados['Establecimiento_Grupo'].replace('', pd.NA).fillna(df_match_cambiados['Establecimiento'])

        for est_nombre, grupo in df_match_cambiados.groupby('Establecimiento_Grupo'):
            csv_sub_match = formatear_csv_workspace(
                grupo,
                mapping_cols={
                    'First Name [Required]': 'First Name [Required]',
                    'Last Name [Required]': 'Last Name [Required]',
                    'Email Address [Required]': 'Email Address [Required]',
                    'Org Unit Path [Required]': 'Org Unit Path [Required]',
                    'Employee ID': 'RUN_norm'
                },
                valores_fijos={
                    'Password [Required]': '****'
                }
            )
            nombre_file = f"{sanitizar_nombre_archivo(est_nombre)}.csv"
            csv_sub_match.to_csv(os.path.join(dir_match_sep, nombre_file), index=False, encoding='utf-8')
            count_match_files += 1

    count_eliminar_files = 0
    if not df_solo_a.empty:
        for est_nombre, grupo in df_solo_a.groupby('Establecimiento'):
            # Agregada la contraseña '****' en los subarchivos de eliminar
            csv_sub_eliminar = formatear_csv_workspace(
                grupo,
                mapping_cols={
                    'First Name [Required]': 'First Name [Required]',
                    'Last Name [Required]': 'Last Name [Required]',
                    'Email Address [Required]': 'Email Address [Required]',
                    'Employee ID': 'Employee ID'
                },
                valores_fijos={
                    'Password [Required]': '****',
                    'Org Unit Path [Required]': '/Archivados Funcionarios',
                    'New Licenses [UPLOAD ONLY]': '1010070004',
                    'New Status [UPLOAD ONLY]': 'Archived'
                }
            )
            nombre_file = f"{sanitizar_nombre_archivo(est_nombre)}.csv"
            csv_sub_eliminar.to_csv(os.path.join(dir_eliminar_sep, nombre_file), index=False, encoding='utf-8')
            count_eliminar_files += 1

    # Resumen
    total_coincidencias = len(df_match)
    cuentas_a_actualizar = len(df_match_cambiados)
    cuentas_sin_cambio = total_coincidencias - cuentas_a_actualizar

    print("\n--- RESUMEN DEL PROCESO ---")
    print(f"🔗 Coincidencias totales (Match A-B): {total_coincidencias}")
    print(f"  └─ ⚙️  Cuentas CON cambio de colegio (incluidas en match.csv): {cuentas_a_actualizar}")
    print(f"  └─ 🟢 Cuentas SIN cambios (omitidas de match.csv): {cuentas_sin_cambio}")
    print(f"➕ Funcionarios a agregar (Solo B): {len(df_solo_b)}")
    print(f"➖ Funcionarios a eliminar/archivar (Solo A): {len(df_solo_a)}")
    if not df_sin_emp_id.empty:
        print(f"⚠️  Cuentas sin Employee ID (Archivo A): {len(df_sin_emp_id)}")

if __name__ == "__main__":
    procesar_cuentas(
        nombre_archivo_a="archivos/uso_workspace2.xlsx", 
        nombre_archivo_b="archivos/dotacion_actualizada.xlsx",
        directorio_base="" 
    )