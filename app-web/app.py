from flask import Flask, render_template, request, redirect, url_for, session, make_response, send_from_directory, send_file, jsonify
from flask_mysqldb import MySQL, MySQLdb
import webbrowser

from datetime import datetime, timedelta
from weasyprint import HTML
import os
from babel.dates import format_date
import bcrypt
from markupsafe import Markup
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.drawing.image import Image


app = Flask(__name__)
# Configuraciones
app.config['SECRET_KEY'] = '3054=HitM'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'user623'
app.config['MYSQL_DB'] = 'abril'
MySQL = MySQL(app)
# app.config['SESSION_TYPE'] = 'filesystem' 
# app.config['SESSION_PERMANENT'] = False
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)  
# Session(app)
# from flask_session import Session

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

@app.route("/logout")
def logout():
    cedula = session.get('cedula')
    username = session.get('username')
    time_login = session.get('time_login')
    time_finish = datetime.now()
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO user_history (cedula, user, action, time_login,time_finish) VALUES (%s, %s, %s, %s,%s)',(cedula, username,'sesion cerrada',time_login,time_finish))
    MySQL.connection.commit()
    cursor.close()
    session.pop('loggedin', None)
    session.pop('cedula', None)
    session.pop('username', None)
    session.pop('Super_Admin', None) 
    return redirect(url_for('login'))



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cedula = request.form['cedula']
        password = request.form['password']
        
        if not cedula or not password:
            error = "Cédula y contraseña son requeridas"
            return render_template('login.html', error=error)

        cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tabla WHERE Cedula = %s', (cedula,))
        user = cursor.fetchone()

        if user:
          
            if bcrypt.checkpw(password.encode('utf-8'), user['Password'].encode('utf-8')):
                if user['estado'] == 'suspendido':
                    error = "Tu cuenta está suspendida. Contacta al administrador."
                    return render_template('login.html', error=error)

                session['loggedin'] = True
                session['cedula'] = user['Cedula']
                session['username'] = user['username']
                session['Super_Admin'] = user['Super_Admin']
                session['time_login'] = datetime.now()
                cursor.execute('INSERT INTO user_history (cedula, user, action, time_login) VALUES (%s, %s, %s, %s)', (session['cedula'], session['username'], 'sesion iniciada', datetime.now()))
                MySQL.connection.commit()
                cursor.close()
                if user['Super_Admin'] == 1:
                    return redirect(url_for('consult'))
                else:
                    return redirect(url_for('consult'))
            else:
                error = "Cédula o contraseña incorrecta"
                return render_template('login.html', error=error)
        else:
            error = "Cédula o contraseña incorrecta"
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route("/superAdmin")
def superAdmin():
    return render_template('superAdmin.html')

@app.route("/tipo_user", methods=["GET", "POST"])
def tipo_user():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        cedula = request.form['cedula']
        nuevo_estatus = request.form['super_admin']

        try:
            cursor.execute('SELECT COUNT(*) AS total_personas FROM tabla')
            total_personas = cursor.fetchone()['total_personas']
            cursor.execute(
                'UPDATE tabla SET Super_Admin = %s WHERE Cedula = %s',
                (nuevo_estatus, cedula)
            )
            MySQL.connection.commit()
        except Exception as e:
            MySQL.connection.rollback()
            return render_template("cambiar_super_admin.html", total_personas=total_personas, error=f"Error al actualizar: {str(e)}")

    cursor.execute('SELECT Cedula, username, Super_Admin FROM tabla')
    usuarios = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) AS total_personas FROM tabla')
    total_personas = cursor.fetchone()['total_personas']
    cursor.close()

    return render_template("cambiar_super_admin.html", usuarios=usuarios, total_personas=total_personas)

