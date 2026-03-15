from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
from form import PedidoForm
from inventario.bd import db, Cliente, ProductoDB
from inventario.inventario import Inventario
from inventario.productos import Producto
from Conexion.conexion import obtener_conexion
from werkzeug.security import generate_password_hash

import json
import csv
import os

#--- Inicializar app---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "super_secret_key"
app.permanent_session_lifetime = timedelta(minutes=15)


#inicar AQLAlchemy
db.init_app(app)



#--- Archivos para guardar pedidos---
txt_file = "inventario/data/datos.txt"
json_file = "inventario/data/datos.json"
csv_file = "inventario/data/datos.csv"


#<<<<<<<<<<<<<<<<<<<< Rutas>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>Ruta principal<<<<<<<<<<<<<<<<<<
@app.route('/')
def inicio():
    conexion = obtener_conexion()              # Conecta con MySQL
    cursor = conexion.cursor(dictionary=True)  # Devuelve filas como diccionario

    cursor.execute("SELECT * FROM productos")  # Trae todos los productos
    productos = cursor.fetchall()              # Guardamos todos los productos

    cursor.close()
    conexion.close()
    return render_template("index.html", productos=productos)

#>>>>>>>>>>>>> Rutas por categorías<<<<<<<<<<<<<<<<
#--- Rutas por categorías usando MySQL ---
@app.route('/categoria/<tipo>')
def categoria(tipo):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM productos WHERE LOWER(categoria) = LOWER(%s)",
        (tipo,)
    )

    productos_categoria = cursor.fetchall()

    cursor.close()
    conexion.close()

    # Diccionario para mapear tipo → plantilla
    plantillas = {
        "deportivos": "deportivos.html",
        "elegantes": "elegantes.html",
        "botas": "botas.html",
        "mocasines": "mocasines.html"
    }

    if tipo.lower() in plantillas:
        return render_template(
            plantillas[tipo.lower()],
            productos_categoria=productos_categoria
        )
    else:
        return "Categoría no encontrada", 404
#>>>>>>>>>>>>>Ruta about<<<<<<<<<<<<<<<<<<
@app.route('/about')
def about():
    return render_template("about.html")
#---Ruta ofertas---
@app.route('/ofertas')
def ofertas():
    return render_template("ofertas.html")

#>>>>>>>>>>>>Ruta pedido<<<<<<<<<<<<<
@app.route('/pedido', methods=['GET', 'POST'])
def pedido():

    form = PedidoForm()  # <-- formulario
    # ---- SESIÓN ACTIVA ----
    usuario_nombre = session.get("usuario")
    usuario_info = None
    if usuario_nombre:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE nombre=%s", (usuario_nombre,))
        usuario_info = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario_info:
            form.nombre.data = usuario_info["nombre"]
            form.email.data = usuario_info["mail"]
    # ---- FIN SESIÓN ----
    if form.validate_on_submit():  # <-- Validación del formulario
        # datos del formulario
        nombre = form.nombre.data
        email = form.email.data
        celular = form.celular.data
        direccion = form.direccion.data
        producto = form.producto.data

        # -- SQLITE  con SQLalchemy--
        nuevo_cliente = Cliente(
        nombre=nombre,
        email=email,
        celular=celular,
        direccion=direccion,
        producto=producto
        )
        db.session.add(nuevo_cliente)
        db.session.commit()

        # -- TXT --
        with open("inventario/data/datos.txt", "a", encoding="utf-8") as f:
            f.write(f"{nombre},{email},{celular},{direccion},{producto}\n")

        # -- JSON --
        pedido_dict = {
            "nombre": nombre,
            "email": email,
            "celular": celular,
            "direccion": direccion,
            "producto": producto
        }
        with open(json_file,"r", encoding="utf-8") as f:
            datos = json.load(f)
        datos.append(pedido_dict)
        with open(json_file,"w", encoding="utf-8") as f:
            json.dump(datos,f,indent=4)

        # -- CSV --
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([nombre, email, celular, direccion, producto])

        # Mostrar confirmación
        return render_template("pedido_confirmado.html", nombre=nombre, producto=producto)

    return render_template("pedido.html", form=form)

