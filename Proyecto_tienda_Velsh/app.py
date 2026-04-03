import json
import csv
import os
import io

from flask import Flask, render_template, request, redirect, url_for, send_file
from datetime import timedelta
from form import PedidoForm
from inventario.bd import db, Cliente
from inventario.inventario import Inventario
from inventario.productos import Producto
from Conexion.conexion import obtener_conexion
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import Usuario, Producto
from services.producto_service import (
    obtener_productos,
    insertar_producto,
    obtener_producto_por_id,
    actualizar_producto,
    eliminar_producto
)
from fpdf import FPDF



#--- Inicializar app---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "super_secret_key"
app.permanent_session_lifetime = timedelta(minutes=15)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_usuario"
login_manager.login_message = "Debes iniciar sesión para acceder a esta página."

#inicar AQLAlchemy
db.init_app(app)



#--- Archivos para guardar pedidos---
txt_file = "inventario/data/datos.txt"
json_file = "inventario/data/datos.json"
csv_file = "inventario/data/datos.csv"


    #--user loader para Flask-Login--
@login_manager.user_loader
def load_user(user_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()

    if usuario:
        return Usuario(
            usuario["id_usuario"],
            usuario["nombre"],
            usuario["mail"],
            usuario["password"],
            usuario["rol"]
        )
    return None

#/////////////////////Rutas>////////////////////////

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
#>>>>>>>>>>>>>>>>>Ruta ofertas<<<<<<<<<<<<<<<<<
@app.route('/ofertas')
def ofertas():
    return render_template("ofertas.html")

#>>>>>>>>>>>>Ruta pedido<<<<<<<<<<<<<
@app.route('/pedido', methods=['GET', 'POST'])
def pedido():
    form = PedidoForm()  # <-- formulario
    # ---- SESIÓN ACTIVA ----
    usuario_info = None
    if current_user.is_authenticated:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (current_user.id_usuario,))
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
@login_required
def ver_pedidos():
        if current_user.rol != "admin":
            return redirect(url_for("usuario"))

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM pedidos")
        pedidos = cursor.fetchall()

        cursor.close()
        conexion.close()

        return render_template("admin/admin_pedidos.html", pedidos=pedidos)

#---Modificar pedido---
@app.route('/admin/pedidos/editar/<int:id_pedido>', methods=['GET', 'POST'])
@login_required
def editar_pedido(id_pedido):
    if current_user.rol != "admin":
        return redirect(url_for("usuario"))
    
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
@login_required
def eliminar_pedido(id_pedido):

    if current_user.rol != "admin":
        return redirect(url_for("usuario"))

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
#<<<<<<<<<<<<<<Ruta administrador>>>>>>>>>>>
@app.route("/admin")
@login_required
def admin():
    if current_user.rol != "admin":
        return redirect(url_for("usuario"))

    productos = inventario.mostrar_productos()
    return render_template("admin.html", productos=productos)

# ---Ruta de admin para añadir productos---
@app.route("/admin/añadir", methods=["GET", "POST"])
@login_required
def admin_añadir():
    if current_user.rol != "admin":
        return redirect(url_for("usuario"))

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
@login_required
def admin_eliminar():
    if current_user.rol != "admin":
        return redirect(url_for("usuario"))

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
@login_required
def admin_actualizar():
    if current_user.rol != "admin":
        return redirect(url_for("usuario"))

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
@login_required
def admin_buscar():
    if current_user.rol != "admin":
        return redirect(url_for("usuario"))

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
@login_required
def admin_productos():
    if current_user.rol != "admin":
        return redirect(url_for("usuario"))

    productos = inventario.mostrar_productos()
    return render_template(
        "admin_productos.html",
        productos=productos
    )

#---Ruta de admin para mostrar datos de pedidos---
@app.route('/admin/datos')
@login_required
def mostrar_datos():
    if current_user.rol != "admin":
        return redirect(url_for("usuario"))

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
#<<<<<<<<<<<Ruta de reporte pdf>>>>>>>>>>
@app.route("/reporte_pdf")
@login_required
def reporte_pdf():
    productos = obtener_productos()  # Lista de tuplas o listas

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Reporte de Productos", 0, 1, "C")

    # Encabezado de la tabla
    pdf.set_font("Arial", "B", 12)
    col_widths = [20, 40, 30, 30, 30, 25, 25]  # anchos de columnas
    headers = ["ID", "Nombre", "Stock", "Precio", "Categoria", "Talla", "Color"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
    pdf.ln()

    pdf.set_font("Arial", "", 12)
    row_height = 6

    for fila in productos:
        id_producto = str(fila[0])
        nombre = str(fila[1])
        categoria = str(fila[2])
        talla = str(fila[3])
        color = str(fila[4] or '')
        precio = fila[5] or 0.0
        stock = fila[6] or 0

        try:
            precio_float = float(str(precio).replace(',', '.'))
        except ValueError:
            precio_float = 0.0

        # Calcular la altura máxima de la fila
        talla_lines = pdf.multi_cell(col_widths[5], row_height, talla, split_only=True)
        color_lines = pdf.multi_cell(col_widths[6], row_height, color, split_only=True)
        max_lines = max(len(talla_lines), len(color_lines))
        max_height = max_lines * row_height

        x = pdf.get_x()
        y = pdf.get_y()

        # Columnas normales
        pdf.cell(col_widths[0], max_height, id_producto, 1, 0, 'C')
        pdf.cell(col_widths[1], max_height, nombre, 1, 0, 'L')
        pdf.cell(col_widths[2], max_height, str(stock), 1, 0, 'C')
        pdf.cell(col_widths[3], max_height, f"${precio_float:.2f}", 1, 0, 'R')
        pdf.cell(col_widths[4], max_height, categoria, 1, 0, 'L')

        # Columna Talla
        pdf.set_xy(x + sum(col_widths[:5]), y)
        pdf.multi_cell(col_widths[5], row_height, talla, border=1, align='C')

        # Columna Color
        pdf.set_xy(x + sum(col_widths[:6]), y)
        pdf.multi_cell(col_widths[6], row_height, color, border=1, align='C')

        # Mover cursor a la siguiente fila
        pdf.set_xy(x, y + max_height)

    # Generar PDF en memoria
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_buffer = io.BytesIO(pdf_output)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="reporte_productos.pdf",
        mimetype="application/pdf"
    )