@app.route("/RegistUser", methods=["GET", "POST"])
def RegistUser():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        cedula = request.form['cedula']
        username = request.form['username']
        password = request.form['password'].replace(" ", "") 
        
        cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Verifica que la cédula se encuentre en la tabla data
        cursor.execute('SELECT * FROM data WHERE Cedula = %s', (cedula,))
        data_user = cursor.fetchone()
        
        if not data_user:
            cursor.close()
            return render_template("regisLogin.html", error="Usted no forma parte del personal activo")
        
        # Verifica que la cédula ya esté registrada en la tabla tabla
        cursor.execute('SELECT * FROM tabla WHERE Cedula = %s', (cedula,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            return render_template("regisLogin.html", error="La cédula ya está registrada en el sistema")
        
        cursor.execute('SELECT * FROM tabla WHERE username = %s', (username,))
        existing_username = cursor.fetchone()
        
        if existing_username:
            cursor.close()
            return render_template("regisLogin.html", error="El nombre de usuario no está disponible")
        
        # Hash de la contraseña antes de guardarla
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Registrar el nuevo usuario en la tabla tabla
        cursor.execute('INSERT INTO tabla (Cedula, username, Password) VALUES (%s, %s, %s)', 
                       (cedula, username, hashed_password))
        MySQL.connection.commit()
  
        cursor.execute('INSERT INTO user_history (cedula, user, action, time_login) VALUES (%s, %s, %s, %s)', 
                       (cedula, username, 'Registro al usuario {0}'.format(cedula), datetime.now()))
        MySQL.connection.commit()
        cursor.close()
        
        return render_template("regisLogin.html", success="Registro exitoso.")
    
    return render_template("regisLogin.html")

@app.route("/", methods=["GET", "POST"])
def consult():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    super_admin = session.get('Super_Admin')
    fecha = request.form.get('fecha', None)
    tipo_usuario = request.form.get('tipo_usuario', 'general')
    cedula = request.form.get('cedula', None)
    session['cedula_titular'] = cedula
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    print("Cédula recibida desde la sesión:",session['cedula_titular'])
    if super_admin == 0:
        # Si el usuario es básico, solo puede ver los datos del día actual
        fecha = datetime.now().strftime('%Y-%m-%d')
    
    if cedula:
        cursor.execute('''
            SELECT data.Cedula, data.Name_Com, data.Location_Physical, data.Type, data.Location_Admin, 
                   IFNULL(delivery.Entregado, 0) AS Entregado, delivery.Observation, data.ESTADOS, data.Estatus
            FROM data
            LEFT JOIN delivery ON data.ID = delivery.Data_ID
            WHERE data.Cedula = %s
        ''', (cedula,))
        data_exit = cursor.fetchone()
        cursor.close()

        if data_exit:
            estatus = data_exit['Estatus']
            if estatus == 3:
                mensaje = "Suspendido por trámites administrativos."
                return render_template('index.html', super_admin=super_admin, mensaje=mensaje, cedula=cedula)
            elif estatus == 4:
                mensaje = "Suspendido por verificar."
                return render_template('index.html', super_admin=super_admin, mensaje=mensaje, cedula=cedula)
            elif estatus == 2:
                cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT COUNT(*) AS total_personas FROM data WHERE Estatus = 2')
                total_personas = cursor.fetchone()['total_personas']
                cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery d JOIN data ON d.Data_ID = data.ID WHERE d.Entregado = 1 AND data.Estatus = 2')
                total_recibido = cursor.fetchone()['total_recibido']
                # total_alert = int(total_recibido)
                # alert = None
                # alert_limite = None
                # if total_alert == 550:
                #     alert = f"{total_alert} personas despachadas"
                #     alert_limite = "Se acerca al limite de 600 "
                # elif total_alert == 590:
                #     alert = f"{total_alert} personas despachadas"
                #     alert_limite = "Se acerca al limite de 600"
                # elif total_alert == 600:
                #     alert = f"{total_alert} personas despachadas"
                #     alert_limite = "Ha alcanzado limite de 600"
                faltan = total_personas - total_recibido
                cursor.close()
                return render_template('index.html', super_admin=super_admin, data=data_exit, total_personas=total_personas, total_recibido=total_recibido, faltan=faltan)
            elif estatus == 6:
                mensaje = "Personal Fallecido"
                return render_template('index.html', super_admin=super_admin, mensaje=mensaje, cedula=cedula)
            elif estatus == 5:
                mensaje = "No puede retirar. Está fuera del país."
                return render_template('index.html', super_admin=super_admin, mensaje=mensaje, cedula=cedula)
            elif estatus == 1:
                cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT COUNT(*) AS total_personas FROM data WHERE Estatus = 1')
                total_personas = cursor.fetchone()['total_personas']
                cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery d JOIN data ON d.Data_ID = data.ID WHERE d.Entregado = 1 AND data.Estatus = 1')
                total_recibido = cursor.fetchone()['total_recibido']
                total_alert = int(total_recibido)
                # alert = None
                # alert_limite = None
                # if total_alert == 550:
                #     alert = f"{total_alert} personas despachadas"
                #     alert_limite = "Se acerca al limite de 600 "
                # elif total_alert == 590:
                #     alert = f"{total_alert} personas despachadas"
                #     alert_limite = "Se acerca al limite de 600"
                # elif total_alert == 600:
                #     alert = f"{total_alert} personas despachadas"
                #     alert_limite = "Ha alcanzado limite de 600"
                faltan = total_personas - total_recibido
                cursor.close()
                return render_template('index.html',  super_admin=super_admin, data=data_exit, total_personas=total_personas, total_recibido=total_recibido, faltan=faltan)
            elif estatus == 10:
                cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT COUNT(*) AS total_personas FROM data WHERE Estatus = 1')
                total_personas = cursor.fetchone()['total_personas']
                cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery d JOIN data ON d.Data_ID = data.ID WHERE d.Entregado = 1 AND data.Estatus = 1')
                total_recibido = cursor.fetchone()['total_recibido']
                total_alert = int(total_recibido)
                # alert = None
                # alert_limite = None
                # if total_alert == 550:
                #     alert = f"{total_alert} personas despachadas"
                #     alert_limite = "Se acerca al limite de 600 "
                # elif total_alert == 590:
                #     alert = f"{total_alert} personas despachadas"
                #     alert_limite = "Se acerca al limite de 600"
                # elif total_alert == 600:
                #     alert = f"{total_alert} personas despachadas"
                #     alert_limite = "Ha alcanzado limite de 600"
                faltan = total_personas - total_recibido
                cursor.close()
                return render_template('index.html',  super_admin=super_admin, data=data_exit, total_personas=total_personas, total_recibido=total_recibido, faltan=faltan)
            
            elif estatus == 11:
                cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT COUNT(*) AS total_personas FROM data WHERE Estatus = 1')
                total_personas = cursor.fetchone()['total_personas']
                cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery d JOIN data ON d.Data_ID = data.ID WHERE d.Entregado = 1 AND data.Estatus = 1')
                total_recibido = cursor.fetchone()['total_recibido']
                faltan = total_personas - total_recibido
                cursor.close()
                return render_template('index.html',  super_admin=super_admin, data=data_exit, total_personas=total_personas, total_recibido=total_recibido, faltan=faltan)
            
            elif estatus == 9:
                 mensaje = "Comisión vencida"
                 mensaje2 = 'Comunicarse con el Supervisor o administrador'
                 return render_template('index.html', super_admin=super_admin, mensaje=mensaje, mensaje2=mensaje2,cedula=cedula, mostrar_boton=True)
            
            else:
                mensaje = "Estatus no permitido para retirar"
                mensaje2 = 'Comunicarse con el administrador'
                return render_template('index.html', super_admin=super_admin, mensaje2=mensaje2, mensaje=mensaje, cedula=cedula)
        else:
            cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT COUNT(*) AS total_personas FROM data')
            total_personas = cursor.fetchone()['total_personas']
            cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery WHERE Entregado = 1')
            total_recibido = cursor.fetchone()['total_recibido']
            faltan = total_personas - total_recibido
            cursor.close()
            mensaje = "Cédula no encontrada"
            return render_template('index.html', super_admin=super_admin, mensaje=mensaje, cedula=cedula, total_personas=total_personas, total_recibido=total_recibido, faltan=faltan)
    else:
        if fecha:
            if tipo_usuario == 'activos':
                cursor.execute('SELECT COUNT(*) AS total_personas FROM data WHERE Estatus = 1')
                total_personas = cursor.fetchone()['total_personas']
                cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery d JOIN data ON d.Data_ID = data.ID WHERE d.Entregado = 1 AND data.Estatus = 1 AND DATE(d.Time_box) = %s', (fecha,))
            elif tipo_usuario == 'pasivos':
                cursor.execute('SELECT COUNT(*) AS total_personas FROM data WHERE Estatus = 2')
                total_personas = cursor.fetchone()['total_personas']
                cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery d JOIN data ON d.Data_ID = data.ID WHERE d.Entregado = 1 AND data.Estatus = 2 AND DATE(d.Time_box) = %s', (fecha,))
           
            elif tipo_usuario == 'comision_servicios_alert':
                cursor.execute('SELECT COUNT(*) AS total_personas FROM data WHERE Estatus IN (9, 11)')
                total_personas = cursor.fetchone()['total_personas']
                cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery d JOIN data ON d.Data_ID = data.ID WHERE d.Entregado = 1 AND data.Estatus IN (9, 11) ')
           
            elif tipo_usuario == 'comision_servicios_2':
                cursor.execute('SELECT COUNT(*) AS total_personas FROM data WHERE Estatus = 10')
                total_personas = cursor.fetchone()['total_personas']
                cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery d JOIN data ON d.Data_ID = data.ID WHERE d.Entregado = 1 AND data.Estatus = 10')
            else:
                cursor.execute('SELECT COUNT(*) AS total_personas FROM data')
                total_personas = cursor.fetchone()['total_personas']
                cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery WHERE Entregado = 1 AND DATE(Time_box) = %s', (fecha,))
        else:
            if tipo_usuario == 'activos':
                cursor.execute('SELECT COUNT(*) AS total_personas FROM data WHERE Estatus = 1')
                total_personas = cursor.fetchone()['total_personas']
                cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery d JOIN data ON d.Data_ID = data.ID WHERE d.Entregado = 1 AND data.Estatus = 1')
            elif tipo_usuario == 'pasivos':
                cursor.execute('SELECT COUNT(*) AS total_personas FROM data WHERE Estatus = 2')
                total_personas = cursor.fetchone()['total_personas']
                cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery d JOIN data ON d.Data_ID = data.ID WHERE d.Entregado = 1 AND data.Estatus = 2')
            else:
                cursor.execute('SELECT COUNT(*) AS total_personas FROM data')
                total_personas = cursor.fetchone()['total_personas']
                cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery WHERE Entregado = 1')
        total_recibido = cursor.fetchone()['total_recibido']
        faltan = total_personas - total_recibido
        cursor.close()
    return render_template('index.html', super_admin=super_admin, total_personas=total_personas, total_recibido=total_recibido, faltan=faltan, fecha=fecha, tipo_usuario=tipo_usuario)


# estatus de comicion vencida
@app.route("/cambiar_estatusComision", methods=["POST"])
def cambiar_estatusComision():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cedula = request.form.get('cedula')
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        # Actualizar el estatus a 11
        cursor.execute('UPDATE data SET Estatus = 11 WHERE Cedula = %s AND Estatus = 9', (cedula,))
        MySQL.connection.commit()
        
        # Registrar el cambio en el historial
        cursor.execute('INSERT INTO user_history (cedula, user, action, time_login) VALUES (%s, %s, %s, %s)', 
                       (session['cedula'], session['username'], f'Cambio de estatus de la cédula {cedula} de 9 a 11', datetime.now()))
        MySQL.connection.commit()
        
        mensaje = "Estatus cambiado exitosamente."
    except Exception as e:
        MySQL.connection.rollback()
        mensaje = f"Error al cambiar el estatus: {str(e)}"
    finally:
        cursor.close()
    
    return redirect(url_for('consult', mensaje=mensaje))

# .................

# entrega de beneficio
@app.route("/registrar", methods=["POST"])
def registrar():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    cedula = request.form['cedula']
  
    cedula_personal = request.form['cedula_personal']
    super_admin = session.get('Super_Admin')
    fecha = request.form.get('fecha', None)
    CIFamily = request.form.get('cedulafamiliar', None)
    lunch = request.form.get('lunch', '0')
    if super_admin == 0:
        # Si el usuario es básico, solo puede ver los datos del día actual
        fecha = datetime.now().strftime('%Y-%m-%d')
        
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    
  # Verificar si la cédula del autorizado o familiar ya existe  
    cursor.execute('''
       SELECT COUNT(*) AS total
       FROM data
        WHERE Cedula_autorizado = %s
    ''', (CIFamily,))
    existe_cedula = cursor.fetchone()['total']

    if existe_cedula > 0:
       cursor.close()
       mensaje = "La cédula del autorizado  ya está registrada en el sistema."
       return render_template('index.html', mensaje=mensaje, cedula=cedula, mensaje2="Por favor, verifique los datos ingresados.")
    
    cursor.execute('SELECT * FROM data WHERE Cedula = %s', (cedula,))
    data_exit = cursor.fetchone()
    
    if not data_exit:
        cursor.close()
        mensaje = "La cédula no se encuentra en la tabla data."
        cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) AS total_personas FROM data')
        total_personas = cursor.fetchone()['total_personas']
        cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery WHERE Entregado = 1 AND DATE(Time_box) = %s', (fecha,))
        total_recibido = cursor.fetchone()['total_recibido']
        faltan = total_personas - total_recibido
        cursor.close()
        return render_template('index.html', mensaje=mensaje, cedula=cedula, mensaje2="Por favor, verifique la cédula ingresada.", total_personas=total_personas, total_recibido=total_recibido, faltan=faltan)
    
    # Registro exitoso
    observacion = request.form.get('observacion', '').upper()
    nameFamily = request.form.get('nombrefamiliar', None).upper() if request.form.get('nombrefamiliar', None) else None
    CIFamily = CIFamily.upper() if CIFamily else None
    hora_entrega = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    estatus = data_exit['Estatus']
    if estatus == 1:
    # Insertar en la tabla delivery para estatus 1
        cursor.execute('INSERT INTO delivery (Time_box, Staff_ID, Observation, Name_Family, Cedula_Family, Data_ID, Entregado, Lunch) VALUES (%s, %s, %s, %s, %s, %s, 1, %s)', 
                   (hora_entrega, cedula_personal, observacion, nameFamily, CIFamily, data_exit['ID'], lunch))

    elif estatus == 2:
    # Insertar en la tabla delivery para estatus 2
        cursor.execute('''
        INSERT INTO delivery (Time_box, Staff_ID, Observation, Data_ID, Entregado, Lunch) 
        VALUES (%s, %s, %s, %s, 1, %s)
    ''', (hora_entrega, cedula_personal, observacion, data_exit['ID'], lunch))

    # Verificar si los campos `Cedula_autorizado` y `Nombre_autorizado` están vacíos
        if not data_exit['Cedula_autorizado'] and not data_exit['Nombre_autorizado']:
        # Actualizar los datos en los campos si están vacíos
            cursor.execute('''
            UPDATE data
            SET Cedula_autorizado = %s, Nombre_autorizado = %s 
            WHERE Cedula = %s
        ''', (CIFamily, nameFamily, cedula))
    else:
        # Si los campos ya tienen datos, no hacer nada
        print("Los campos Cedula_autorizado y Nombre_autorizado ya tienen datos. No se realizará ninguna modificación.")

# Confirmar los cambios en la base de datos
    MySQL.connection.commit()
    
    if data_exit['Cedula']:
        cursor.execute('INSERT INTO user_history (cedula, user, action, time_login) VALUES (%s, %s, %s, %s)', (session['cedula'], session['username'], 'Marco Como Entregado el Beneficio Alimenticio de {0}'.format(data_exit['Cedula']), session['time_login']))
    MySQL.connection.commit()
    
    mensaje = "Registro exitoso."
    mensaje2 = "El registro se ha completado correctamente."
    
  
    cursor.execute('SELECT COUNT(*) AS total_personas FROM data')
    total_personas = cursor.fetchone()['total_personas']
    cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery WHERE Entregado = 1 AND DATE(Time_box) = %s', (fecha,))
    total_recibido = cursor.fetchone()['total_recibido']
    faltan = total_personas - total_recibido
    cursor.close()
    
    return render_template('index.html', mensaje=mensaje, cedula=cedula, mensaje2=mensaje2, total_personas=total_personas, total_recibido=total_recibido, faltan=faltan)

# 78078
# autorizado

@app.route("/obtener_autorizados", methods=["GET"])
def obtener_autorizados():
    if 'loggedin' not in session:
        return jsonify({"error": "No autorizado"}), 403

    # Recupera la cédula del titular desde la sesión
    cedula_titular = session.get('cedula_titular')
    print("Cédula recibida desde la sesión:", cedula_titular)

    if not cedula_titular:
        return jsonify({"error": "Cédula del titular no proporcionada"}), 400

    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT Cedula_autorizado, Nombre_autorizado, estatus
        FROM data
        WHERE Cedula = %s AND (Cedula_autorizado IS NOT NULL AND TRIM(Cedula_autorizado) != '')
    ''', (cedula_titular,))
    autorizados = cursor.fetchall()
    cursor.close()

    if not autorizados:
        return jsonify({"error": "No se encontraron autorizados para esta cédula, desea asignarlo?"}), 404

    return jsonify(autorizados)

#CONTEO DE ENTREGAS POR USUARIO

@app.route("/reporte_entregas_usuario", methods=["GET", "POST"])
def reporte_entregas_usuario():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == "POST":
        fecha = request.form['fecha']
        if fecha:
            cursor.execute('''
                SELECT Staff_ID, DATE(Time_box) as fecha, COUNT(*) as total_entregas
                FROM delivery
                WHERE Entregado = 1 AND DATE(Time_box) = %s
                GROUP BY Staff_ID, DATE(Time_box)
            ''', (fecha,))
        else:
            cursor.execute('''
                SELECT Staff_ID, DATE(Time_box) as fecha, COUNT(*) as total_entregas
                FROM delivery
                WHERE Entregado = 1
                GROUP BY Staff_ID, DATE(Time_box)
            ''')
    else:
        cursor.execute('''
            SELECT Staff_ID, DATE(Time_box) as fecha, COUNT(*) as total_entregas
            FROM delivery
            WHERE Entregado = 1
            GROUP BY Staff_ID, DATE(Time_box)
        ''')
    
    reportes = cursor.fetchall()
    cursor.close()
    
    for reporte in reportes:
        cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT Name_Com FROM data WHERE Cedula = %s', (reporte['Staff_ID'],))
        staff_name = cursor.fetchone()['Name_Com']
        cursor.close()
        reporte['staff_name'] = staff_name
        fecha = reporte['fecha']
        reporte['fecha_formateada'] = format_date(fecha, format='full', locale='es_ES')
    
    return render_template('reporte_entregas_usuario.html', reportes=reportes)

@app.route("/reporte_entregas_usuario_excel", methods=["GET", "POST"])
def reporte_entregas_usuario_excel():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Obtener la fecha del formulario
    fecha = request.form.get('fecha', None)
    
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Filtrar por fecha si se proporciona
    if fecha:
        cursor.execute('''
            SELECT Staff_ID, DATE(Time_box) as fecha, COUNT(*) as total_entregas
            FROM delivery
            WHERE Entregado = 1 AND DATE(Time_box) = %s
            GROUP BY Staff_ID, DATE(Time_box)
        ''', (fecha,))
    else:
        cursor.execute('''
            SELECT Staff_ID, DATE(Time_box) as fecha, COUNT(*) as total_entregas
            FROM delivery
            WHERE Entregado = 1
            GROUP BY Staff_ID, DATE(Time_box)
        ''')
    
    reportes = cursor.fetchall()
    cursor.close()
    
    for reporte in reportes:
        cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT Name_Com FROM data WHERE Cedula = %s', (reporte['Staff_ID'],))
        staff_name = cursor.fetchone()['Name_Com']
        cursor.close()
        reporte['staff_name'] = staff_name
        fecha = reporte['fecha']
        reporte['fecha_formateada'] = format_date(fecha, format='full', locale='es_ES')
    
    # Generar el archivo Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte Entregas Usuario"

    headers = ["Fecha", "Usuario", "Total Entregas"]
    ws.append(headers)
    header_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        cell.fill = header_fill

    for reporte in reportes:
        row = [
            reporte['fecha_formateada'],
            reporte['staff_name'],
            reporte['total_entregas']
        ]
        ws.append(row)
        for cell in ws[ws.max_row]:
            cell.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
            cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    column_widths = {
        'A': 20,
        'B': 30,
        'C': 15
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    from io import BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, download_name="reporte_entregas_usuario.xlsx", as_attachment=True)

# EDITAR EL ESTATUS DE LOS USUARIOS
@app.route("/cambiar_estatus", methods=["GET", "POST"])
def cambiar_estatus():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == "POST":
        cedula = request.form['cedula']
        nuevo_estatus = request.form['estatus']
        
        
        cursor.execute('SELECT Estatus FROM data WHERE Cedula = %s', (cedula,))
        estatus_actual = cursor.fetchone()['Estatus']
        
       
        estatus_nombres = {
            1: "Activo",
            2: "Pasivo",
            3: "Suspendido",
            4: "Suspendido",
            5: "Fuera del país",
            6: "Por verificar"
        }
        
        estatus_actual_nombre = estatus_nombres.get(estatus_actual, "Desconocido")
        nuevo_estatus_nombre = estatus_nombres.get(int(nuevo_estatus), "Desconocido")
        
       
        cursor.execute('UPDATE data SET Estatus = %s WHERE Cedula = %s', (nuevo_estatus, cedula))
        MySQL.connection.commit()
        

        cursor.execute('INSERT INTO user_history (cedula, user, action, time_login) VALUES (%s, %s, %s, %s)', 
                       (session['cedula'], session['username'], f'Cambió el estatus de la cédula {cedula} de {estatus_actual_nombre} a {nuevo_estatus_nombre}', datetime.now()))
        MySQL.connection.commit()
        
        cursor.close()
        return redirect(url_for('cambiar_estatus'))
    
    cursor.execute('SELECT Cedula, Code, Name_Com, Estatus FROM data ')
    usuarios = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) AS total_personas FROM data')
    total_personas = cursor.fetchone()['total_personas']
    cursor.close()
    return render_template('cambiar_estatus.html', usuarios=usuarios, total_personas=total_personas)

@app.route("/editar_usuario/<int:cedula>", methods=["GET", "POST"])
def editar_usuario(cedula):
   
    
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password'].replace(" ", "") 
        unidad_fisica = request.form['unidad_fisica']
        
       
        if password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        else:
            hashed_password = None  
       
        if hashed_password:
            cursor.execute('''
                UPDATE tabla
                SET username = %s, Password = %s
                WHERE Cedula = %s
            ''', (username, hashed_password, cedula))
        else:
            cursor.execute('''
                UPDATE tabla
                SET username = %s
                WHERE Cedula = %s
            ''', (username, cedula))
        
        cursor.execute('''
            UPDATE data
            SET Location_Physical = %s
            WHERE Cedula = %s
        ''', (unidad_fisica, cedula))
        MySQL.connection.commit()
        cursor.close()
        return redirect(url_for('usuarios'))
    
    # Obtener los datos actuales del usuario
    cursor.execute('''
        SELECT tabla.Cedula, data.Name_Com, tabla.username, data.Location_Physical, tabla.Password, tabla.estado
        FROM tabla
        JOIN data ON tabla.Cedula = data.Cedula
        WHERE tabla.Cedula = %s
    ''', (cedula,))
    usuario = cursor.fetchone()
    cursor.close()
    
    return render_template('editar_usuario.html', usuario=usuario)


@app.route("/suspender_usuario/<int:cedula>", methods=["POST"])
def suspender_usuario(cedula):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE tabla SET estado = %s WHERE Cedula = %s', ('suspendido', cedula))
    MySQL.connection.commit()
    cursor.execute('INSERT INTO user_history (cedula, user, action, time_login) VALUES (%s, %s, %s, %s)', (session['cedula'], session['username'], 'Suspendio El Usuario {0}'.format(cedula),session['time_login']))
    MySQL.connection.commit()
    cursor.close()
    return redirect(url_for('usuarios'))

@app.route("/reactivar_usuario/<int:cedula>", methods=["POST"])
def reactivar_usuario(cedula):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE tabla SET estado = %s WHERE Cedula = %s', ('activo', cedula))
    MySQL.connection.commit()
    cursor.execute('INSERT INTO user_history (cedula, user, action, time_login) VALUES (%s, %s, %s, %s)', (session['cedula'], session['username'], 'Reactivo El Usuario {0}'.format(cedula),session['time_login']))
    MySQL.connection.commit()
    cursor.close()
    return redirect(url_for('usuarios'))

@app.route("/usuarios", methods=["GET"])
def usuarios():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT tabla.Cedula, data.Name_Com, tabla.username, data.Location_Physical, data.Location_Admin, tabla.estado
        FROM tabla
        JOIN data ON tabla.Cedula = data.Cedula
    ''')
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route("/reporte_usuarios", methods=["GET","POST"])
def reporte_usuarios():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select * from user_history')
    historial = cursor.fetchall()
    MySQL.connection.commit()
   
    cursor.close()
    return render_template('reporte_usuarios.html', historial=historial)

