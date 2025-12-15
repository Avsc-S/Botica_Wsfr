from app import app, db
from models.models import Tbl_Users, Tbl_Roles

with app.app_context():
    user = Tbl_Users.query.filter_by(Username="admin").first()
    admin_role = Tbl_Roles.query.filter_by(Nom_Role="Administrador").first()

    user.Id_Role = admin_role.Id_Role
    db.session.commit()

    print("Rol asignado:", user.Username, "->", admin_role.Nom_Role)
