from Conexion.conexion import obtener_conexion

def obtener_productos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos")
    datos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return datos


def insertar_producto(nombre, categoria, talla, color, precio, stock, imagen):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO productos(nombre,categoria,talla,color,precio,stock,imagen)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (nombre,categoria,talla,color,precio,stock,imagen))

    conexion.commit()
    cursor.close()
    conexion.close()


def obtener_producto_por_id(id_producto):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT * FROM productos WHERE id_producto=%s",
        (id_producto,)
    )

    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    return producto


def actualizar_producto(id_producto, nombre, categoria, talla, color, precio, stock):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE productos
        SET nombre=%s,categoria=%s,talla=%s,color=%s,precio=%s,stock=%s
        WHERE id_producto=%s
    """, (nombre,categoria,talla,color,precio,stock,id_producto))

    conexion.commit()
    cursor.close()
    conexion.close()


def eliminar_producto(id_producto):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM productos WHERE id_producto=%s",
        (id_producto,)
    )

    conexion.commit()
    cursor.close()
    conexion.close()