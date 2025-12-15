# Importar modelos despues de inicializar db
from extensions import db
from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for, abort
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from services.usuario_service import sincronizar_usuario_con_empleado

app = Flask(__name__)

# Configuración de la base de datos SQLite
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'botica.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'clave-secreta-123'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Botica_Wsfr/botica.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY'] = 'clave-secreta-123'

db.init_app(app)

from models.models import Tbl_Personal, Tbl_Users, Tbl_Roles

bcrypt = Bcrypt(app)

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect('/login')

            user = Tbl_Users.query.get(session['user_id'])

            if user.rol.Nom_Role not in allowed_roles:
                return abort(403)  # Prohibido

            return f(*args, **kwargs)
        return wrapper
    return decorator

def get_current_user():
    if 'user_id' not in session:
        return None
    return Tbl_Users.query.get(session['user_id'])


# ========= RUTAS =========
@app.route('/')
def inicio():
    if 'user_id' in session:
        return redirect('/panel')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # 🔹 LIMPIAR SESIÓN AL MOSTRAR LOGIN
    if request.method == 'GET':
        session.clear()
        return render_template(
            'login.html',
            foco='usuario'
        )

    if request.method == 'POST':
        # Obtener datos del formulario (sin autofill del navegador)
        usuario = request.form.get('user_name', '').strip()
        clave = request.form.get('user_pass', '')

        user = Tbl_Users.query.filter_by(Username=usuario).first()

        # ❌ Usuario no existe
        if not user:
            return render_template(
                'login.html',
                error="Usuario no existe",
                username="",
                foco="username"
            )

        # 🔒 VALIDAR EMPLEADO ASOCIADO
        empleado = None
        if user.Id_Personal:
            empleado = Tbl_Personal.query.get(user.Id_Personal)

        if empleado and empleado.Activo == 0:
            return render_template(
                'login.html',
                error="Empleado desactivado. Contacte al administrador.",
                username=usuario,
                foco="username"
            )

        # 🔒 USUARIO DESACTIVADO
        if user.Activo == 0:
            return render_template(
                'login.html',
                error="Usuario desactivado. Contacte al administrador.",
                username=usuario,
                foco="username"
            )
        
        # 🔒 USUARIO BLOQUEADO
        if user.Bloqueado == 1:
            return render_template(
                'login.html',
                error="Usuario bloqueado. Contacte al administrador.",
                username=usuario,
                foco="username"
            )


        # ❌ CONTRASEÑA INCORRECTA
        if not bcrypt.check_password_hash(user.Password_Hash, clave):

            if user.Intentos_Fallidos is None:
                user.Intentos_Fallidos = 0

            user.Intentos_Fallidos += 1

            # 🔒 DESACTIVAR USUARIO (NO EMPLEADO)
            if user.Intentos_Fallidos >= 3:
                user.Activo = 0
                db.session.commit()
                return render_template(
                    'login.html',
                    error=f"Usuario desactivado por múltiples intentos fallidos. Contacte al administrador.",
                    username=usuario,
                    foco="username"
                )

            db.session.commit()
            return render_template(
                'login.html',
                error=f"Contraseña incorrecta. Intentos: {user.Intentos_Fallidos}/3",
                username=usuario,
                foco="password"
            )

        # ✅ LOGIN CORRECTO
        user.Intentos_Fallidos = 0
        db.session.commit()

        session.clear()
        session['user_id'] = user.Id_User
        session['username'] = user.Username

        return redirect('/panel')

    # GET → formulario limpio
    return render_template(
        'login.html',
        username="",
        foco="username"
    )


@app.route('/usuarios/<int:id>/unlock', methods=['POST'])
@role_required("Administrador")
def usuario_unlock(id):
    user = Tbl_Users.query.get_or_404(id)
    user.Intentos_Fallidos = 0
    user.Bloqueado = 0
    db.session.commit()
    return redirect('/usuarios')


@app.route('/panel')
def panel():
    if 'user_id' not in session:
        return redirect('/login')

    user = Tbl_Users.query.get(session['user_id'])
    return render_template(
        'panel.html',
        username=user.Username,
        role=user.rol.Nom_Role
        )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ================== ROLES ==================

