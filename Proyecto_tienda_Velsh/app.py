from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
import sqlite3
import os
app = Flask(__name__)
app.secret_key = "super_secret_key"
app.permanent_session_lifetime = timedelta(minutes=15)
# Ruta de inicio
@app.route('/')
def inicio():
    productos = inventario.mostrar_productos()
    return render_template("index.html", productos=productos)

# Rutas por categorías 
@app.route('/categoria/<tipo>')
def categoria(tipo):
    # Filtrar productos según la categoría (insensible a mayúsculas)
    productos_categoria = [
        p for p in inventario.productos.values()
        if p.categoria and p.categoria.lower() == tipo.lower()
    ]

    # Diccionario para mapear tipo → plantilla
    plantillas = {
        "deportivos": "deportivos.html",
        "elegantes": "elegantes.html",
        "botas": "botas.html",
        "mocasines": "mocasines.html"
    }

    if tipo.lower() in plantillas:
        return render_template(plantillas[tipo.lower()], productos_categoria=productos_categoria)
    else:
        return "Categoría no encontrada", 404
#otras rutas    
@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/ofertas')
def ofertas():
    return render_template("ofertas.html")

@app.route('/pedido', methods=['GET', 'POST'])
def pedido():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        celular = request.form['celular']
        direccion = request.form['direccion']
        producto = request.form['producto']

        # Guardar en base de datos
        conn = sqlite3.connect('inventario.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clientes (nombre, email, celular, direccion, producto)
            VALUES (?, ?, ?, ?, ?)
            ''', (nombre, email, celular, direccion, producto))
        conn.commit()
        conn.close()

        return render_template(
            "pedido_confirmado.html",
            nombre=nombre,
            producto=producto
        )
    return render_template("pedido.html")

@app.route('/contacto')
def contacto():
    return render_template("contacto.html")

# ---- Inicializar DB ----
def inicializar_db():
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id_producto TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT,
            talla INTEGER,
            color TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            email TEXT,
            celular TEXT,
            direccion TEXT,
            producto TEXT
        )
    """)
    conn.commit()
    conn.close()

#Clase producto
class Producto:
    def __init__(self, id_producto, nombre, cantidad, precio, categoria, talla, color,imagen):
        self.id_producto = id_producto
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio
        self.categoria = categoria
        self.talla = talla
        self.color = color
        self.imagen = imagen

    # actualizar cantidad administrador
    def actualizar_cantidad(self, nueva_cantidad):
        self.cantidad = nueva_cantidad

    def actualizar_precio(self, nuevo_precio):
        self.precio = nuevo_precio

    def actualizar_categoria(self, categoria):
        self.categoria = categoria

    def actualizar_talla(self, talla):
        self.talla = talla

    def actualizar_color(self, color):
        self.color = color

    def __str__(self):
        return f"ID: {self.id_producto}, Nombre: {self.nombre}, Cantidad: {self.cantidad}, Precio: ${self.precio:.2f}, Categoria: {self.categoria}, Talla: {self.talla}, Color: {self.color}, imagen: {self.imagen}"
    
# Clase Inventario usando diccionario y sqsl
class Inventario:
    def __init__(self):
        self.productos = {}
    
#Crear tabla productos
    def crear_tabla(self):
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                cantidad INTEGER,
                precio REAL,
                categoria TEXT,
                talla TEXT,
                color TEXT,
                imagen TEXT
            )
        """)

        conn.commit()
        conn.close()

    # --- Operaciones en memoria + DB ---
    def agregar_producto(self, producto):
        self.guardar_producto_db(producto) 
        self.productos[producto.id_producto] = producto

    def eliminar_producto(self, id_producto):
        if id_producto in self.productos:
            del self.productos[id_producto]
            self.eliminar_producto_db(id_producto)

    def actualizar_producto(self, id_producto, cantidad, precio, categoria, talla, color, imagen):
        if id_producto in self.productos:
            prod = self.productos[id_producto]
            if cantidad is not None: prod.actualizar_cantidad(cantidad)
            if precio is not None: prod.actualizar_precio(precio)
            if categoria is not None: prod.actualizar_categoria(categoria)
            if imagen is not None: prod.imagen = imagen
            if talla is not None: prod.actualizar_talla(talla)
            if color is not None: prod.actualizar_color(color)
            self.guardar_producto_db(prod)

    # --- CRUD SQLite ---
    def guardar_producto_db(self, producto):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, cantidad, precio, categoria, talla, color, imagen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            producto.nombre,
            producto.cantidad,
            producto.precio,
            producto.categoria,
            producto.talla,
            producto.color,
            producto.imagen
        ))
        conn.commit()
        producto.id_producto = cursor.lastrowid
        conn.close()

    def eliminar_producto_db(self, id_producto):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id_producto = ?", (id_producto,))
        conn.commit()
        conn.close()

    def cargar_productos_desde_db(self):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos")
        filas = cursor.fetchall()
        for fila in filas:
            prod = Producto(*fila)  
            self.productos[prod.id_producto] = prod
        conn.close()

    def actualizar_producto_db(self, id_producto, nombre, cantidad, precio, categoria, talla, color):
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE productos
            SET nombre = ?, cantidad = ?, precio = ?, categoria = ?, talla = ?, color = ?
            WHERE id_producto = ?
        """, (nombre, cantidad, precio, categoria, talla, color, id_producto))

        conn.commit()
        conn.close()

    # --- Búsqueda y mostrar ---
    def buscar_producto_db(self, nombre):
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM productos
            WHERE nombre LIKE ?
        """, ('%' + nombre + '%',))

        filas = cursor.fetchall()
        conn.close()

        productos_encontrados = []
        for fila in filas:
            prod = Producto(*fila)
            productos_encontrados.append(prod)

        return productos_encontrados
    
    def mostrar_productos(self):
        self.cargar_productos_desde_db()
        return self.productos.values()
    
# --- Seguridad ---
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
#conectar base de datos
def conectar_db():
    conn = sqlite3.connect("inventario.db")
    conn.row_factory = sqlite3.Row
    return conn

#Ruta sesion de administrador
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contraseña = request.form.get("contraseña")

        if seguridad.verificar(usuario, contraseña):
            session["admin"] = True   # 🔐 
            session.permanent = False  # Se cierra al cerrar navegador
            return redirect(url_for("admin"))
        else:
            return "Usuario o clave incorrectos"

    return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
#admin
@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Si no hay sesión activa, redirige al login
    if not session.get("admin"):
        return redirect(url_for("login"))

    # Si ya está logueado, muestra el panel
    productos = inventario.mostrar_productos()
    return render_template("admin.html", mostrar_login=False, productos=productos)
# Mostrar todos los productos
@app.route("/admin/mostrar")
def admin_mostrar():
    productos = inventario.mostrar_productos()
    return render_template("admin_productos.html", productos=productos)

# Añadir nuevos productos
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
        #creación de producto
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

         # Guardar ruta relativa para mostrar en HTML
        imagen = f"img/{archivo.filename}" 
    return render_template(
        "admin_añadir.html",
        mensaje=mensaje,
        productos=inventario.mostrar_productos()
        )

# Eliminar productos por ID
@app.route("/admin/eliminar", methods=["GET", "POST"])
def admin_eliminar():
    mensaje = ""
    if request.method == "POST":
        id_str = request.form.get("id_producto")
        if not id_str:
            mensaje = "Debes ingresar un ID"
        else:
            id_producto = int(id_str)

            if inventario.eliminar_producto_db(id_producto):
                mensaje = "Producto eliminado"
            else:
                mensaje = "ID no encontrado"

    return render_template(
        "admin_eliminar.html",
        mensaje=mensaje,
        productos=inventario.mostrar_productos()
    )
# Actualizar cantidad o precio( en este caso se actualizan todos los campos)
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

# Buscar productos por nombre
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
# Mostrar productos
@app.route("/admin/productos")
def admin_productos():
    productos = inventario.mostrar_productos()
    return render_template(
        "admin_productos.html",
        productos=productos
    )

if __name__ == "__main__":
    inventario = Inventario()
    inventario.crear_tabla()
    inventario.cargar_productos_desde_db()
    app.run(debug=True)