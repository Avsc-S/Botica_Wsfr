from datetime import date
from extensions import db


class Tbl_Personal(db.Model):
    __tablename__ = 'Tbl_Personal'

    Id_Personal = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DNI = db.Column(db.String(10), unique=True, nullable=False)
    Nombres = db.Column(db.String(100))
    Apellidos = db.Column(db.String(100))
    Fecha_Nacimiento = db.Column(db.Date)
    Telefono = db.Column(db.String(20))
    Direccion = db.Column(db.String(200))
    Email_Personal = db.Column(db.String(150))
    
    Id_Distrito = db.Column(db.Integer)
    Id_Provincia = db.Column(db.Integer)
    Id_Departamento = db.Column(db.Integer)
    Id_Pais = db.Column(db.Integer)

    Fecha_Ingreso = db.Column(db.Date)
    Activo = db.Column(db.Integer)

    # Relación con usuario
    usuario = db.relationship("Tbl_Users", lazy=True, uselist=False)

class Tbl_Users(db.Model):
    __tablename__ = 'Tbl_Users'

    Id_User = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Username = db.Column(db.String(100), unique=True, nullable=False)
    Email_Acceso = db.Column(db.String(150))
    Password_Hash = db.Column(db.String(255), nullable=False)
    Activo = db.Column(db.Integer, default=1)

    # NUEVOS CAMPOS PARA SEGURIDAD
    Intentos_Fallidos = db.Column(db.Integer, default=0)
    Bloqueado = db.Column(db.Integer, default=0)
    Fecha_Alta = db.Column(db.Date, default=date.today)
    
    # FK con personal
    Id_Personal = db.Column(db.Integer, db.ForeignKey('Tbl_Personal.Id_Personal'))
    Id_Role = db.Column(db.Integer, db.ForeignKey('Tbl_Roles.Id_Role'))
    personal = db.relationship("Tbl_Personal", lazy=True)

    # ✅ NUEVO: control centralizado
    @property
    def puede_editar(self):
        return self.Activo == 1 and self.Bloqueado == 0


class Tbl_Roles(db.Model):
    __tablename__ = 'Tbl_Roles'

    Id_Role = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nom_Role = db.Column(db.String(50), unique=True, nullable=False)
    Descripcion = db.Column(db.String(200))

    usuarios = db.relationship("Tbl_Users", backref="rol", lazy=True)

class Tbl_Privilegios(db.Model):
    __tablename__ = 'Tbl_Privilegios'

    Id_Privilegio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nom_Privilegio = db.Column(db.String(100), unique=True)
    Descripcion = db.Column(db.String(200))

class Tbl_Role_Privilegio(db.Model):
    __tablename__ = 'Tbl_Role_Privilegio'

    Id_Role_Privilegio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Id_Role = db.Column(db.Integer, db.ForeignKey('Tbl_Roles.Id_Role'))
    Id_Privilegio = db.Column(db.Integer, db.ForeignKey('Tbl_Privilegios.Id_Privilegio'))

class Tbl_Pais(db.Model):
    __tablename__ = 'Tbl_Pais'

    Id_Pais = db.Column(db.Integer, primary_key=True)
    Nom_Pais = db.Column(db.String(150), nullable=False)
    FechaAlta_Pais = db.Column(db.Date)
    Observ_Pais = db.Column(db.String(255))

    departamentos = db.relationship("Tbl_Departamento", backref="pais", lazy=True)


class Tbl_Provincia(db.Model):
    __tablename__ = 'Tbl_Provincia'

    Id_Provincia = db.Column(db.Integer, primary_key=True)
    Nom_Provincia = db.Column(db.String(150), nullable=False)
    Id_Departamento = db.Column(
        db.Integer, db.ForeignKey('Tbl_Departamento.Id_Departamento')
    )
    FechaAlta_Provincia = db.Column(db.Date)
    Observ_Provincia = db.Column(db.String(255))

    distritos = db.relationship("Tbl_Distrito", backref="provincia", lazy=True)


class Tbl_Distrito(db.Model):
    __tablename__ = 'Tbl_Distrito'

    Id_Distrito = db.Column(db.Integer, primary_key=True)
    Nom_Distrito = db.Column(db.String(150), nullable=False)
    Id_Provincia = db.Column(db.Integer, db.ForeignKey('Tbl_Provincia.Id_Provincia'))
    FechaAlta_Distrito = db.Column(db.Date)
    Observ_Distrito = db.Column(db.String(255))

class Tbl_Departamento(db.Model):
    __tablename__ = 'Tbl_Departamento'

    Id_Departamento = db.Column(db.Integer, primary_key=True)
    Nom_Departamento = db.Column(db.String(150), nullable=False)
    Id_Pais = db.Column(db.Integer, db.ForeignKey('Tbl_Pais.Id_Pais'))
    FechaAlta_Departamento = db.Column(db.Date)
    Observ_Departamento = db.Column(db.String(255))

    provincias = db.relationship("Tbl_Provincia", backref="departamento", lazy=True)