@app.route('/roles')
@role_required("Administrador")
def roles_list():
    current_user = get_current_user()
    roles = Tbl_Roles.query.all()
    return render_template(
        'roles_list.html',
        username=current_user.Username,
        role=current_user.rol.Nom_Role,
        roles=roles
    )


@app.route('/roles/nuevo', methods=['GET', 'POST'])
@role_required("Administrador")
def rol_nuevo():
    current_user = get_current_user()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']

        nuevo = Tbl_Roles(Nom_Role=nombre, Descripcion=descripcion)
        db.session.add(nuevo)
        db.session.commit()

        return redirect('/roles')

    return render_template(
        'role_form.html',
        username=current_user.Username,
        role=current_user.rol.Nom_Role,
        modo='nuevo'
    )


@app.route('/roles/<int:id>/editar', methods=['GET', 'POST'])
@role_required("Administrador")
def rol_editar(id):
    current_user = get_current_user()
    rol = Tbl_Roles.query.get_or_404(id)

    if request.method == 'POST':
        rol.Nom_Role = request.form['nombre']
        rol.Descripcion = request.form['descripcion']
        db.session.commit()
        return redirect('/roles')

    return render_template(
        'role_form.html',
        username=current_user.Username,
        role=current_user.rol.Nom_Role,
        modo='editar',
        rol=rol
    )


@app.route('/roles/<int:id>/eliminar', methods=['POST'])
@role_required("Administrador")
def rol_eliminar(id):
    rol = Tbl_Roles.query.get_or_404(id)

    # (opcional) evitar borrar rol si tiene usuarios
    if rol.usuarios:
        return "No se puede eliminar un rol con usuarios asignados", 400

    db.session.delete(rol)
    db.session.commit()
    return redirect('/roles')

# ================== USUARIOS ==================
from sqlalchemy import or_

@app.route('/usuarios')
@role_required("Administrador")
def usuarios_list():
    current_user = get_current_user()

    q = request.args.get('q', '').strip()
    campo = request.args.get('campo', 'usuario')

    query = Tbl_Users.query.join(Tbl_Roles, isouter=True)\
                           .join(Tbl_Personal, isouter=True)

    # 🔍 FILTROS SEGÚN CAMPO
    if q:
        if campo == 'usuario':
            query = query.filter(Tbl_Users.Username.ilike(f"%{q}%"))

        elif campo == 'rol':
            query = query.filter(Tbl_Roles.Nom_Role.ilike(f"%{q}%"))

        elif campo == 'empleado':
            query = query.filter(
                or_(
                    Tbl_Personal.Nombres.ilike(f"%{q}%"),
                    Tbl_Personal.Apellidos.ilike(f"%{q}%")
                )
            )

    usuarios = query.all()
    roles = Tbl_Roles.query.all()

    return render_template(
        'usuarios_list.html',
        username=current_user.Username,
        role=current_user.rol.Nom_Role,
        usuarios=usuarios,
        roles=roles,
        q=q,
        campo=campo
    )


@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
@role_required("Administrador")
def usuario_nuevo():
    current_user = get_current_user()

    # Cargar roles y empleados para los combos
    roles = Tbl_Roles.query.all()
    # 🔹 Empleados SIN usuario
    empleados = Tbl_Personal.query.filter(
        Tbl_Personal.usuario == None
    ).all()

    # ========================
    # POST → Guardar usuario
    # ========================
    if request.method == 'POST':

        # Datos enviados por el formulario
        # Datos del formulario NUEVO USUARIO
        username = request.form.get('usr_codigo', '').strip()
        email    = request.form.get('usr_email', '').strip()
        password = request.form.get('usr_clave', '')
        id_role = request.form['id_role']
        id_personal = request.form['id_personal']

        # 🔒 Validar campos obligatorios
        if not username.strip() or not email.strip() or not password.strip():
            return render_template(
                'usuario_form.html',
                modo='nuevo',
                roles=roles,
                empleados=empleados,
                error="Debe completar todos los campos obligatorios"
            )

        # ❌ VALIDAR USUARIO DUPLICADO
        existe_usuario = Tbl_Users.query.filter_by(Username=username).first()
        if existe_usuario:
            return render_template(
                'usuario_form.html',
                modo='nuevo',
                roles=roles,
                empleados=empleados,
                error="El nombre de usuario ya existe. Elija otro."
            )

        # 🔐 Encriptar contraseña
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')

        from datetime import date

        # Crear usuario
        nuevo = Tbl_Users(
            Username=username,
            Email_Acceso=email,
            Password_Hash=hashed,
            Activo=1,
            Fecha_Alta=date.today(),
            Id_Role=id_role or None,
            Id_Personal=id_personal or None
        )

         # ========================
        # TRY / EXCEPT → CAPA BD
        # ========================
        try:
            db.session.add(nuevo)
            db.session.commit()

        except IntegrityError:
            # 🔄 Revertir transacción
            db.session.rollback()

            return render_template(
                'usuario_form.html',
                modo='nuevo',
                roles=roles,
                empleados=empleados,
                error="El usuario o email ya existen en el sistema."
            )

        return redirect('/usuarios')

    # ========================
    # GET → Formulario limpio
    # ========================
    from datetime import date

    return render_template(
        'usuario_form.html',
        modo='nuevo',
        roles=roles,
        empleados=empleados,
        fecha_hoy=date.today().isoformat(),
        nav_user=current_user.Username,   # 👈 SOLO PARA NAVBAR
        role=current_user.rol.Nom_Role
    )

