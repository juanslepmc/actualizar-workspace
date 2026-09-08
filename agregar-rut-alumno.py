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

# Cursos clasificados como Egresados
CURSOS_EGRESADOS = [
    "4° MEDIO", 
    "3ER NIVEL (4° MEDIO)", 
    "2DO NIVEL (3° Y 4° MEDIO)"
]

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

def normalizar_rut(rut):
    if pd.isna(rut):
        return ""
    rut_clean = str(rut).upper().replace('.', '').replace(' ', '').strip()
    if not rut_clean:
        return ""
    if '-' not in rut_clean and len(rut_clean) > 1:
        rut_clean = f"{rut_clean[:-1]}-{rut_clean[-1]}"
    return rut_clean

def normalizar_rbd(rbd):
    if pd.isna(rbd):
        return ""
    rbd_str = str(rbd).replace('.', '').strip()
    return rbd_str.split('-')[0]

def sanitizar_nombre_archivo(nombre):
    if pd.isna(nombre) or str(nombre).strip() == "":
        return "Sin_Establecimiento"
    nombre_clean = re.sub(r'[\\/*?:"<>|]', "", str(nombre))
    nombre_clean = re.sub(r'\s+', ' ', nombre_clean).strip()
    return nombre_clean if nombre_clean else "Sin_Establecimiento"

def extraer_info_workspace_path(path):
    if pd.isna(path) or not str(path).strip():
        return "", "", ""
    
    parts = [p.strip() for p in str(path).split('/') if p.strip()]
    curso = parts[-1] if len(parts) > 0 else ""
    
    rbd = ""
    establecimiento = ""
    for part in parts:
        match = re.match(r'^(\d+)\s*(.*)$', part)
        if match:
            rbd = match.group(1)
            establecimiento = match.group(2)
            break
            
    return rbd, establecimiento, curso

def construir_path_destino(rbd, curso, dicc_establecimientos):
    rbd_norm = normalizar_rbd(rbd)
    info = dicc_establecimientos.get(rbd_norm, {})
    comuna = info.get('comuna', 'Constitucion')
    nombre_est = info.get('nombre', f'ESTABLECIMIENTO_{rbd_norm}')
    
    return f"/Comunas/{comuna}/{rbd_norm} {nombre_est}/Estudiantes/{curso}"

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

def estructurar_salida_excel_estudiantes(df, origen):
    out = pd.DataFrame()
    if df.empty:
        return out

    if origen == 'both':
        out['First Name [Required]'] = df.get('First Name [Required]', '')
        out['Last Name [Required]'] = df.get('Last Name [Required]', '')
        out['Email Address [Required]'] = df.get('Email Address [Required]', '')
        out['RUT (SIGE)'] = df.get('RUT_norm', '')
        out['RBD Workspace'] = df.get('RBD_WS', '')
        out['Curso Workspace'] = df.get('Curso_WS', '')
        out['Org Unit Path Actual'] = df.get('Org Unit Path [Required]', '') # Retiene el valor original de Archivo A
        out['RBD SIGE'] = df.get('RBD_SIGE', '')
        out['Curso SIGE'] = df.get('Curso_SIGE', '')
        out['Estado'] = df.get('Estado', '')
        out['Org Unit Path Nuevo'] = df.get('Nuevo_Path', '')
        out['Establecimiento SIGE'] = df.get('Establecimiento_SIGE', '')
        out['ID_A'] = df.get('ID_A', '')
        out['ID_B'] = df.get('ID_B', '')

    elif origen == 'A':
        out['First Name [Required]'] = df.get('First Name [Required]', '')
        out['Last Name [Required]'] = df.get('Last Name [Required]', '')
        out['Email Address [Required]'] = df.get('Email Address [Required]', '')
        out['Employee ID (Workspace)'] = df.get('Employee ID', '')
        out['RBD Workspace'] = df.get('RBD_WS', '')
        out['Curso Workspace'] = df.get('Curso_WS', '')
        out['Org Unit Path Actual'] = df.get('Org Unit Path [Required]', '')
        out['Org Unit Path Nuevo'] = "/Archivados Estudiantes"
        out['Estado'] = "Alumno a eliminar"
        out['Establecimiento Workspace'] = df.get('Establecimiento_WS', '')
        out['ID_A'] = df.get('ID_A', '')
        out['ID_B'] = ""

    elif origen == 'B':
        out['First Name [Required]'] = df.get('Nombres', '')
        ap_pat = df.get('Apellido Paterno', pd.Series()).fillna('')
        ap_mat = df.get('Apellido Materno', pd.Series()).fillna('')
        out['Last Name [Required]'] = (ap_pat.astype(str) + " " + ap_mat.astype(str)).str.strip()
        out['Email Address [Required]'] = ""
        out['RUT (SIGE)'] = df.get('RUT_norm', '')
        out['RBD SIGE'] = df.get('RBD_SIGE', '')
        out['Curso SIGE'] = df.get('Curso_SIGE', '')
        out['Estado'] = "Alumno nuevo"
        out['Org Unit Path Nuevo'] = df.get('Nuevo_Path', '')
        out['Establecimiento SIGE'] = df.get('Establecimiento_SIGE', '')
        out['ID_A'] = ""
        out['ID_B'] = df.get('ID_B', '')

    if 'Last Name [Required]' in out.columns and not out.empty:
        out['Last Name [Required]'] = out['Last Name [Required]'].astype(str).str.strip()

    return out