#>>>>>>>>>>>Ruta de admin para bd productos mysQl<<<<<<<<<<<<
#---Ruta de admin para consultar productos desde bd mysql---
#--Implementación del CRUD--
@app.route("/admin/productos_bd")
@login_required
def ver_productos_bd():
    if current_user.rol != "admin":
        return redirect(url_for("usuario"))

    productos_bd = obtener_productos()

    productos = []
    for p in productos_bd:
        producto = Producto(
            p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7]
        )
        productos.append(producto)

    return render_template("admin/productos_bd.html", productos=productos)
#---Ruta para insertar registros de productos desde bd mysql---
@app.route("/admin/productos_bd/agregar", methods=["GET","POST"])
@login_required
def agregar_producto_bd():

    if current_user.rol != "admin":
        return redirect(url_for("usuario"))

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

        insertar_producto(nombre,categoria,talla,color,precio,stock,imagen)

        return redirect(url_for("ver_productos_bd"))

    return render_template("admin/agregar_producto_bd.html")

#---Ruta para eliminar registros de productos desde bd mysql---
@app.route("/admin/productos_bd/eliminar/<int:id_producto>")
@login_required
def eliminar_producto_bd(id_producto):
    if current_user.rol != "admin":
        return redirect(url_for("usuario"))

    eliminar_producto(id_producto)

    return render_template("admin/eliminar_bd.html", id_producto=id_producto)
#---Ruta para modificar registros de productos desde bd mysql---
@app.route("/admin/productos_bd/editar/<int:id_producto>", methods=["GET","POST"])
@login_required
def editar_producto_bd(id_producto):

    if current_user.rol != "admin":
        return redirect(url_for("usuario"))


    if request.method == "POST":

        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        talla = request.form["talla"]
        color = request.form["color"]
        precio = request.form["precio"]
        stock = request.form["stock"]

        try:
            actualizar_producto(id_producto,nombre,categoria,talla,color,precio,stock)
            print("Producto actualizado correctamente")
            return redirect(url_for("ver_productos_bd"))
        except Exception as e:
            print("Error:", e)

    producto = obtener_producto_por_id(id_producto)

    return render_template(
        "admin/editar_producto_bd.html",
        producto=producto
    )
#----Ruta para mostrar usuarios en admin---
@app.route("/admin/usuarios")
@login_required
def ver_usuarios():
    if current_user.rol != "admin":
        return redirect(url_for("usuario"))

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM usuarios") 
    usuarios = cursor.fetchall()
    
    cursor.close()
    conexion.close()

    
    return render_template("admin/admin_usuarios.html", usuarios=usuarios)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>  Página índice de usuario  <<<<<<<<<<<<<<<<<<<<<<<<<<<
#---Ruta para usuario---
@app.route("/usuario")
@login_required
def usuario():
    return render_template("usuario.html")
# --- Registro de usuarios ---
@app.route("/usuario/registro", methods=["GET", "POST"])
def registro_usuario():
    mensaje = ""
    if request.method == "POST":
        nombre = request.form.get("nombre").strip()
        mail = request.form.get("mail").strip().lower()
        password = request.form.get("password").strip()
        
        fecha_registro = request.form.get("fecha_registro")

        
        
        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        

        # Guardar en base de datos MySQL
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE mail = %s", (mail,))
        usuario_existente = cursor.fetchone()
        if usuario_existente:
            cursor.close()
            conexion.close()
            mensaje = "El correo electrónico ya está registrado"
            return render_template("registro_usuario.html", mensaje=mensaje)
        
        cursor.execute(
            "INSERT INTO usuarios (nombre, mail, password, fecha_registro, rol) VALUES (%s,%s,%s,%s,%s)",
              (nombre, mail, password_hash, fecha_registro, "usuario")
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
        mail = request.form.get("mail").strip().lower()
        password = request.form.get("password").strip()
    
        print("PASSWORD LOGIN:", repr(password))
        print("MAIL INGRESADO:", repr(mail))

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE mail = %s", (mail,))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario:
            password_hash_db = usuario["password"].strip()
            print("HASH GUARDADO:", repr(password_hash_db))

            resultado_check = check_password_hash(password_hash_db, password)
            
            if resultado_check:
                user = Usuario(
                    usuario["id_usuario"],
                    usuario["nombre"],
                    usuario["mail"],
                    usuario["password"],
                    usuario["rol"]
                )

                login_user(user)

                if user.rol == "admin":
                    return redirect(url_for("admin"))

                return redirect(url_for("usuario"))
            else:
                mensaje = "Mail o contraseña incorrectos"
        else:
            mensaje = "Mail o contraseña incorrectos"

    return render_template("login_usuario.html", mensaje=mensaje)

#---Logout de usuario---
@app.route("/usuario/logout")
@login_required
def logout_usuario():
    logout_user()
    return redirect(url_for("login_usuario"))

if __name__ == "__main__":
    inventario = Inventario()

    with app.app_context():  
        inventario.crear_tabla(app)
        inventario.cargar_productos_desde_db()

    app.run(debug=True)