@app.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@role_required("Administrador")
def usuario_editar(id):
    current_user = get_current_user()
    user = Tbl_Users.query.get_or_404(id)

    # 🔒 BLOQUEO REAL: no permitir editar usuarios inactivos o bloqueados
    if user.Activo == 0 or user.Bloqueado == 1:
        abort(403)


    roles = Tbl_Roles.query.all()
    # 👇 Empleados sin usuario O el empleado actual del usuario
    empleados = Tbl_Personal.query.filter(
        (Tbl_Personal.usuario == None) |
        (Tbl_Personal.Id_Personal == user.Id_Personal)
    ).all()

    # ========================
    # POST → Actualizar usuario
    # ========================
    if request.method == 'POST':

        # 📥 Leer datos EXACTAMENTE como vienen del HTML
        username = request.form.get('usr_codigo', '').strip()
        email = request.form.get('usr_email', '').strip()
        nueva_clave = request.form.get('usr_clave', '')
        id_role = request.form.get('id_role')
        id_personal = request.form.get('id_personal')
        
        # 🔒 Validación básica
        if not username or not email:
            return render_template(
                'usuario_form.html',
                modo='editar',
                usuario=user,
                roles=roles,
                empleados=empleados,
                error="Usuario y Email son obligatorios"
            )

        # ❌ Validar usuario duplicado (excepto él mismo)
        existe_usuario = Tbl_Users.query.filter(
            Tbl_Users.Username == username,
            Tbl_Users.Id_User != user.Id_User
        ).first()

        if existe_usuario:
            return render_template(
                'usuario_form.html',
                modo='editar',
                usuario=user,
                roles=roles,
                empleados=empleados,
                error="El nombre de usuario ya pertenece a otro usuario"
            )

        # ❌ Validar email duplicado (excepto él mismo)
        existe_email = Tbl_Users.query.filter(
            Tbl_Users.Email_Acceso == email,
            Tbl_Users.Id_User != user.Id_User
        ).first()

        if existe_email:
            return render_template(
                'usuario_form.html',
                modo='editar',
                usuario=user,
                roles=roles,
                empleados=empleados,
                error="El email ya está registrado en otro usuario"
            )

        # ========================
        # Actualizar datos
        # ========================
        user.Username = username
        user.Email_Acceso = email
        user.Id_Role = id_role or None
        user.Id_Personal = id_personal or None

        # 🔐 Cambiar contraseña SOLO si se ingresó algo
        if nueva_clave.strip():
            user.Password_Hash = bcrypt.generate_password_hash(
                nueva_clave
            ).decode('utf-8')

        # ========================
        # TRY / EXCEPT → capa BD
        # ========================
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return render_template(
                'usuario_form.html',
                modo='editar',
                usuario=user,
                roles=roles,
                empleados=empleados,
                error="Error al guardar cambios. Posible duplicidad de datos."
            )

        return redirect('/usuarios')

    # ========================
    # GET → Mostrar formulario
    # ========================
    return render_template(
        'usuario_form.html',
        modo='editar',
        usuario=user,
        roles=roles,
        empleados=empleados,
        username=current_user.Username,
        role=current_user.rol.Nom_Role
    )


