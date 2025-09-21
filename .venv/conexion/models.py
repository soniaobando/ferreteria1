from flask_login import UserMixin
from conexion import get_connection

class User(UserMixin):
    def __init__(self, id, name, email, password_hash):
        self.id = str(id)  # Flask-Login requiere string
        self.name = name
        self.email = email
        self.password_hash = password_hash

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return User(row["id"], row["name"], row["email"], row["password_hash"])
    return None

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return User(row["id"], row["name"], row["email"], row["password_hash"])
    return None

def create_user(name, email, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)", 
                   (name, email, password_hash))
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return get_user_by_id(user_id)