# REGISTRAR NUEVOS EMPLEADOS ACTIVOS/PASIVOS
@app.route("/nuevoEmpActivo", methods=["GET", "POST"])
def NuevoUserActivo():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        cedula = request.form['cedula']
        nombreCompleto = request.form['nombreCompleto']
        unidadFisica = request.form['unidadFisica']
        unidadAdmin = request.form['unidadAdmin']
        observacion = request.form['observacion']
        CIFamiliar = request.form.get('cedula-family', None)
        Nombre_Familiar = request.form.get('Nombre_Familiar', None)
        CodigoCarnet = request.form.get('CodigoCarnet', None)
        estatus = 1  
        cedula_personal = session['cedula']
        entregado = True if 'entregado' in request.form else False
        lunch = True if 'lunch' in request.form else False
        horaEntrega = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM data WHERE Cedula = %s', (cedula,))
            existing_user = cursor.fetchone()

            if existing_user:
                cursor.close()
                return render_template("nuevo_user_activo.html", error="Esta cédula ya está registrada.")

           
            cursor.execute('SELECT MAX(ID) AS max_id FROM data')
            max_id = cursor.fetchone()['max_id']
            new_id = max_id + 1 if max_id is not None else 1

            cursor.execute('INSERT INTO data (ID, Cedula, Name_Com, Code, Location_Physical, Location_Admin, manually, Estatus) VALUES (%s, %s, %s, %s, %s, %s, 1, %s)', 
                           (new_id, cedula, nombreCompleto, CodigoCarnet, unidadFisica, unidadAdmin, estatus))
            MySQL.connection.commit()
            cursor.execute('INSERT INTO user_history (cedula, user, action, time_login) VALUES (%s, %s, %s, %s)', 
                           (session['cedula'], session['username'], f'Registró un personal activo con cédula {cedula}', datetime.now()))
            MySQL.connection.commit()

            if entregado:
                cursor.execute('SELECT ID FROM data WHERE Cedula = %s', (cedula,))
                data_id = cursor.fetchone()
                cursor.execute('INSERT INTO delivery (Time_box, Staff_ID, Name_Family, Cedula_Family, Observation, Data_ID, Entregado, Lunch) VALUES (%s, %s, %s, %s, %s, %s, 1, %s)', 
                               (horaEntrega, cedula_personal, Nombre_Familiar, CIFamiliar if CIFamiliar else None, observacion, data_id['ID'], lunch))

                MySQL.connection.commit()
                cursor.execute('INSERT INTO user_history (cedula, user, action, time_login) VALUES (%s, %s, %s, %s)', 
                               (session['cedula'], session['username'], f'Marcó como entregado el beneficio alimenticio para la cédula {cedula}', datetime.now()))
                MySQL.connection.commit()
            cursor.close()
            return render_template("nuevo_user_activo.html", success="Registro exitoso.")  
        except Exception as e:
            return render_template("nuevo_user_activo.html", error=f"Error en el registro: {str(e)}")
    return render_template("nuevo_user_activo.html")