# ----------------------------
#  EXPORTAR A EXCEL
# ----------------------------
import pandas as pd
from flask import send_file
from io import BytesIO

@app.route('/usuarios/exportar')
@role_required("Administrador")
def usuarios_exportar_excel():

    q = request.args.get('q', '').strip()
    query = Tbl_Users.query

    if q:
        query = query.filter(
            (Tbl_Users.Username.ilike(f"%{q}%")) |
            (Tbl_Users.Email_Acceso.ilike(f"%{q}%"))
        )

    usuarios = query.all()

    data = []
    for u in usuarios:
        data.append({
            "Usuario": u.Username,
            "Email": u.Email_Acceso,
            "Rol": u.rol.Nom_Role if u.rol else "Sin rol",
            "Estado": "Activo" if u.Activo == 1 else "Inactivo",
            "Empleado": (
                f"{u.personal.Nombres} {u.personal.Apellidos}"
                if u.personal else "Sin empleado"
            ),
            # 🔹 SOLO PARA EXCEL
            "Fecha Alta": (
                u.Fecha_Alta.strftime("%d/%m/%Y")
                if u.Fecha_Alta else ""
            )

        })

    df = pd.DataFrame(data)

    output = BytesIO()
    df.to_excel(output, index=False, sheet_name="Usuarios")
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="usuarios.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route('/usuarios/<int:id>/toggle', methods=['POST'])
@role_required("Administrador")
def usuario_toggle_activo(id):
    user = Tbl_Users.query.get_or_404(id)
    user.Activo = 0 if user.Activo == 1 else 1
    db.session.commit()
    return redirect('/usuarios')

@app.route('/usuarios/<int:id>/eliminar', methods=['POST'])
@role_required("Administrador")
def usuario_eliminar_fisico(id):
    current_user = get_current_user()
    user = Tbl_Users.query.get_or_404(id)

    # 🔒 Seguridad: no permitir eliminarse a sí mismo
    if user.Id_User == current_user.Id_User:
        abort(403)

    # 🔒 Seguridad adicional: romper vínculo con empleado
    user.Id_Personal = None

    db.session.delete(user)
    db.session.commit()

    return redirect('/usuarios')

@app.route('/empleados')
@role_required("Administrador")
def empleados_list():

    current_user = get_current_user()

    q = request.args.get('q', '').strip()
    filtro = request.args.get('filtro', 'dni')

    query = Tbl_Personal.query

    if q:
        if filtro == 'dni':
            query = query.filter(Tbl_Personal.DNI.like(f"%{q}%"))
        elif filtro == 'nombres':
            query = query.filter(Tbl_Personal.Nombres.like(f"%{q}%"))
        elif filtro == 'apellidos':
            query = query.filter(Tbl_Personal.Apellidos.like(f"%{q}%"))
        elif filtro == 'email':
            query = query.filter(Tbl_Personal.Email_Personal.like(f"%{q}%"))

    empleados = query.order_by(Tbl_Personal.Apellidos.asc()).all()

    return render_template(
        "empleados_list.html",
        empleados=empleados,
        titulo="Empleados del sistema",
        url_nuevo=url_for("empleado_nuevo"),
        url_exportar=url_for("empleado_exportar_excel", **request.args),
        url_volver=url_for("empleados_list"),
        placeholder="Ingrese criterio de búsqueda",
        texto_nuevo="Nuevo"
    )