#<<<<<<<<<<<<PEDIDOS MYSQL<<<<<<<<<<<<<
@app.route('/admin/pedidos')
def ver_pedidos():
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM pedidos")
        pedidos = cursor.fetchall()

        cursor.close()
        conexion.close()

        return render_template("admin/admin_pedidos.html", pedidos=pedidos)

#---Modificar pedido---
@app.route('/admin/pedidos/editar/<int:id_pedido>', methods=['GET', 'POST'])
def editar_pedido(id_pedido):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE id_pedido=%s", (id_pedido,))
    pedido = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        celular = request.form['celular']
        direccion = request.form['direccion']
        producto = request.form['producto']

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE pedidos 
            SET nombre=%s, email=%s, celular=%s, direccion=%s, producto=%s 
            WHERE id_pedido=%s
        """, (nombre,email,celular,direccion,producto,id_pedido))
        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect(url_for('ver_pedidos'))

    return render_template("admin/admin_editarp.html", pedido=pedido)

#---Eliminar pedido---
@app.route('/admin/pedidos/eliminar/<int:id_pedido>')
def eliminar_pedido(id_pedido):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM pedidos WHERE id_pedido=%s", (id_pedido,))
    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(url_for('ver_pedidos'))
#<<<<<<<<<<Ruta contacto>>>>>>>>>>>
@app.route('/contacto')
def contacto():
    return render_template("contacto.html")


#<<<<<<<<<<<Seguridad>>>>>>>>>>>>>>
class Seguridad:
    def __init__(self, usuario_correcto, clave_correcta):
        self.usuario_correcto = usuario_correcto
        self.clave_correcta = clave_correcta

    def verificar(self, usuario_ingresado, clave_ingresada):
        return (
            usuario_ingresado == self.usuario_correcto and
            clave_ingresada == self.clave_correcta
        )

seguridad = Seguridad("Velsh", "0706194511")

#<<<<<<<<<<<<<<<Ruta sesion de administrador>>>>>>>>>>>>>>>
#---Ruta de login---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contraseña = request.form.get("contraseña")

        if seguridad.verificar(usuario, contraseña):
            session["admin"] = True   # 🔐 
            session.permanent = False  
            return redirect(url_for("admin"))
        else:
            return "Usuario o clave incorrectos"

    return render_template("login.html")
#<<<<<<<<<<<<<<<Ruta de logout<<<<<<<<<<<<<<<<<<
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
#_________Ruta administrador_________
@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Si no hay sesión activa, redirige al login
    if not session.get("admin"):
        return redirect(url_for("login"))
    #Si ya está logueado, muestra el panel
    productos = inventario.mostrar_productos()
    return render_template("admin.html", mostrar_login=False, productos=productos)
# Mostrar todos los productos
@app.route("/admin/mostrar")
def admin_mostrar():
    productos = inventario.mostrar_productos()
    return render_template("admin_productos.html", productos=productos)

# ---Ruta de admin para añadir productos---
@app.route("/admin/añadir", methods=["GET", "POST"])
def admin_añadir():
    mensaje = ""
    if request.method == "POST":
        # Extraer datos del formulario
        nombre = request.form.get("nombre")
        cantidad = int(request.form.get("cantidad"))
        precio = float(request.form.get("precio"))
        categoria = request.form.get("categoria")
        talla = request.form.get("talla")
        color = request.form.get("color")

        archivo = request.files.get("imagen")
        if not archivo or archivo.filename == "":
            mensaje = "Debes subir una imagen para el producto"
            return render_template("admin_añadir.html", mensaje=mensaje, productos=inventario.mostrar_productos())
        
        # Guardar imagen en la carpeta static/images

        ruta = os.path.join("static", "img", archivo.filename)
        archivo.save(ruta)
        imagen = f"img/{archivo.filename}"

        #creación de producto + DB
        producto = Producto(
            None, 
            nombre,
            cantidad,
            precio,
            categoria,
            talla,
            color,
            imagen
   )
        inventario.agregar_producto(producto)

        mensaje = "Producto agregado correctamente"

    return render_template(
        "admin_añadir.html",
        mensaje=mensaje,
        productos=inventario.mostrar_productos()
    )

# ---Ruta de admin para eliminar productos---
@app.route("/admin/eliminar", methods=["GET", "POST"])
def admin_eliminar():
    mensaje = ""
    if request.method == "POST":
        id_str = request.form.get("id_producto")
        if not id_str:
            mensaje = "Debes ingresar un ID"
        else:
            id_producto = int(id_str)

            # Verificar si existe en memoria
            if id_producto in inventario.productos:
                inventario.eliminar_producto(id_producto)  # Borra memoria + DB
                mensaje = "Producto eliminado"

            else:
                mensaje = "ID no encontrado"

    return render_template(
        "admin_eliminar.html",
        mensaje=mensaje,
        productos=inventario.mostrar_productos()
    )
# ---Ruta de admin para actualizar productos---
@app.route("/admin/actualizar", methods=["GET", "POST"])
def admin_actualizar():
    mensaje = ""

    if request.method == "POST":
        id_producto = request.form.get("id_producto")

        if not id_producto:
            mensaje = "Debes ingresar un ID"
        else:
            id_producto = int(id_producto)

            nombre = request.form.get("nombre")
            cantidad = request.form.get("cantidad")
            precio = request.form.get("precio")
            categoria = request.form.get("categoria")
            talla = request.form.get("talla")
            color = request.form.get("color")

            inventario.actualizar_producto_db(
                id_producto, nombre, cantidad, precio, categoria, talla, color
            )

            mensaje = "Producto actualizado correctamente"

    return render_template(
        "admin_actualizar.html",
        mensaje=mensaje,
        productos=inventario.mostrar_productos()
    )

# ---Ruta de admin buscar productos---
@app.route("/admin/buscar", methods=["GET", "POST"])
def admin_buscar():
    productos = []
    mensaje = ""

    if request.method == "POST":
        nombre = request.form.get("nombre")

        if not nombre:
            mensaje = "Debes ingresar un nombre"
        else:
            productos = inventario.buscar_producto_db(nombre)

            if not productos:
                mensaje = "No se encontraron productos"

    return render_template(
        "admin_buscar.html",
        productos=productos,
        mensaje=mensaje
    )
# ---Ruta de admin para mostrar productos---
@app.route("/admin/productos")
def admin_productos():
    productos = inventario.mostrar_productos()
    return render_template(
        "admin_productos.html",
        productos=productos
    )

#---Ruta de admin para mostrar datos de pedidos---
@app.route('/admin/datos')
def mostrar_datos():
     # --- Pedidos desde SQLite ---
    pedidos_db = Cliente.query.all()  # Trae todos los pedidos de la base de datos
    # Leer TXT
    pedidos_txt = []
    if os.path.exists(txt_file):
        with open(txt_file, "r", encoding="utf-8") as f:
            for linea in f:
                if linea.strip():
                    partes = linea.strip().split(",", 4)
                    if len(partes) == 5:
                        nombre, email, celular, direccion, producto = partes
                        pedidos_txt.append({
                        "nombre": nombre,
                        "email": email,
                        "celular": celular,
                        "direccion": direccion,
                        "producto": producto
                    })

    # Leer JSON
    pedidos_json = []
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            pedidos_json = json.load(f)

    # Leer CSV
    pedidos_csv = []
    if os.path.exists(csv_file):
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pedidos_csv.append(row)

    return render_template(
        "datos.html",
        pedidos_db=pedidos_db,
        pedidos_txt=pedidos_txt,
        pedidos_json=pedidos_json,
        pedidos_csv=pedidos_csv
    )

#>>>>>>>>>>>Ruta de admin para bd productos mysQl<<<<<<<<<<<<
#---Ruta de admin para consultar productos desde bd mysql---
@app.route("/admin/productos_bd")
def ver_productos_bd():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("admin/productos_bd.html", productos=productos)
#---Ruta para insertar registros de productos desde bd mysql---
@app.route("/admin/productos_bd/agregar", methods=["GET","POST"])
def agregar_producto_bd():

    if request.method == "POST":

        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        talla = request.form["talla"]
        color = request.form["color"]
        precio = request.form["precio"]
        stock = request.form["stock"]

        # IMAGEN
        imagen = ""

        archivo = request.files["imagen"]

        if archivo and archivo.filename != "":
           nombre_imagen = archivo.filename
           ruta = os.path.join("static/img", nombre_imagen)
           archivo.save(ruta)

           imagen = "img/" + nombre_imagen

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
        INSERT INTO productos(nombre,categoria,talla,color,precio,stock,imagen)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,(nombre,categoria,talla,color,precio,stock,imagen))

        conexion.commit()
        conexion.close()

        return redirect(url_for("ver_productos_bd"))

    return render_template("admin/agregar_producto_bd.html")

#---Ruta para eliminar registros de productos desde bd mysql---
@app.route("/admin/productos_bd/eliminar/<int:id_producto>")
def eliminar_producto_bd(id_producto):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM productos WHERE id_producto=%s",
        (id_producto,)
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(url_for("ver_productos_bd"))
#---Ruta para modificar registros de productos desde bd mysql---
@app.route("/admin/productos_bd/editar/<int:id_producto>", methods=["GET","POST"])
def editar_producto_bd(id_producto):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        talla = request.form["talla"]
        color = request.form["color"]
        precio = request.form["precio"]
        stock = request.form["stock"]

        cursor.execute("""
        UPDATE productos
        SET nombre=%s,categoria=%s,talla=%s,color=%s,precio=%s,stock=%s
        WHERE id_producto=%s
        """,(nombre,categoria,talla,color,precio,stock,id_producto))

        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect(url_for("ver_productos_bd"))

    cursor.execute(
        "SELECT * FROM productos WHERE id_producto=%s",
        (id_producto,)
    )

    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    return render_template(
        "admin/editar_producto_bd.html",
        producto=producto
    )
#----Ruta para mostrar usuarios en admi---
@app.route("/admin/usuarios")
def ver_usuarios():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT * FROM usuarios")  # Trae todos los usuarios
    usuarios = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    return render_template("admin/admin_usuarios.html", usuarios=usuarios)


# --- Página índice de usuario  ---
@app.route("/usuario")
def usuario():
    return render_template("usuario.html")
# --- Registro de usuarios ---
@app.route("/usuario/registro", methods=["GET", "POST"])
def registro_usuario():
    mensaje = ""
    if request.method == "POST":
        nombre = request.form.get("nombre")
        mail = request.form.get("mail")
        password = request.form.get("password")
        fecha_registro = request.form.get("fecha_registro")

        # Guardar en base de datos MySQL
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre, mail, password, fecha_registro) VALUES (%s,%s,%s,%s)",
            (nombre, mail, password, fecha_registro)
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        mensaje = "Usuario registrado correctamente"
        return redirect(url_for("login_usuario"))  # Redirige al login

    return render_template("registro_usuario.html", mensaje=mensaje)


# --- Login de usuarios ---
@app.route("/usuario/login", methods=["GET", "POST"])
def login_usuario():
    mensaje = ""
    if request.method == "POST":
        mail = request.form.get("mail")
        password = request.form.get("password")

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuarios WHERE mail=%s AND password=%s",
            (mail, password)
        )
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario:
            # Guardar usuario en session
            session["usuario"] = usuario["nombre"]
            return redirect(url_for("inicio"))  # o página de usuario
        else:
            mensaje = "Mail o contraseña incorrectos"

    return render_template("login_usuario.html", mensaje=mensaje)




if __name__ == "__main__":
    inventario = Inventario()

    with app.app_context():  
        inventario.crear_tabla(app)
        inventario.cargar_productos_desde_db()

    app.run(debug=True)