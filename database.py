import os
import sqlite3
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "botica.db")
SQL_PATH = os.path.join(BASE_DIR, "Botica_Wsfr.sql")

def init_db_if_not_exists():
    if os.path.exists(DB_PATH):
        print("✔ Base de datos ya existe")
        return

    print("🛠 Creando base de datos desde Botica_Wsfr.sql...")
    conn = sqlite3.connect(DB_PATH)

    with open(SQL_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.close()
    print("✅ Base de datos creada correctamente")