@app.route('/empleados/nuevo', methods=['GET', 'POST'])
@role_required("Administrador")
def empleado_nuevo():
    current_user = get_current_user()

    from datetime import date
    from models.models import (
    Tbl_Pais, Tbl_Departamento, Tbl_Provincia, Tbl_Distrito
    )

    paises = Tbl_Pais.query.all()
    departamentos = Tbl_Departamento.query.all()
    provincias = Tbl_Provincia.query.all()
    distritos = Tbl_Distrito.query.all()

    fecha_hoy = date.today().isoformat()

    if request.method == 'POST':

        # ----------------------------
        #  VALIDACIÓN DE DNI (8 dígitos)
        # ----------------------------
        dni = request.form['dni']
        if not dni.isdigit() or len(dni) != 8:
            return render_template(
                "empleado_form.html",
                error="El DNI debe contener exactamente 8 dígitos",
                modo="nuevo",
                paises=paises,
                provincias=provincias,
                distritos=distritos,
                fecha_hoy=fecha_hoy
            )

        # ----------------------------
        # VALIDAR DNI DUPLICADO
        # ----------------------------
        existe_dni = Tbl_Personal.query.filter_by(DNI=dni).first()
        if existe_dni:
            return render_template(
            "empleado_form.html",
            error="Ya existe un empleado registrado con este DNI",
            modo="nuevo",
            paises=paises,
            departamentos=departamentos,
            provincias=provincias,
            distritos=distritos,
            fecha_hoy=fecha_hoy,
            username=current_user.Username,
            role=current_user.rol.Nom_Role
            )

        # ----------------------------
        # VALIDACIÓN DE EMAIL PERSONAL
        # ----------------------------
        email_personal = request.form["email_personal"]
        if email_personal and "@" not in email_personal:
            return render_template(
                "empleado_form.html",
                error="Ingrese un correo electrónico válido",
                modo="nuevo",
                paises=paises,
                provincias=provincias,
                distritos=distritos,
                fecha_hoy=fecha_hoy
            )

        # ----------- SI TODO OK, REGISTRAR ----------
        from datetime import datetime

        fecha_nac = request.form['fecha_nac']
        fecha_ing = request.form['fecha_ingreso']

        fecha_nacimiento = datetime.strptime(fecha_nac, "%Y-%m-%d").date() if fecha_nac else None
        fecha_ingreso = datetime.strptime(fecha_ing, "%Y-%m-%d").date() if fecha_ing else None

        nuevo = Tbl_Personal(
            DNI=dni,
            Nombres=request.form['nombres'],
            Apellidos=request.form['apellidos'],
            Fecha_Nacimiento=fecha_nacimiento,
            Telefono=request.form['telefono'],
            Direccion=request.form['direccion'],
            Email_Personal=email_personal,
            Id_Pais=request.form['id_pais'] or None,
            Id_Departamento=request.form['id_departamento'] or None,
            Id_Provincia=request.form['id_provincia'] or None,
            Id_Distrito=request.form['id_distrito'] or None,
            Fecha_Ingreso=fecha_ingreso,
            Activo=1
            )


        db.session.add(nuevo)
        db.session.commit()

        return redirect('/empleados')

    # GET: mostrar formulario vacío
    return render_template(
        "empleado_form.html",
        paises=paises,
        departamentos=departamentos,
        provincias=provincias,
        distritos=distritos,
        fecha_hoy=fecha_hoy,
        modo="nuevo",
        username=current_user.Username,
        role=current_user.rol.Nom_Role
    )


@app.route('/empleados/<int:id>/editar', methods=['GET', 'POST'])
@role_required("Administrador")
def empleado_editar(id):
    current_user = get_current_user()
    empleado = Tbl_Personal.query.get_or_404(id)

    # 🔒 BLOQUEO REAL
    if empleado.Activo == 0:
        abort(403)

    if request.method == 'POST':
        empleado.DNI = request.form['dni']
        empleado.Nombres = request.form['nombres']
        empleado.Apellidos = request.form['apellidos']
        empleado.Telefono = request.form['telefono']
        empleado.Direccion = request.form['direccion']

        db.session.commit()

        return redirect('/empleados')

    return render_template(
        'empleado_form.html',
        username=current_user.Username,
        role=current_user.rol.Nom_Role,
        modo="editar",
        empleado=empleado
    )


@app.route('/empleados/<int:id>/estado', methods=['POST'])
@role_required("Administrador")
def empleado_cambiar_estado(id):
    empleado = Tbl_Personal.query.get_or_404(id)

    # Cambiar estado
    empleado.Activo = 0 if empleado.Activo == 1 else 1

    db.session.commit()

    # 🔁 AQUÍ VA TU RECOMENDACIÓN
    sincronizar_usuario_con_empleado(empleado)

    return redirect('/empleados')

