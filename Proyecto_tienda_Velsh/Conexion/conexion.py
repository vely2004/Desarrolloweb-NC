import mysql.connector

def obtener_conexion():
    conexion = mysql.connector.connect(
        host="127.0.0.1",
        port=33065,
        user="root",
        password="",
        database="tienda_velsh",
        auth_plugin="mysql_native_password"
    )
    return conexion