def solicitar_confirmacion_egresados():
    while True:
        respuesta = input("¿Desea considerar proceso de egresados? (si/no): ").strip().lower()
        respuesta_norm = ''.join(c for c in unicodedata.normalize('NFD', respuesta) if unicodedata.category(c) != 'Mn')
        
        if respuesta_norm in ['si', 's']:
            return True
        elif respuesta_norm in ['no', 'n']:
            return False
        else:
            print("⚠️ Opción no válida. Por favor responda únicamente con 'si' o 'no'.\n")

def procesar_estudiantes(nombre_archivo_a, nombre_archivo_b, directorio_base="", directorio_salida="resultado estudiantes", dicc_establecimientos=None, procesar_egresados=True):
    if dicc_establecimientos is None:
        dicc_establecimientos = DICCIONARIO_ESTABLECIMIENTOS_DEFAULT

    ruta_a = os.path.join(directorio_base, nombre_archivo_a) if directorio_base else nombre_archivo_a
    ruta_b = os.path.join(directorio_base, nombre_archivo_b) if directorio_base else nombre_archivo_b
    
    def cargar_archivo(ruta):
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No se encontró el archivo en la ruta: {ruta}")
        
        if ruta.endswith('.xlsx') or ruta.endswith('.xls'):
            df = pd.read_excel(ruta, dtype=str)
        else:
            df = pd.read_csv(ruta, dtype=str)
            
        df.columns = df.columns.str.strip()
        return df

    df_a = cargar_archivo(ruta_a)
    df_b = cargar_archivo(ruta_b)

    # 1. NORMALIZAR Y CREAR ID ARTIFICIAL EN ARCHIVO A (Workspace)
    df_a['First_Name_norm'] = df_a['First Name [Required]'].apply(normalizar_texto)
    df_a['Last_Name_norm'] = df_a['Last Name [Required]'].apply(normalizar_texto)
    
    info_extracted = df_a['Org Unit Path [Required]'].apply(extraer_info_workspace_path)
    df_a['RBD_WS'] = info_extracted.apply(lambda x: normalizar_rbd(x[0]))
    df_a['Establecimiento_WS'] = info_extracted.apply(lambda x: x[1])
    df_a['Curso_WS'] = info_extracted.apply(lambda x: x[2])

    df_a = df_a[df_a['RBD_WS'] != '3535'].copy()
    df_a['ID_A'] = (df_a['First_Name_norm'] + df_a['Last_Name_norm'] + df_a['RBD_WS']).str.replace(" ", "")
    df_a['ID'] = df_a['ID_A']

    # 2. NORMALIZAR Y CREAR ID ARTIFICIAL EN ARCHIVO B (SIGE)
    df_b['RBD_SIGE'] = df_b['RBD'].apply(normalizar_rbd)
    df_b = df_b[df_b['RBD_SIGE'] != '3535'].copy()

    run_col = df_b['Run'].fillna('').astype(str).str.strip()
    dv_col = df_b['Dígito Ver.'].fillna('').astype(str).str.strip()
    df_b['RUT_norm'] = (run_col + "-" + dv_col).apply(normalizar_rut)

    df_b['Nombres_norm'] = df_b['Nombres'].apply(normalizar_texto)
    df_b['Ap_Paterno_norm'] = df_b['Apellido Paterno'].apply(normalizar_texto)
    df_b['Ap_Materno_norm'] = df_b['Apellido Materno'].apply(normalizar_texto)
    df_b['ID_B'] = (df_b['Nombres_norm'] + df_b['Ap_Paterno_norm'] + df_b['Ap_Materno_norm'] + df_b['RBD_SIGE']).str.replace(" ", "")
    df_b['ID'] = df_b['ID_B']

    desc_grado = df_b['Desc Grado'].fillna('').astype(str).str.strip()
    letra_curso = df_b['Letra Curso'].fillna('').astype(str).str.strip()
    df_b['Curso_SIGE'] = (desc_grado + " " + letra_curso).str.strip()

    rbds_permitidos = set(dicc_establecimientos.keys())
    df_b_validos = df_b[df_b['RBD_SIGE'].isin(rbds_permitidos)].copy()
    df_b_omitidos = df_b[~df_b['RBD_SIGE'].isin(rbds_permitidos)].copy()

    df_b_validos['Establecimiento_SIGE'] = df_b_validos['RBD_SIGE'].apply(
        lambda rbd: dicc_establecimientos.get(rbd, {}).get('nombre', f"ESTABLECIMIENTO_{rbd}")
    )

    # 3. CRUCE DE DATOS POR ID ARTIFICIAL
    df_merge = pd.merge(df_a, df_b_validos, on='ID', how='outer', indicator=True)
    df_match = df_merge[df_merge['_merge'] == 'both'].copy()

    def evaluar_match_estudiante(row):
        rbd_ws = row['RBD_WS']
        rbd_sige = row['RBD_SIGE']
        curso_ws = normalizar_texto(row['Curso_WS'])
        curso_sige = normalizar_texto(row['Curso_SIGE'])
        curso_sige_raw = row['Curso_SIGE']

        if procesar_egresados and (curso_sige in CURSOS_EGRESADOS):
            return "Egresado", "/Archivados Estudiantes/Egresados"

        if rbd_sige != rbd_ws:
            nuevo_path = construir_path_destino(rbd_sige, curso_sige_raw, dicc_establecimientos)
            return "Cambio de establecimiento", nuevo_path

        if curso_sige != curso_ws:
            nuevo_path = construir_path_destino(rbd_sige, curso_sige_raw, dicc_establecimientos)
            return "Cambio de curso", nuevo_path

        return "Sin cambios", row['Org Unit Path [Required]']

    if not df_match.empty:
        eval_res = df_match.apply(evaluar_match_estudiante, axis=1)
        df_match['Estado'] = [r[0] for r in eval_res]
        df_match['Nuevo_Path'] = [r[1] for r in eval_res]
        # Mantiene intacto df_match['Org Unit Path [Required]'] con el valor proveniente de Archivo A

    df_solo_a = df_merge[df_merge['_merge'] == 'left_only'].copy()
    df_solo_b = df_merge[df_merge['_merge'] == 'right_only'].copy()

    if not df_solo_b.empty:
        df_solo_b['Nuevo_Path'] = df_solo_b.apply(
            lambda r: construir_path_destino(r['RBD_SIGE'], r['Curso_SIGE'], dicc_establecimientos), axis=1
        )

    # 4. EXPORTACIÓN Y SALIDAS
    excel_coincidencias = estructurar_salida_excel_estudiantes(df_match, 'both')
    excel_solo_a_eliminar = estructurar_salida_excel_estudiantes(df_solo_a, 'A')
    excel_solo_b_nuevos = estructurar_salida_excel_estudiantes(df_solo_b, 'B')

    csv_match = formatear_csv_workspace(
        df_match,
        mapping_cols={
            'First Name [Required]': 'First Name [Required]',
            'Last Name [Required]': 'Last Name [Required]',
            'Email Address [Required]': 'Email Address [Required]',
            'Org Unit Path [Required]': 'Nuevo_Path',
            'Employee ID': 'RUT_norm'
        },
        valores_fijos={'Password [Required]': '****'}
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
            'Org Unit Path [Required]': '/Archivados Estudiantes',
            'New Licenses [UPLOAD ONLY]': '1010070004',
            'New Status [UPLOAD ONLY]': 'Archived'
        }
    )

    os.makedirs(directorio_salida, exist_ok=True)
    excel_coincidencias.to_excel(os.path.join(directorio_salida, 'coincidencias.xlsx'), index=False)
    excel_solo_a_eliminar.to_excel(os.path.join(directorio_salida, 'solo_a_eliminar.xlsx'), index=False)
    excel_solo_b_nuevos.to_excel(os.path.join(directorio_salida, 'solo_b_nuevos.xlsx'), index=False)

    if not df_b_omitidos.empty:
        df_b_omitidos.to_excel(os.path.join(directorio_salida, 'sige_omitidos_sin_cobertura.xlsx'), index=False)

    csv_match.to_csv(os.path.join(directorio_salida, 'match.csv'), index=False, encoding='utf-8')
    csv_solo_a_eliminar.to_csv(os.path.join(directorio_salida, 'solo_a_eliminar.csv'), index=False, encoding='utf-8')

    dir_separados = os.path.join(directorio_salida, 'separados')
    dir_match_sep = os.path.join(dir_separados, 'match')
    dir_eliminar_sep = os.path.join(dir_separados, 'eliminar')

    os.makedirs(dir_match_sep, exist_ok=True)
    os.makedirs(dir_eliminar_sep, exist_ok=True)

    count_match_files = 0
    if not df_match.empty:
        df_match['Grupo_Establecimiento'] = df_match['Establecimiento_SIGE'].fillna('').astype(str)
        df_match['Grupo_Establecimiento'] = df_match['Grupo_Establecimiento'].replace('', pd.NA).fillna(df_match['Establecimiento_WS'])

        for est_nombre, grupo in df_match.groupby('Grupo_Establecimiento'):
            csv_sub_match = formatear_csv_workspace(
                grupo,
                mapping_cols={
                    'First Name [Required]': 'First Name [Required]',
                    'Last Name [Required]': 'Last Name [Required]',
                    'Email Address [Required]': 'Email Address [Required]',
                    'Org Unit Path [Required]': 'Nuevo_Path',
                    'Employee ID': 'RUT_norm'
                },
                valores_fijos={'Password [Required]': '****'}
            )
            nombre_file = f"{sanitizar_nombre_archivo(est_nombre)}.csv"
            csv_sub_match.to_csv(os.path.join(dir_match_sep, nombre_file), index=False, encoding='utf-8')
            count_match_files += 1

    count_eliminar_files = 0
    if not df_solo_a.empty:
        for est_nombre, grupo in df_solo_a.groupby('Establecimiento_WS'):
            csv_sub_eliminar = formatear_csv_workspace(
                grupo,
                mapping_cols={
                    'First Name [Required]': 'First Name [Required]',
                    'Last Name [Required]': 'Last Name [Required]',
                    'Email Address [Required]': 'Email Address [Required]',
                    'Employee ID': 'Employee ID'
                },
                valores_fijos={
                    'Org Unit Path [Required]': '/Archivados Estudiantes',
                    'New Licenses [UPLOAD ONLY]': '1010070004',
                    'New Status [UPLOAD ONLY]': 'Archived'
                }
            )
            nombre_file = f"{sanitizar_nombre_archivo(est_nombre)}.csv"
            csv_sub_eliminar.to_csv(os.path.join(dir_eliminar_sep, nombre_file), index=False, encoding='utf-8')
            count_eliminar_files += 1

    num_cambio_est = len(df_match[df_match['Estado'] == 'Cambio de establecimiento']) if not df_match.empty else 0
    num_cambio_curso = len(df_match[df_match['Estado'] == 'Cambio de curso']) if not df_match.empty else 0
    num_egresados = len(df_match[df_match['Estado'] == 'Egresado']) if not df_match.empty else 0
    num_sin_cambios = len(df_match[df_match['Estado'] == 'Sin cambios']) if not df_match.empty else 0

    print("\n--- RESUMEN DEL PROCESO DE ESTUDIANTES ---")
    print(f"⚙️ Proceso de egresados: {'ACTIVADO' if procesar_egresados else 'DESACTIVADO'}")
    print(f"✅ Coincidencias procesadas en total: {len(df_match)}")
    print(f"   • Sin cambios: {num_sin_cambios}")
    print(f"   • Cambios de curso: {num_cambio_curso}")
    print(f"   • Cambios de establecimiento: {num_cambio_est}")
    print(f"   • Egresados movidos: {num_egresados}")
    print(f"➕ Alumnos nuevos a agregar (Solo B/SIGE): {len(df_solo_b)}")
    print(f"➖ Alumnos a archivar/eliminar (Solo A/Workspace): {len(df_solo_a)}")
    print(f"⚠️ Alumnos SIGE omitidos (fuera de la cobertura de 68 RBDs): {len(df_b_omitidos)}")

if __name__ == "__main__":
    aplica_egresados = solicitar_confirmacion_egresados()
    
    procesar_estudiantes(
        nombre_archivo_a="archivos alumno/uso_workspace.xlsx", 
        nombre_archivo_b="archivos alumno/Consolidado_sin_duplicados.xlsx",
        directorio_base="",
        directorio_salida="resultado estudiantes",
        procesar_egresados=aplica_egresados
    )