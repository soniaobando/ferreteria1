import mysql.connector

def get_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",          # tu usuario de MySQL
        password="123456",  # tu contraseña
        database="ferreteria"    # tu base
    )
    return conn