@app.route("/nuevoEmpPasivo", methods=["GET", "POST"])
def NuevoUserPasivo():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        cedula = request.form['cedula']
        nombreCompleto = request.form['nombreCompleto']
        observacion = request.form['observacion']
        CIFamiliar = request.form.get('cedula-family', None)
        Nombre_Familiar = request.form.get('Nombre_Familiar', None)
        CodigoCarnet = request.form.get('CodigoCarnet', None)
        estatus = 2  
        estado = request.form['estado']
        cedula_personal = session['cedula']
        entregado = True if 'entregado' in request.form else False
        lunch = True if 'lunch' in request.form else False
        horaEntrega = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM data WHERE Cedula = %s', (cedula,))
            existing_user = cursor.fetchone()

            if existing_user:
                cursor.close()
                return render_template("nuevo_user_pasivo.html", error="Esta cédula ya está registrada.")

            cursor.execute('SELECT MAX(ID) AS max_id FROM data')
            max_id = cursor.fetchone()['max_id']
            new_id = max_id + 1 if max_id is not None else 1

            cursor.execute('INSERT INTO data (ID, Cedula, Name_Com, Code, manually, Estatus, ESTADOS) VALUES (%s, %s, %s, %s, 1, %s, %s)', 
                           (new_id, cedula, nombreCompleto, CodigoCarnet, estatus, estado))
            MySQL.connection.commit()
            cursor.execute('INSERT INTO user_history (cedula, user, action, time_login) VALUES (%s, %s, %s, %s)', 
                           (session['cedula'], session['username'], f'Registró un personal pasivo con cédula {cedula}', datetime.now()))
            MySQL.connection.commit()

            if entregado:
                cursor.execute('SELECT ID FROM data WHERE Cedula = %s', (cedula,))
                data_id = cursor.fetchone()
                cursor.execute('INSERT INTO delivery (Time_box, Staff_ID, Name_Family, Cedula_Family, Observation, Data_ID, Entregado, Lunch) VALUES (%s, %s, %s, %s, %s, %s, 1, %s)', 
                               (horaEntrega, cedula_personal, Nombre_Familiar, CIFamiliar if CIFamiliar else None, observacion, data_id['ID'], lunch))

                MySQL.connection.commit()
                cursor.execute('INSERT INTO user_history (cedula, user, action, time_login) VALUES (%s, %s, %s, %s)', 
                               (session['cedula'], session['username'], f'Marcó como entregado el beneficio alimenticio para la cédula {cedula}', datetime.now()))
                MySQL.connection.commit()
            cursor.close()
            return render_template("nuevo_user_pasivo.html", success="Registro exitoso.")  
        except Exception as e:
            return render_template("nuevo_user_pasivo.html", error=f"Error en el registro: {str(e)}")
    return render_template("nuevo_user_pasivo.html")

