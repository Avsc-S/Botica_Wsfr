from app import app, db
from models.models import Tbl_Personal, Tbl_Users
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

with app.app_context():

    # Crear persona
    persona = Tbl_Personal(
        DNI="12345678",
        Nombres="Administrador",
        Apellidos="General",
        Activo=1
    )
    db.session.add(persona)
    db.session.commit()

    # Crear usuario admin
    hashed = bcrypt.generate_password_hash("admin123").decode('utf-8')

    user = Tbl_Users(
        Username="admin",
        Email_Acceso="admin@botica.com",
        Password_Hash=hashed,
        Activo=1,
        Id_Personal=persona.Id_Personal
    )

    db.session.add(user)
    db.session.commit()

    print("Usuario admin creado correctamente. ID =", user.Id_User)
