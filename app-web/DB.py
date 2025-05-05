def backup_to_sql():
    """Genera un backup de la base de datos en formato SQL."""
    # Verificar autenticación y permisos primero
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if session.get('Super_Admin') != 1:
        return render_template("gestionar_data.html", error="No tiene permisos para realizar esta acción.")
    
    try:
        # Crear directorio de backups si no existe
        backup_dir = os.path.join(app.root_path, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_db_{timestamp}.sql'
        file_path = os.path.join(backup_dir, filename)
        
        # Asegurar que las rutas usen el formato correcto para Windows
        file_path = os.path.normpath(file_path)

        # Configurar los parámetros de conexión
        db_config = {
            'host': app.config['MYSQL_HOST'],
            'user': app.config['MYSQL_USER'],
            'password': app.config['MYSQL_PASSWORD'],
            'database': app.config['MYSQL_DB']
        }
        
        # Crear un archivo de log para debugging
        log_path = os.path.join(backup_dir, f"mysqldump_log_{timestamp}.txt")
        
        # Crear el log_path independientemente del éxito/fracaso
        log_path = os.path.join(backup_dir, f"mysqldump_log_{timestamp}.txt")
        
        # Iniciar el log con información básica del sistema
        with open(log_path, 'w') as log_file:
            log_file.write(f"Log de búsqueda de mysqldump - {datetime.now()}\n")
            log_file.write(f"Sistema operativo: {os.name}\n")
            log_file.write(f"Directorio de trabajo actual: {os.getcwd()}\n")
            log_file.write(f"Directorio de backup: {backup_dir}\n\n")
            log_file.write(f"Configuración de base de datos:\n")
            log_file.write(f"- Host: {app.config['MYSQL_HOST']}\n")
            log_file.write(f"- DB: {app.config['MYSQL_DB']}\n\n")
            
        # Buscar mysqldump en ubicaciones comunes en Windows
        mysqldump_cmd = 'mysqldump'
        mysqldump_found = False
        paths_checked = []
        
        if os.name == 'nt':  # Windows
            # Lista extendida de posibles ubicaciones de mysqldump.exe en Windows
            possible_paths = [
                # XAMPP installations - Priorizar primero las rutas XAMPP
                r'C:\xampp\mysql\bin\mysqldump.exe',
                r'C:\xampp\bin\mysql\bin\mysqldump.exe',  # Estructura alternativa
                r'C:\xampp\mysql\bin\mariadb\mysqldump.exe',  # Posible estructura anidada
                r'C:\xampp7\mysql\bin\mysqldump.exe',
                r'C:\xampp8\mysql\bin\mysqldump.exe',
                r'C:\xampp\MariaDB\bin\mysqldump.exe',
                r'C:\xampp\mysql-8.0\bin\mysqldump.exe',
                r'C:\xampp\mysql-5.7\bin\mysqldump.exe',
                
                # Buscar en ruta del código - puede ser una instalación local
                os.path.join(app.root_path, '..', 'mysql', 'bin', 'mysqldump.exe'),
                os.path.join(app.root_path, '..', 'xampp', 'mysql', 'bin', 'mysqldump.exe'),
                
                # Common XAMPP alternative paths en otras unidades
                r'D:\xampp\mysql\bin\mysqldump.exe',
                r'E:\xampp\mysql\bin\mysqldump.exe',
                r'F:\xampp\mysql\bin\mysqldump.exe',  # Unidades adicionales
                
                # Paths with MariaDB (often included with XAMPP instead of MySQL)
                r'C:\xampp\mariadb\bin\mysqldump.exe',
                r'C:\xampp\mariadb-10.4\bin\mysqldump.exe',
                r'C:\xampp\mariadb-10.5\bin\mysqldump.exe',
                r'C:\xampp\mariadb-10.6\bin\mysqldump.exe',  # Versión más reciente
                
                # MySQL standard installations
                r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe',
                r'C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqldump.exe',
                r'C:\Program Files\MySQL\MySQL Server 5.6\bin\mysqldump.exe',
                r'C:\Program Files\MySQL\MySQL Server 8.1\bin\mysqldump.exe',
                r'C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysqldump.exe',
                r'C:\Program Files (x86)\MySQL\MySQL Server 5.7\bin\mysqldump.exe',
                
                # WAMP installations
                r'C:\wamp\bin\mysql\mysql5.7.36\bin\mysqldump.exe',
                r'C:\wamp64\bin\mysql\mysql5.7.36\bin\mysqldump.exe',
                r'C:\wamp\bin\mysql\mysql8.0\bin\mysqldump.exe',
                r'C:\wamp64\bin\mysql\mysql8.0\bin\mysqldump.exe',
                
                # Laragon installations
                r'C:\laragon\bin\mysql\mysql-5.7.33-winx64\bin\mysqldump.exe',
                r'C:\laragon\bin\mysql\mysql-8.0-winx64\bin\mysqldump.exe',
                
                # MAMP installations
                r'C:\MAMP\bin\mysql\bin\mysqldump.exe'
            ]
            
            # Agregar rutas desde variables de entorno
            if 'PATH' in os.environ:
                path_dirs = os.environ['PATH'].split(os.pathsep)
                for dir_path in path_dirs:
                    mysql_bin_dir = os.path.join(dir_path, 'bin')
                    if 'mysql' in dir_path.lower() or 'xampp' in dir_path.lower():
                        mysqldump_path = os.path.join(dir_path, 'mysqldump.exe')
                        if mysqldump_path not in possible_paths:
                            possible_paths.append(mysqldump_path)
                        
                        mysqldump_bin_path = os.path.join(dir_path, 'bin', 'mysqldump.exe')
                        if mysqldump_bin_path not in possible_paths:
                            possible_paths.append(mysqldump_bin_path)
            
            # Buscar en versiones de MySQL en Program Files
            for base_dir in [r'C:\Program Files\MySQL', r'C:\Program Files (x86)\MySQL']:
                if os.path.exists(base_dir):
                    try:
                        for folder in os.listdir(base_dir):
                            if folder.startswith('MySQL Server'):
                                path = os.path.join(base_dir, folder, 'bin', 'mysqldump.exe')
                                if path not in possible_paths:
                                    possible_paths.append(path)
                    except Exception as e:
                        # Simplemente continuar si hay error al listar directorios
                        continue
            
            # Buscar en instalaciones XAMPP en diferentes unidades y configuraciones
            xampp_possible_bases = [r'C:\xampp', r'D:\xampp', r'E:\xampp']
            
            for xampp_base in xampp_possible_bases:
                if os.path.exists(xampp_base):
                    try:
                        # Buscar directamente en las rutas más comunes primero
                        direct_paths = [
                            os.path.join(xampp_base, 'mysql', 'bin', 'mysqldump.exe'),
                            os.path.join(xampp_base, 'mariadb', 'bin', 'mysqldump.exe')
                        ]
                        
                        for path in direct_paths:
                            if os.path.exists(path) and path not in possible_paths:
                                possible_paths.append(path)
                                with open(log_path, 'a') as log_file:
                                    log_file.write(f"Encontrado posible mysqldump en XAMPP: {path}\n")
                        
                        # Buscar en subdirectorios que puedan contener instalaciones MySQL/MariaDB
                        for folder in os.listdir(xampp_base):
                            # Buscar en patrones como mysql, mysql-5.7, mariadb, etc.
                            if folder.startswith('mysql') or folder.startswith('mariadb'):
                                bin_path = os.path.join(xampp_base, folder, 'bin', 'mysqldump.exe')
                                if os.path.exists(bin_path) and bin_path not in possible_paths:
                                    possible_paths.append(bin_path)
                                    with open(log_path, 'a') as log_file:
                                        log_file.write(f"Encontrado mysqldump en subdirectorio XAMPP: {bin_path}\n")
                            
                            # También buscar en patrones como /bin/mysql/mysql5.7/bin/
                            if folder == 'bin':
                                mysql_path = os.path.join(xampp_base, folder, 'mysql')
                                if os.path.exists(mysql_path):
                                    for mysql_ver in os.listdir(mysql_path):
                                        bin_path = os.path.join(mysql_path, mysql_ver, 'bin', 'mysqldump.exe')
                                        if os.path.exists(bin_path) and bin_path not in possible_paths:
                                            possible_paths.append(bin_path)
                                            with open(log_path, 'a') as log_file:
                                                log_file.write(f"Encontrado mysqldump en bin/mysql XAMPP: {bin_path}\n")
                    except Exception as e:
                        with open(log_path, 'a') as log_file:
                            log_file.write(f"Error al buscar en XAMPP {xampp_base}: {str(e)}\n")
            
            # Registrar rutas verificadas para debugging
            with open(log_path, 'a') as log_file:
                log_file.write(f"Buscando mysqldump.exe en las siguientes rutas:\n")
                
                # Comprobar si mysqldump existe en alguna de las rutas
                for path in possible_paths:
                    paths_checked.append(path)
                    try:
                        log_file.write(f"Verificando: {path}\n")
                        if os.path.isfile(path):
                            # Verificar si el archivo es realmente un ejecutable
                            try:
                                with open(path, 'rb') as f:
                                    header = f.read(2)
                                    # Verificar el encabezado MZ de los ejecutables Windows
                                    if header == b'MZ':
                                        mysqldump_cmd = path
                                        mysqldump_found = True
                                        log_file.write(f"¡ENCONTRADO!: {path} (Verificado como ejecutable válido)\n")
                                        break
                                    else:
                                        log_file.write(f"Archivo encontrado pero no parece ser un ejecutable válido: {path}\n")
                            except Exception as file_error:
                                log_file.write(f"Error al verificar el archivo: {path}: {str(file_error)}\n")
                                # Aun así, intentarlo si es el único que encontramos
                                if not mysqldump_found:
                                    mysqldump_cmd = path
                        else:
                            log_file.write(f"No encontrado: {path}\n")
                    except Exception as path_error:
                        log_file.write(f"Error al verificar la ruta {path}: {str(path_error)}\n")
                
                # Si no se encontró en las rutas específicas, intentar con PATH
                if not mysqldump_found:
                    log_file.write("No se encontró mysqldump en rutas específicas, intentando con where/which...\n")
                    try:
                        # Intentar encontrar mysqldump en el PATH
                        where_cmd = "where mysqldump" if os.name == 'nt' else "which mysqldump"
                        result = subprocess.run(where_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        if result.returncode == 0 and result.stdout.strip():
                            mysqldump_cmd = result.stdout.strip().split('\n')[0]
                            mysqldump_found = True
                            log_file.write(f"Encontrado vía where/which: {mysqldump_cmd}\n")
                        else:
                            log_file.write(f"No se encontró mysqldump en PATH\n")
                    except Exception as e:
                        log_file.write(f"Error al buscar mysqldump en PATH: {str(e)}\n")
                
                # Intentar encontrar mysql.exe en lugar de mysqldump.exe como alternativa
                if not mysqldump_found:
                    log_file.write("Buscando mysql.exe como alternativa...\n")
                    mysql_paths = [path.replace('mysqldump.exe', 'mysql.exe') for path in possible_paths]
                    
                    for path in mysql_paths:
                        try:
                            log_file.write(f"Verificando mysql.exe en: {path}\n")
                            if os.path.isfile(path):
                                try:
                                    with open(path, 'rb') as f:
                                        header = f.read(2)
                                        if header == b'MZ':
                                            mysql_cmd = path
                                            log_file.write(f"¡ENCONTRADO mysql.exe!: {path}\n")
                                            
                                            # Intentar usar mysql para el backup
                                            try:
                                                # Escapar caracteres especiales en la contraseña para evitar problemas de codificación
                                                password_escaped = db_config["password"].replace('"', '\\"').replace('$', '\\$')
                                                
                                                # Comando para exportar usando mysql con configuración de codificación
                                                # Usar 'cp1252' (Windows Latin-1) para Windows
                                                charset = 'cp1252' if os.name == 'nt' else 'utf8mb4'
                                                encoding_param = 'latin1' if os.name == 'nt' else 'utf-8'
                                                log_file.write(f"Usando conjunto de caracteres: {charset} para el sistema {os.name}\n")
                                                log_file.write(f"Usando codificación de proceso: {encoding_param}\n")
                                                
                                                backup_cmd = f'"{mysql_cmd}" -h {db_config["host"]} ' \
                                                            f'-u {db_config["user"]} ' \
                                                            f'-p{password_escaped} ' \
                                                            f'--default-character-set={charset} ' \
                                                            f'{db_config["database"]} ' \
                                                            f'--execute="SET NAMES {charset}; SET CHARACTER SET {charset}; ' \
                                                            f'SELECT * FROM information_schema.tables ' \
                                                            f'WHERE table_schema = \'{db_config["database"]}\'; ' \
                                                            f'SHOW CREATE TABLE data; SHOW CREATE TABLE delivery; ' \
                                                            f'SHOW CREATE TABLE user_history; SHOW CREATE TABLE tabla;" ' \
                                                            f'> "{file_path}"'
                                                
                                                log_file.write(f"Ejecutando comando mysql.exe con codificación {charset}:\n")
                                                log_file.write(f"Comando: {backup_cmd}\n")
                                                
                                                # Usar entorno de ejecución con variables de entorno controladas
                                                env = os.environ.copy()
                                                if os.name == 'nt':  # Windows
                                                    # Para Windows, establecer variables de entorno para codificación
                                                    env['PYTHONIOENCODING'] = 'latin1'
                                                    env['LANG'] = 'es_ES.1252'
                                                    env['LC_ALL'] = 'es_ES.1252'  # Añadir LC_ALL para mayor control de codificación
                                                else:  # Unix/Linux
                                                    env['PYTHONIOENCODING'] = 'utf-8'
                                                    env['LANG'] = 'es_ES.UTF-8'
                                                    env['LC_ALL'] = 'es_ES.UTF-8'  # Añadir LC_ALL para mayor control de codificación
                                                
                                                # Configurar proceso con manejo explícito de codificación
                                                encoding = 'latin1' if os.name == 'nt' else 'utf-8'
                                                errors_mode = 'surrogateescape' if os.name == 'nt' else 'replace'
                                                log_file.write(f"Usando codificación {encoding} con modo de error {errors_mode} para el proceso\n")
                                                
                                                process = subprocess.Popen(
                                                    backup_cmd,
                                                    shell=True,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    encoding=encoding,
                                                    errors=errors_mode,
                                                    env=env,
                                                    universal_newlines=True  # Asegurar manejo correcto de fin de línea
                                                )
                                                try:
                                                    output, error = process.communicate(timeout=300)
                                                    
                                                    if process.returncode == 0:
                                                        # Verificar si el archivo se creó correctamente
                                                        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                                            backup_success = True
                                                            log_file.write(f"¡Éxito! Backup generado usando mysql.exe. Tamaño: {os.path.getsize(file_path)} bytes\n")
                                                            # Verificar la codificación del archivo generado
                                                            try:
                                                                with open(file_path, 'r', encoding='utf-8') as test_file:
                                                                    # Leer algunas líneas para verificar
                                                                    test_content = test_file.read(1024)
                                                                    log_file.write(f"Verificación de archivo: Lectura correcta con UTF-8\n")
                                                            except UnicodeDecodeError:
                                                                log_file.write(f"Archivo no legible con UTF-8, intentando con codificación alternativa...\n")
                                                                log_file.write(f"Advertencia: El archivo generado no usa codificación UTF-8 pura. Verificando con otras codificaciones...\n")
                                                                # Intentar con otras codificaciones como respaldo
                                                                try:
                                                                    with open(file_path, 'r', encoding='latin1') as test_file:
                                                                        test_content = test_file.read(1024)
                                                                        log_file.write(f"Archivo legible con codificación latin1\n")
                                                                except Exception as enc_error:
                                                                    log_file.write(f"Error al verificar codificación alternativa: {str(enc_error)}\n")
                                                            break
                                                        else:
                                                            log_file.write(f"El comando finalizó exitosamente pero el archivo está vacío o no se creó\n")
                                                    else:
                                                        # Manejo seguro del mensaje de error con codificación
                                                        if isinstance(error, bytes):
                                                            error_str = error.decode('latin1', errors='replace')
                                                        elif isinstance(error, str):
                                                            error_str = error
                                                        else:
                                                            error_str = str(error)
                                                        
                                                        log_file.write(f"Error al ejecutar mysql.exe (código {process.returncode}): {error_str}\n")
                                                except subprocess.TimeoutExpired:
                                                    process.kill()
                                                    output, error = process.communicate()
                                                    log_file.write("Error: Timeout al ejecutar mysql.exe (300 segundos)\n")
                                            except Exception as e:
                                                # Registrar información detallada del error
                                                log_file.write(f"Error al usar mysql.exe para backup: {str(e)}\n")
                                                import traceback
                                                log_file.write(f"Detalles del error:\n{traceback.format_exc()}\n")
                                                
                                                # Intentar diagnosticar problemas comunes
                                                error_msg = str(e)
                                                if "No such file or directory" in error_msg or "sistema no puede encontrar" in error_msg:
                                                    log_file.write("Diagnóstico: Problema de ruta de archivo no encontrada\n")
                                                elif "access" in error_msg.lower() or "permiso" in error_msg.lower() or "denied" in error_msg.lower():
                                                    log_file.write("Diagnóstico: Problema de permisos de acceso\n") 
                                                elif "codec" in error_msg.lower() or "decode" in error_msg.lower() or "encode" in error_msg.lower():
                                                    log_file.write("Diagnóstico: Problema de codificación de caracteres\n")
                                        else:
                                            log_file.write(f"Archivo encontrado pero no es un ejecutable válido: {path}\n")
                                except Exception as file_error:
                                    log_file.write(f"Error al verificar el archivo mysql.exe: {str(file_error)}\n")
                        except Exception as path_error:
                            log_file.write(f"Error al verificar la ruta de mysql.exe {path}: {str(path_error)}\n")
                    
                    # Si no se encuentra en las rutas específicas, buscar en PATH
                    if not backup_success:
                        log_file.write("Buscando mysql.exe en el PATH...\n")
                        try:
                            where_cmd = "where mysql.exe" if os.name == 'nt' else "which mysql"
                            result = subprocess.run(where_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                            if result.returncode == 0 and result.stdout.strip():
                                mysql_cmd = result.stdout.strip().split('\n')[0]
                                log_file.write(f"Encontrado mysql.exe vía where/which: {mysql_cmd}\n")
                                
                                # Intentar usar mysql.exe encontrado en PATH
                                try:
                                    # Escapar caracteres especiales en la contraseña para evitar problemas de codificación
                                    password_escaped = db_config["password"].replace('"', '\\"').replace('$', '\\$').replace('&', '\\&')
                                    
                                    # Usar cp1252 (Windows Latin-1) para Windows para evitar problemas de codificación
                                    charset = 'cp1252' if os.name == 'nt' else 'utf8mb4'
                                    
                                    # Usar el mismo enfoque que funcionó para la versión anterior
                                    charset = 'cp1252' if os.name == 'nt' else 'utf8mb4'
                                    encoding_param = 'latin1' if os.name == 'nt' else 'utf-8'
                                    errors_mode = 'surrogateescape' if os.name == 'nt' else 'replace'
                                    
                                    # Construir el comando con opciones de codificación específicas
                                    backup_cmd = f'"{mysql_cmd}" -h {db_config["host"]} ' \
                                                f'-u {db_config["user"]} ' \
                                                f'-p{password_escaped} ' \
                                                f'--default-character-set={charset} ' \
                                                f'{db_config["database"]} ' \
                                                f'--execute="SET NAMES {charset}; SET CHARACTER SET {charset}; ' \
                                                f'SELECT * FROM information_schema.tables ' \
                                                f'WHERE table_schema = \'{db_config["database"]}\'; ' \
                                                f'SHOW CREATE TABLE data; SHOW CREATE TABLE delivery; ' \
                                                f'SHOW CREATE TABLE user_history; SHOW CREATE TABLE tabla;" ' \
                                                f'> "{file_path}"'

                                    # Configurar proceso con manejo explícito de codificación
                                    # Configurar entorno de ejecución
                                    env = os.environ.copy()
                                    if os.name == 'nt':  # Windows
                                        env['PYTHONIOENCODING'] = 'latin1'
                                        env['LANG'] = 'es_ES.1252'
                                        env['LC_ALL'] = 'es_ES.1252'
                                    else:  # Unix/Linux
                                        env['PYTHONIOENCODING'] = 'utf-8'
                                        env['LANG'] = 'es_ES.UTF-8'
                                        env['LC_ALL'] = 'es_ES.UTF-8'
                                        
                                    # Log para debugging
                                    log_file.write(f"Ejecutando comando mysql.exe con codificación {encoding_param}:\n")
                                    log_file.write(f"Comando: {backup_cmd}\n")
                                    
                                    # Iniciar proceso con configuración de codificación
                                    process = subprocess.Popen(
                                        backup_cmd,
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        encoding=encoding_param,
                                        errors=errors_mode,
                                        env=env,
                                        universal_newlines=True
                                    )

                                    try:
                                        output, error = process.communicate(timeout=300)
                                        if process.returncode == 0:
                                            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                                backup_success = True
                                                log_file.write("¡Éxito! Backup generado usando mysql.exe del PATH\n")
                                            else:
                                                log_file.write("El archivo de backup está vacío o no se creó\n")
                                        else:
                                            # Manejo seguro de errores con codificación adecuada
                                            if isinstance(error, bytes):
                                                error_str = error.decode('latin1' if os.name == 'nt' else 'utf-8', errors='replace')
                                            elif isinstance(error, str):
                                                error_str = error
                                            else:
                                                error_str = str(error)
                                                
                                            # Registrar el error detallado y posibles causas
                                            log_file.write(f"Error al ejecutar mysql.exe (código {process.returncode}): {error_str}\n")
                                            
                                            # Diagnosticar problemas comunes
                                            if "Access denied" in error_str or "acceso denegado" in error_str.lower():
                                                log_file.write("Diagnóstico: Problema de autenticación con la base de datos\n")
                                            elif "Can't connect" in error_str or "No se puede conectar" in error_str:
                                                log_file.write("Diagnóstico: Problema de conexión a la base de datos\n")
                                            elif "Character set" in error_str or "codificación" in error_str.lower():
                                                log_file.write("Diagnóstico: Problema con el conjunto de caracteres\n")
                                    except subprocess.TimeoutExpired:
                                        process.kill()
                                        log_file.write("Error: Timeout al ejecutar mysql.exe\n")
                                    except Exception as e:
                                        log_file.write(f"Error durante la ejecución de mysql.exe: {str(e)}\n")
                                except Exception as e:
                                    log_file.write(f"Error al usar mysql.exe del PATH para backup: {str(e)}\n")
                            else:
                                log_file.write(f"No se encontró mysql.exe en PATH\n")
                        except Exception as e:
                            log_file.write(f"Error al buscar mysql.exe en PATH: {str(e)}\n")
                
        # Crear credenciales para mysqldump (evitar contraseña en línea de comandos)
        my_cnf_path = os.path.join(backup_dir, ".my.cnf")
        with open(my_cnf_path, 'w', encoding='utf-8') as f:
            f.write(f"[client]\nuser={db_config['user']}\npassword={db_config['password']}\nhost={db_config['host']}\ndefault-character-set=utf8mb4")
        
        backup_success = False
        try:
            if os.name == 'nt' and not mysqldump_found:
                # En Windows, si no se encuentra mysqldump, intentar un método alternativo usando comando directo
                # Escapar caracteres problemáticos en la contraseña
                password_escaped = db_config["password"].replace('"', '\\"').replace('$', '\\$').replace('&', '\\&')
                cmd = f'mysql -h {db_config["host"]} -u {db_config["user"]} -p{password_escaped} --default-character-set=utf8mb4 {db_config["database"]} -e "SET NAMES utf8mb4; SELECT * FROM information_schema.tables WHERE table_schema = \'{db_config["database"]}\'" > "{file_path}"'
                
                # Registrar intento alternativo
                with open(log_path, 'a') as log_file:
                    log_file.write("\nIntentando método alternativo con comando mysql directo\n")
                    log_file.write(f"Comando: {cmd}\n")
                    
                # Intentar usar el comando alternativo
                try:
                    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if result.returncode == 0:
                        backup_success = True
                        log_file.write("¡Éxito! Backup generado con el método alternativo.\n")
                    else:
                        log_file.write(f"Error en el método alternativo: {result.stderr}\n")
                except Exception as e:
                    log_file.write(f"Excepción en el método alternativo: {str(e)}\n")
                    
                # Si el método alternativo falló, intentar exportar solo los datos usando Python
                if not backup_success:
                    log_file.write("\nIntentando método de respaldo usando Python para exportar datos...\n")
                    try:
                        # Crear un archivo SQL manualmente con Python
                        with open(file_path, 'w', encoding='utf-8') as sql_file:
                            sql_file.write(f"-- Backup generado por Python el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            sql_file.write(f"-- Base de datos: {db_config['database']}\n\n")
                            
                            # Obtener todas las tablas
                            cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
                            cursor.execute("SHOW TABLES")
                            tables = [table[f'Tables_in_{db_config["database"]}'] for table in cursor.fetchall()]
                            
                            for table in tables:
                                sql_file.write(f"\n-- Estructura y datos para la tabla `{table}`\n")
                                
                                # Obtener la estructura de la tabla
                                try:
                                    cursor.execute(f"SHOW CREATE TABLE `{table}`")
                                    result = cursor.fetchone()
                                    create_key = 'Create Table'
                                    if create_key not in result and 'Create View' in result:
                                        create_key = 'Create View'
                                    create_stmt = result[create_key]
                                    sql_file.write(f"{create_stmt};\n\n")
                                except Exception as table_error:
                                    sql_file.write(f"-- Error al obtener estructura para tabla {table}: {str(table_error)}\n")
                                    log_file.write(f"Error al obtener estructura para tabla {table}: {str(table_error)}\n")
                                
                                # Obtener los datos
                                cursor.execute(f"SELECT * FROM `{table}`")
                                rows = cursor.fetchall()
                                
                                if rows:
                                    for row in rows:
                                        # Construir INSERT statement
                                        columns = ", ".join([f"`{col}`" for col in row.keys()])
                                        values = []
                                        for val in row.values():
                                            if val is None:
                                                values.append("NULL")
                                            elif isinstance(val, str):
                                                # Escapar comillas y caracteres especiales
                                                escaped_val = val.replace("'", "''").replace("\\", "\\\\")
                                                values.append(f"'{escaped_val}'")
                                            elif isinstance(val, (int, float)):
                                                values.append(str(val))
                                            elif isinstance(val, datetime):
                                                values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                                            else:
                                                values.append("NULL")
                                        
                                        values_str = ", ".join(values)
                                        sql_file.write(f"INSERT INTO `{table}` ({columns}) VALUES ({values_str});\n")
                                
                                backup_success = True
                                log_file.write("¡Éxito! Backup generado usando Python.\n")
                                
                                # Verificar la codificación del archivo generado
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as test_file:
                                        test_content = test_file.read(1024)  # Leer solo un fragmento para verificar
                                        log_file.write(f"Verificación: Archivo generado legible con UTF-8\n")
                                except UnicodeDecodeError as ude:
                                    log_file.write(f"Advertencia: Error al verificar codificación UTF-8: {str(ude)}\n")
                    except Exception as e:
                        log_file.write(f"Error en el método de Python: {str(e)}\n")
            else:
                # Si mysqldump fue encontrado, usarlo normalmente
                # Crear el comando mysqldump
                command = [
                    mysqldump_cmd,
                    f"--defaults-file={my_cnf_path}",
                    '--no-tablespaces',
                    '--skip-triggers',
                    '--complete-insert',
                    '--extended-insert=FALSE',
                    '--skip-add-locks',
                    db_config['database'],
                    f"--result-file={file_path}"
                ]
                
                # Ejecutar el backup con mejor manejo de errores en Windows
                try:
                    # En Windows, especialmente con XAMPP, es mejor usar rutas completas
                    if os.name == 'nt':
                        # Asegurar que las rutas usen el formato correcto para Windows
                        mysqldump_cmd = os.path.normpath(mysqldump_cmd)
                        my_cnf_path = os.path.normpath(my_cnf_path)
                        file_path = os.path.normpath(file_path)
                        
                        with open(log_path, 'a') as log_file:
                            log_file.write(f"Ejecutando comando en Windows:\n")
                            log_file.write(f"  - mysqldump_cmd: {mysqldump_cmd}\n")
                            log_file.write(f"  - my_cnf_path: {my_cnf_path}\n")
                            log_file.write(f"  - file_path: {file_path}\n")
                            log_file.write(f"  - Comando completo: {' '.join(command)}\n")
                    
                        # Configurar para Windows y problemas de codificación de idioma español
                        env = os.environ.copy()
                        # Configurar variables de entorno según el sistema operativo
                        if os.name == 'nt':  # Windows
                            # Para Windows, establecer variables de entorno para codificación
                            env['PYTHONIOENCODING'] = 'latin1'
                            env['LANG'] = 'es_ES.1252'
                            env['LC_ALL'] = 'es_ES.1252'  # Añadir LC_ALL para mayor control de codificación
                        else:  # Unix/Linux
                            env['PYTHONIOENCODING'] = 'utf-8'
                            env['LANG'] = 'es_ES.UTF-8'
                            env['LC_ALL'] = 'es_ES.UTF-8'  # Añadir LC_ALL para mayor control de codificación
                        
                        # Configurar codificación según sistema operativo
                        encoding = 'latin1' if os.name == 'nt' else 'utf-8'
                        errors_mode = 'surrogateescape' if os.name == 'nt' else 'replace'
                        
                        with open(log_path, 'a') as log_file:
                            log_file.write(f"Usando codificación {encoding} con modo de error {errors_mode} para el proceso\n")
                        
                        # Ejecutar el proceso con la configuración adecuada
                        process = subprocess.Popen(
                            command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            encoding=encoding,
                            errors=errors_mode,
                            env=env,
                            universal_newlines=True  # Asegurar manejo correcto de fin de línea
                        )
                        
                        # Esperar a que termine el proceso con timeout
                        output, error = process.communicate(timeout=300)  # Agregar timeout de 5 minutos
                    
                except subprocess.TimeoutExpired:
                    process.kill()
                    output, error = process.communicate()
                    with open(log_path, 'a') as log_file:
                        log_file.write("Error: El proceso de backup excedió el tiempo de espera (5 minutos).\n")
                    raise Exception("El proceso de backup excedió el tiempo de espera. Posible problema con mysqldump.")

                if process.returncode != 0:
                    try:
                        if isinstance(error, bytes):
                            error_msg = error.decode('latin1' if os.name == 'nt' else 'utf-8', errors='replace')
                        elif isinstance(error, str):
                            error_msg = error
                        else:
                            error_msg = str(error)
                    except Exception as decode_error:
                        error_msg = f"Error desconocido al ejecutar mysqldump (error al decodificar: {str(decode_error)})"
                    with open(log_path, 'a') as log_file:
                        log_file.write(f"Error al ejecutar mysqldump: {error_msg}\n")
                        log_file.write(f"Comando ejecutado: {' '.join(command)}\n")
                    raise Exception(f"Error en mysqldump: {error_msg}")
                else:
                    backup_success = True
                    with open(log_path, 'a') as log_file:
                        log_file.write("¡Éxito! Backup generado con mysqldump.\n")
                
        except FileNotFoundError:
            with open(log_path, 'a') as log_file:
                log_file.write("Error: Archivo no encontrado al ejecutar el comando.\n")
                
            # Si todas las opciones fallan, intentar usar el backup a Excel como alternativa
            if not backup_success:
                with open(log_path, 'a') as log_file:
                    log_file.write("Todos los métodos SQL fallaron. Intentando backup a Excel como alternativa...\n")
                return backup_to_excel()  # Fallback a Excel como alternativa
        
        finally:
            # Eliminar el archivo de configuración temporal
            if os.path.exists(my_cnf_path):
                try:
                    os.remove(my_cnf_path)
                except:
                    pass  # Ignorar errores al eliminar el archivo temporal

        # Verificar que el archivo de backup se creó correctamente
        if not backup_success or not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            with open(log_path, 'a') as log_file:
                log_file.write("Error: El archivo de backup SQL no se creó correctamente o está vacío.\n")
            raise Exception("El archivo de backup SQL no se creó correctamente o está vacío")

        # Registrar la acción en el historial
        cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'INSERT INTO user_history (cedula, user, action, time_login) VALUES (%s, %s, %s, %s)',
            (session['cedula'], session['username'], 'Generó backup SQL de la base de datos', datetime.now())
        )
        MySQL.connection.commit()
        cursor.close()

        # Enviar el archivo al usuario
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/sql'
        )

    except FileNotFoundError as e:
        # Agregar más información para el error específico
        with open(log_path, 'a') as log_file:
            log_file.write(f"FileNotFoundError: {str(e)}\n")
            log_file.write(f"Paths comprobados: {', '.join(paths_checked if 'paths_checked' in locals() else ['ninguno'])}\n")
        
        error_msg = f"No se encontró mysqldump.exe. Verifique el archivo de log en {log_path} para más detalles."
        return render_template("gestionar_data.html", error=error_msg)
    
    except PermissionError as e:
        error_msg = f"Error de permisos al crear el backup SQL: {str(e)}. Asegúrese de tener permisos de escritura en la carpeta de backups."
        return render_template("gestionar_data.html", error=error_msg)
    
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        
        # Registrar el error en el log
        try:
            with open(log_path, 'a') as log_file:
                log_file.write(f"Error general: {str(e)}\n")
                import traceback
                log_file.write(traceback.format_exc())
        except:
            pass
        
        # Si el error es que no se puede encontrar mysqldump, dar un mensaje más claro
        error_msg = str(e)
        
        # Mensajes de error más específicos para problemas comunes
        if "No such file or directory" in error_msg or "El sistema no puede encontrar el archivo" in error_msg:
            error_msg = f"No se pudo encontrar mysqldump.exe en su sistema. Si está usando XAMPP, verifique que está instalado correctamente y que las rutas son accesibles. Detalles en el log: {log_path}"
        elif "Access is denied" in error_msg or "permiso denegado" in error_msg.lower():
            error_msg = f"Error de permisos al acceder a mysqldump. Intente ejecutar la aplicación con privilegios de administrador. Detalles en el log: {log_path}"
        elif "exited with code" in error_msg or "returned non-zero" in error_msg:
            error_msg = f"Error al ejecutar mysqldump. El programa terminó con un código de error. Detalles en el log: {log_path}"
        
        # Incluir información sobre XAMPP en el mensaje de error
        if "xampp" not in error_msg.lower():
            paths_info = "Rutas buscadas: " + ", ".join(paths_checked[:5]) + "..." if 'paths_checked' in locals() and len(paths_checked) > 0 else ""
            error_msg += f"\n\nSi está utilizando XAMPP, asegúrese de que MySQL/MariaDB esté instalado y en ejecución. {paths_info}"
        
        return render_template("gestionar_data.html", error=f"Error al crear backup SQL: {error_msg}")

@app.route("/backup_sql", methods=["GET", "POST"])
def backup_sql_route():
    """Ruta para generar backup SQL de la base de datos."""
    # Verificar autenticación primero
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Verificar permisos
    if session.get('Super_Admin') != 1:
        return render_template("gestionar_data.html", error="No tiene permisos para realizar esta acción.")
    
    try:
        # Manejo según el método HTTP
        if request.method == "POST":
            # Verificar si es una confirmación de backup
            action = request.form.get('action')
            if action == 'confirm':
                # Generar el backup SQL
                return backup_to_sql()
            else:
                # Si no hay acción o es diferente, redirigir a la página principal
                return redirect(url_for('gestionar_data'))
        
        elif request.method == "GET":
            # Mostrar la página de confirmación en la interfaz
            return render_template("gestionar_data.html")
        
        else:
            # Método no permitido (diferente de GET o POST)
            return render_template("gestionar_data.html", error="Método no permitido para esta operación."), 405
    
    except Exception as e:
        # Capturar cualquier error no manejado
        return render_template("gestionar_data.html", error=f"Error al generar backup SQL: {str(e)}")