# MOSTRAR REPORTE DE ENTREGADOS
@app.route("/reporte")
def reporte():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT DATE(Time_box) as fecha,
               SUM(CASE WHEN data.Estatus = 1 THEN 1 ELSE 0 END) as total_activos,
               SUM(CASE WHEN data.Estatus = 2 THEN 1 ELSE 0 END) as total_pasivos,
               SUM(CASE WHEN data.Estatus  IN (9, 11)  THEN 1 ELSE 0 END) as total_comision_vencida,
               SUM(CASE WHEN data.Estatus = 10 THEN 1 ELSE 0 END) as total_comision_vigente,
               COUNT(*) as total_entregas
        FROM delivery
        JOIN data ON delivery.Data_ID = data.ID
        WHERE Entregado = 1
        GROUP BY DATE(Time_box)
    ''')
    reportes = cursor.fetchall()

    # Calcular totales generales
    total_entregas = sum(reporte['total_entregas'] for reporte in reportes)
    total_activos = sum(reporte['total_activos'] for reporte in reportes)
    total_pasivos = sum(reporte['total_pasivos'] for reporte in reportes)
    total_comision_vencida = sum(reporte['total_comision_vencida'] for reporte in reportes)
    total_comision_vigente = sum(reporte['total_comision_vigente'] for reporte in reportes)

    cursor.close()

    # Formatear las fechas
    for reporte in reportes:
        fecha = reporte['fecha']
        reporte['fecha_formateada'] = format_date(fecha, format='full', locale='es_ES')

    return render_template(
        'reporte.html',
        reportes=reportes,
        total_entregas=total_entregas,
        total_activos=total_activos,
        total_pasivos=total_pasivos,
        total_comision_vencida=total_comision_vencida,
        total_comision_vigente=total_comision_vigente
    )
# GENERAR REPORTE DE ENTREGADOS EN PDF
@app.route("/reporte_pdf", methods=["GET", "POST"])
def reporte_pdf():
    if request.method == "POST":
        fecha = request.form['fecha']
        cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT DATE(Time_box) as fecha,
                   SUM(CASE WHEN data.Estatus = 1 THEN 1 ELSE 0 END) as total_activos,
                   SUM(CASE WHEN data.Estatus = 2 THEN 1 ELSE 0 END) as total_pasivos,
                   SUM(CASE WHEN data.Estatus IN (9, 11) THEN 1 ELSE 0 END) as total_comision_vencida,
                   SUM(CASE WHEN data.Estatus = 10 THEN 1 ELSE 0 END) as total_comision_vigente,
                   COUNT(*) as total_entregas
            FROM delivery
            JOIN data ON delivery.Data_ID = data.ID
            WHERE Entregado = 1 AND DATE(Time_box) = %s
            GROUP BY DATE(Time_box)
        ''', (fecha,))
    else:
        cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT DATE(Time_box) as fecha,
                   SUM(CASE WHEN data.Estatus = 1 THEN 1 ELSE 0 END) as total_activos,
                   SUM(CASE WHEN data.Estatus = 2 THEN 1 ELSE 0 END) as total_pasivos,
                   SUM(CASE WHEN data.Estatus IN (9, 11) THEN 1 ELSE 0 END) as total_comision_vencida,
                   SUM(CASE WHEN data.Estatus = 10 THEN 1 ELSE 0 END) as total_comision_vigente,
                   COUNT(*) as total_entregas
            FROM delivery
            JOIN data ON delivery.Data_ID = data.ID
            WHERE Entregado = 1
            GROUP BY DATE(Time_box)
        ''')
    reportes = cursor.fetchall()
    cursor.close()
    
    # Calcular totales generales
    total_entregas = sum(reporte['total_entregas'] for reporte in reportes)
    total_activos = sum(reporte['total_activos'] for reporte in reportes)
    total_pasivos = sum(reporte['total_pasivos'] for reporte in reportes)
    total_comision_vencida = sum(reporte['total_comision_vencida'] for reporte in reportes)
    total_comision_vigente = sum(reporte['total_comision_vigente'] for reporte in reportes)
    
    # Formatear las fechas
    for reporte in reportes:
        fecha = reporte['fecha']
        reporte['fecha_formateada'] = format_date(fecha, format='full', locale='es_ES')
    
    rendered = render_template(
        'reporte_pdf.html',
        reportes=reportes,
        total_entregas=total_entregas,
        total_activos=total_activos,
        total_pasivos=total_pasivos,
        total_comision_vencida=total_comision_vencida,
        total_comision_vigente=total_comision_vigente
    )
    pdf = HTML(string=rendered).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte.pdf'
    return response

# MOSTRAR LISTADO DE ENTREGADOS 
@app.route("/listado")
def listado():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('''
    SELECT d.Data_ID, d.Time_box, d.Entregado, d.Staff_ID, d.Observation, d.Lunch, d.Cedula_Family, d.Name_Family,data.Cedula_autorizado, data.Nombre_autorizado,
           data.Cedula, data.Code, data.Name_Com, data.Manually, data.Location_Admin, data.Estatus, data.ESTADOS, data.Location_Physical,
           staff.Name_Com AS Registrador_Name  -- Incluye el nombre del registrador
    FROM delivery d
    JOIN data ON d.Data_ID = data.ID
    LEFT JOIN data AS staff ON d.Staff_ID = staff.Cedula  -- Une con la tabla de datos para obtener el nombre del registrador
    WHERE d.Entregado = 1
    ''')
    registros = cursor.fetchall()
       
    cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery WHERE Entregado = 1')
    total_recibido = cursor.fetchone()['total_recibido']
    cursor.close()
    return render_template('tabla.html', registros=registros, total_recibido=total_recibido)

# GENERAR LISTADO DE ENTREGADOS EN PDF
@app.route("/listado_pdf", methods=["GET", "POST"])
def listado_pdf():
    if request.method == "POST":
        fecha = request.form['fecha']
        cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT d.Data_ID, d.Time_box, d.Entregado,  d.Staff_ID, d.Observation, d.Lunch,d.Cedula_Family, d.Name_Family,data.Cedula_autorizado, data.Nombre_autorizado,
                   data.Cedula, data.Name_Com,data.Manually,data.Location_Admin, data.Estatus,data.ESTADOS,data.Location_Physical 
            FROM delivery d
            JOIN data ON d.Data_ID = data.ID
            WHERE d.Entregado = 1 AND DATE(d.Time_box) = %s
        ''', (fecha,))
        registros = cursor.fetchall()
        cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery WHERE Entregado = 1 AND DATE(Time_box) = %s', (fecha,))
        total_recibido = cursor.fetchone()['total_recibido']
        cursor.close()

        rendered = render_template('tabla_pdf.html', registros=registros, total_recibido=total_recibido, fecha=fecha)
        pdf = HTML(string=rendered).write_pdf()

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=listado.pdf'
        return response
    else:
        return render_template('tabla_pdf.html')
    