@app.route('/empleados/<int:id>/crear-usuario', methods=['GET', 'POST'])
@role_required("Administrador")
def empleado_crear_usuario(id):
    current_user = get_current_user()
    empleado = Tbl_Personal.query.get_or_404(id)
    roles = Tbl_Roles.query.all()

    # 🔒 BLOQUEO REAL: empleado INACTIVO
    if empleado.Activo == 0:
        return abort(403)

    # 🔒 BLOQUEO REAL: ya tiene usuario
    if empleado.usuario:
        return redirect('/empleados')

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        id_role = request.form['id_role']

        if not password.strip():
            return render_template(
                "usuario_desde_empleado.html",
                error="Debe ingresar una contraseña",
                empleado=empleado,
                roles=roles
            )

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')

        nuevo = Tbl_Users(
            Username=username,
            Email_Acceso=email,
            Password_Hash=hashed,
            Activo=1,
            Id_Role=id_role,
            Id_Personal=empleado.Id_Personal
        )

        db.session.add(nuevo)
        db.session.commit()

        return redirect('/empleados')

    return render_template(
        "usuario_desde_empleado.html",
        empleado=empleado,
        roles=roles,
        username=current_user.Username,
        role=current_user.rol.Nom_Role
    )

@app.route('/empleados/<int:id>/eliminar', methods=['POST'])
@role_required("Administrador")
def empleado_eliminar_fisico(id):

    # Obtener empleado o 404
    empleado = Tbl_Personal.query.get_or_404(id)

    # 🔒 No permitir eliminar si tiene usuario asociado
    if empleado.usuario:
        abort(403)

    # 🔒 (Opcional) exigir que esté inactivo
    if empleado.Activo == 1:
        abort(403)

    try:
        db.session.delete(empleado)
        db.session.commit()

    except Exception:
        db.session.rollback()
        abort(500)

    return redirect('/empleados')

import pandas as pd
from flask import send_file
from io import BytesIO

@app.route('/empleados/exportar-excel')
@role_required("Administrador")
def empleado_exportar_excel():

    q = request.args.get('q', '').strip()
    filtro = request.args.get('filtro', 'dni')

    query = Tbl_Personal.query

    if q:
        if filtro == 'dni':
            query = query.filter(Tbl_Personal.DNI.like(f"%{q}%"))
        elif filtro == 'nombres':
            query = query.filter(Tbl_Personal.Nombres.like(f"%{q}%"))
        elif filtro == 'apellidos':
            query = query.filter(Tbl_Personal.Apellidos.like(f"%{q}%"))
        elif filtro == 'email':
            query = query.filter(Tbl_Personal.Email_Personal.like(f"%{q}%"))

    empleados = query.order_by(Tbl_Personal.Apellidos.asc()).all()

    data = []
    for e in empleados:
        data.append({
            "ID": e.Id_Personal,
            "DNI": e.DNI,
            "Nombres": e.Nombres,
            "Apellidos": e.Apellidos,
            "Teléfono": e.Telefono or "",
            "Dirección": e.Direccion or "",
            "Estado": "Activo" if e.Activo == 1 else "Inactivo"
        })

    df = pd.DataFrame(data)

    output = BytesIO()
    df.to_excel(output, index=False, sheet_name="Empleados")
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="empleados.xlsx"
    )


# ================= API UBIGEO =================
from flask import jsonify
from models.models import Tbl_Departamento, Tbl_Provincia, Tbl_Distrito

@app.route('/api/departamentos/<int:id_pais>')
def api_departamentos(id_pais):
    deps = Tbl_Departamento.query.filter_by(Id_Pais=id_pais).all()
    return jsonify([
        {"id": d.Id_Departamento, "nombre": d.Nom_Departamento}
        for d in deps
    ])


@app.route('/api/provincias/<int:id_departamento>')
def api_provincias(id_departamento):
    provs = Tbl_Provincia.query.filter_by(Id_Departamento=id_departamento).all()
    return jsonify([
        {"id": p.Id_Provincia, "nombre": p.Nom_Provincia}
        for p in provs
    ])


@app.route('/api/distritos/<int:id_provincia>')
def api_distritos(id_provincia):
    dists = Tbl_Distrito.query.filter_by(Id_Provincia=id_provincia).all()
    return jsonify([
        {"id": d.Id_Distrito, "nombre": d.Nom_Distrito}
        for d in dists
    ])



# === Capturar el error 403 en Flask ===
@app.errorhandler(403)
def forbidden_error(e):
    return render_template("403.html"), 403

# === EJECUTAR SERVIDOR ===
if __name__ == '__main__':
    app.run(debug=True)
