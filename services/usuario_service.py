from extensions import db
from models.models import Tbl_Users

def sincronizar_usuario_con_empleado(empleado):
    usuario = Tbl_Users.query.filter_by(Id_Personal=empleado.Id_Personal).first()

    if not usuario:
        return

    if empleado.Activo == 0:
        usuario.Bloqueado = 1
        usuario.Activo = 0
    else:
        usuario.Bloqueado = 0
        usuario.Activo = 1

    db.session.commit()