# GENERAR LISTADO EN EXCEL
@app.route("/listado_excel", methods=["GET", "POST"])
def listado_excel():
    if request.method == "POST":
        fecha = request.form['fecha']
        filtro = request.form.get('filtro', 'todos')  # Obtiene el filtro seleccionado

        # Construir la consulta SQL dinámicamente
        query = '''
            SELECT d.Data_ID, d.Time_box, d.Entregado, d.Staff_ID, d.Observation, d.Lunch,d.Cedula_Family, d.Name_Family,data.Cedula_autorizado, data.Nombre_autorizado,
                   data.Cedula, data.Name_Com, data.Manually, data.Location_Admin, data.Estatus, data.ESTADOS, data.Location_Physical 
            FROM delivery d
            JOIN data ON d.Data_ID = data.ID
            WHERE d.Entregado = 1 AND DATE(d.Time_box) = %s
        '''
        if filtro == 'autorizados':
            query += ' AND (d.Cedula_Family IS NOT NULL OR data.Cedula_autorizado IS NOT NULL)'
        elif filtro == 'activo':
            query += ' AND data.Estatus = 1'
        elif filtro == 'pasivo':
            query += ' AND data.Estatus = 2'
        elif filtro == 'manually':
            query += ' AND data.Manually = 1'
        elif filtro == 'comision_vencida':
            query += ' AND data.Estatus IN (9, 11)'
        elif filtro == 'comision_vigente':
            query += ' AND data.Estatus = 10'

        query += ' ORDER BY data.ESTADOS ASC, data.Location_Physical ASC, data.Location_Admin ASC'

        cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query, (fecha,))
        registros = cursor.fetchall()
        cursor.execute('SELECT COUNT(*) AS total_recibido FROM delivery WHERE Entregado = 1 AND DATE(Time_box) = %s', (fecha,))
        total_recibido = cursor.fetchone()['total_recibido']
        cursor.close()

        # Generar el archivo Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Listado"

        img1_path = os.path.join(app.root_path, 'static/css/img/logo.png')
        img2_path = os.path.join(app.root_path, 'static/css/img/logo2.png')
        img1 = Image(img1_path)
        img2 = Image(img2_path)
        img1.width, img1.height = 60, 60
        img2.width, img2.height = 60, 60
        ws.add_image(img1, 'A1')

        headers = ["#", "Cedula", "Nombre Completo", "Estado", "Estatus", "Unidad Fisica", "Ubicación administrativa", "Hora de Entrega", "Cedula del Autorizado", "Nombre del Autorizado", "Observacion", "Registro Manual", "Merienda", "Cedula del Registrador", "Nombre del Registrador"]

        last_column = chr(64 + len(headers))
        img2.anchor = f'{last_column}1'
        ws.add_image(img2)

        ws.row_dimensions[1].height = 55

        ws.merge_cells(f'A1:{last_column}1')
        ws['A1'] = "Listado de Personas que han Recibido la Caja"
        ws['A1'].font = Font(size=14, bold=True)
        ws['A1'].alignment = Alignment(horizontal="center", vertical="center")

        ws.append(headers)
        header_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
        for cell in ws[2]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
            cell.fill = header_fill

        ws.row_dimensions[2].height = 30

        for idx, registro in enumerate(registros, start=1):
            cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT Name_Com FROM data WHERE Cedula = %s', (registro['Staff_ID'],))
            staff_name = cursor.fetchone()['Name_Com']
            cursor.close()
            
            cedula_autorizado = registro['Cedula_Family'] if registro['Cedula_Family'] else registro['Cedula_autorizado'] if registro['Cedula_autorizado'] else ''
            nombre_autorizado = registro['Name_Family'] if registro['Name_Family'] else registro['Nombre_autorizado'] if registro['Nombre_autorizado'] else ''

            estatus = "Activo" if registro['Estatus'] == 1 else "Pasivo" if registro['Estatus'] == 2 else "Comisión Vencida" if registro['Estatus'] == 9 else "Comisión Vencida" if registro['Estatus'] == 11 else "Comisión Vigente"
           
            row = [
                idx,
                registro['Cedula'],
                registro['Name_Com'],
                registro['ESTADOS'] if registro['Estatus'] in [2, 9, 10] else "",
                estatus,
                registro['Location_Physical'] if  registro['Estatus'] == 1 else "",
                registro['Location_Admin'] if   registro['Estatus'] == 1 else "",
                registro['Time_box'],
                cedula_autorizado,
                nombre_autorizado,
                registro['Observation'] if registro['Observation'] else ' ',
                "Si" if registro['Manually'] else 'No',
                "Si" if registro['Lunch'] else 'No',
                registro['Staff_ID'],
                staff_name
            ]
            
            ws.append(row)
            for cell in ws[ws.max_row]:
                cell.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
                cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

        column_widths = {
            'A': 7,
            'B': 10,
            'C': 20,
            'D': 20,
            'E': 20,
            'F': 20,
            'G': 20,
            'H': 20,
            'I': 20,
            'J': 20,
            'K': 20,
            'L': 20,
            'M': 20,
            'N': 20,
            'O': 20,
            'P': 20
        }
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        for row in ws.iter_rows(min_row=3, max_row=ws.max_row):
            ws.row_dimensions[row[0].row].height = 82.5

        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        nombre_archivo = f"listado_entregados_{fecha_actual}.xlsx"
        
        return send_file(output, download_name=nombre_archivo, as_attachment=True)
    return render_template('tabla_pdf.html')


# GENERAR LISTADO DE NO ENTREGADOS 
@app.route("/listado_no_registrado")
def listado_no_registrado():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT data.Cedula, data.Name_Com, data.Location_Physical, data.Estatus,data.ESTADOS,data.Code,data.Location_Admin, delivery.Entregado
        FROM data
        LEFT JOIN delivery ON data.ID = delivery.Data_ID
        WHERE delivery.Entregado IS NULL OR delivery.Entregado = 0
    ''')
    registros = cursor.fetchall()
    cursor.execute('''
        SELECT COUNT(*) AS total_no_entregados
        FROM data
        LEFT JOIN delivery ON data.ID = delivery.Data_ID
        WHERE delivery.Entregado IS NULL OR delivery.Entregado = 0
    ''')
    total_no_entregados = cursor.fetchone()['total_no_entregados']
    cursor.close()
    return render_template('listado_no_registrado.html', registros=registros, total_no_entregados=total_no_entregados)

# GENERAR LISTADO DE NO ENTREGADOS EN PDF
@app.route("/listado_no_regist_pdf", methods=["GET", "POST"])
def listado_no_regist_pdf():
    filtro = request.args.get('filtro', 'todos')  # Obtiene el filtro desde la URL (por defecto "todos")
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Construir la consulta SQL dinámicamente según el filtro
    query = '''
        SELECT data.Cedula, data.Name_Com, data.Location_Physical, data.Location_Admin, data.Code, data.Estatus, data.ESTADOS, delivery.Entregado
        FROM data
        LEFT JOIN delivery ON data.ID = delivery.Data_ID
        WHERE delivery.Entregado IS NULL OR delivery.Entregado = 0
    '''
    if filtro == 'activos':
        query += ' AND data.Estatus = 1'
    elif filtro == 'pasivos':
        query += ' AND data.Estatus = 2'
    elif filtro == 'comision_vigente':
        query += ' AND data.Estatus = 10'
    elif filtro == 'comision_vencida':
        query += ' AND data.Estatus IN (9, 11)'
    
    cursor.execute(query)
    registros = cursor.fetchall()
    
    # Contar el total de registros según el filtro
    cursor.execute(f'''
        SELECT COUNT(*) AS total_no_entregados
        FROM data
        LEFT JOIN delivery ON data.ID = delivery.Data_ID
        WHERE delivery.Entregado IS NULL OR delivery.Entregado = 0
        {'AND data.Estatus = 1' if filtro == 'activos' else ''}
        {'AND data.Estatus = 2' if filtro == 'pasivos' else ''}
        {'AND data.Estatus = 10' if filtro == 'comision_vigente' else ''}
        {'AND data.Estatus IN (9, 11)' if filtro == 'comision_vencida' else ''}
    ''')
    total_no_entregados = cursor.fetchone()['total_no_entregados']
    cursor.close()
    
    rendered = render_template('tabla_no_regist_pdf.html', registros=registros, total_no_entregados=total_no_entregados, filtro=filtro)
    pdf = HTML(string=rendered).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=listado.pdf'
    return response

# Generar listado de no entregado en excel
@app.route("/listado_no_registrado_excel", methods=["GET", "POST"])
def listado_no_registrado_excel():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Obtener el filtro de estatus desde el formulario
    filtro = request.form.get('filtro', 'todos')  # Por defecto, "todos"
    print(f"Filtro seleccionado: {filtro}")

    # Construir la consulta SQL dinámicamente según el filtro
    query = '''
        SELECT data.Cedula, data.Name_Com, data.Location_Physical, data.Location_Admin, data.Code, data.Estatus, data.ESTADOS, delivery.Entregado
        FROM data
        LEFT JOIN delivery ON data.ID = delivery.Data_ID
        WHERE delivery.Entregado IS NULL OR delivery.Entregado = 0
    '''
    if filtro == 'activo':
        query += ' AND data.Estatus = 1'
    elif filtro == 'pasivo':
        query += ' AND data.Estatus = 2'
    elif filtro == 'comision_vigente':
        query += ' AND data.Estatus = 10'
    elif filtro == 'comision_vencida':
        query += ' AND data.Estatus IN (9, 11)'
    elif filtro == 'autorizados':
        query += ' AND (data.Cedula_autorizado IS NOT NULL OR TRIM(data.Cedula_autorizado) != "")'

    # Ejecutar la consulta
    cursor = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query)
    registros = cursor.fetchall()
    cursor.close()

    # Generar el archivo Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "No Entregados"

    # Agregar imágenes
    img1_path = os.path.join(app.root_path, 'static/css/img/logo.png')
    img2_path = os.path.join(app.root_path, 'static/css/img/logo2.png')
    img1 = Image(img1_path)
    img2 = Image(img2_path)
    img1.width, img1.height = 60, 60
    img2.width, img2.height = 60, 60
    ws.add_image(img1, 'A1')

    # Encabezados
    headers = ["#", "Cédula", "Nombre Completo", "Unidad Física", "Ubicación Administrativa", "Código", "Estatus", "Estado", "Entregado"]
    last_column = chr(64 + len(headers))
    img2.anchor = f'{last_column}1'
    ws.add_image(img2)

    ws.row_dimensions[1].height = 55
    ws.merge_cells(f'A1:{last_column}1')
    ws['A1'] = "Listado de Personas que No han Recibido la Caja"
    ws['A1'].font = Font(size=14, bold=True)
    ws['A1'].alignment = Alignment(horizontal="center", vertical="center")

    # Agregar encabezados
    ws.append(headers)
    header_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
    for cell in ws[2]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        cell.fill = header_fill

    ws.row_dimensions[2].height = 30

    # Agregar los datos
    for idx, registro in enumerate(registros, start=1):
        estatus = "Activo" if registro['Estatus'] == 1 else "Pasivo" if registro['Estatus'] == 2 else "Comisión Vencida" if registro['Estatus'] in [9, 11] else "Comisión Vigente" if registro['Estatus'] == 10 else "Desconocido"
        row = [
            idx,
            registro['Cedula'],
            registro['Name_Com'],
            registro['Location_Physical'],
            registro['Location_Admin'],
            registro['Code'],
            estatus,
            registro['ESTADOS'],
            "No" if registro['Entregado'] == 0 or registro['Entregado'] is None else "Sí"
        ]
        ws.append(row)
        for cell in ws[ws.max_row]:
            cell.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
            cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    # Ajustar el ancho de las columnas
    column_widths = {
        'A': 7,
        'B': 15,
        'C': 25,
        'D': 20,
        'E': 25,
        'F': 15,
        'G': 20,
        'H': 15,
        'I': 10
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    # Guardar el archivo en memoria
    from io import BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Obtener la fecha actual para el nombre del archivo
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    nombre_archivo = f"listado_no_entregados_{fecha_actual}.xlsx"

    return send_file(output, download_name=nombre_archivo, as_attachment=True)

@app.route('/check_session')
def check_session():
    if 'loggedin' in session:
        return jsonify({"active": True})
    else:
        return jsonify({"active": False})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    