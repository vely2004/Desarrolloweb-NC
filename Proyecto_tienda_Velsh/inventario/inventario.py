from inventario.bd import db, ProductoDB
from inventario.productos import Producto

# Clase Inventario usando diccionario y sqsl
class Inventario:
    def __init__(self):
        self.productos = {}
    
#Crear tabla productos
    def crear_tabla(self, app):
        with app.app_context():
            db.create_all()  


    # --- Operaciones en memoria + DB ---
#>>>Agregar producto<<<
    def agregar_producto(self, producto):
        # Crear objeto ProductoDB para SQLAlchemy (no pasamos id)
        producto_db = ProductoDB(
            nombre=producto.nombre,
            cantidad=producto.cantidad,
            precio=producto.precio,
            categoria=producto.categoria,
            talla=producto.talla,
            color=producto.color,
            imagen=producto.imagen
        )
        db.session.add(producto_db)
        db.session.commit()  # SQLAlchemy asigna automáticamente un id

        # Actualizar el id en memoria
        producto.id_producto = producto_db.id

        # Guardar en diccionario
        self.productos[producto.id_producto] = producto

#>>>Actualizar producto<<<
    def actualizar_producto(self, id_producto, cantidad, precio, categoria, talla, color, imagen):
        # Actualizar en memoria
        if id_producto in self.productos:
            prod = self.productos[id_producto]
            if cantidad: prod.cantidad = cantidad
            if precio: prod.precio = precio
            if categoria: prod.categoria = categoria
            if talla: prod.talla = talla
            if color: prod.color = color
            if imagen: prod.imagen = imagen

        # Actualizar en DB
        producto_db = ProductoDB.query.get(id_producto)
        if producto_db:
            if cantidad: producto_db.cantidad = cantidad
            if precio: producto_db.precio = precio
            if categoria: producto_db.categoria = categoria
            if talla: producto_db.talla = talla
            if color: producto_db.color = color
            if imagen: producto_db.imagen = imagen
            db.session.commit()    
#>>>Eliminar producto<<<
    def eliminar_producto(self, id_producto):
        if id_producto in self.productos:
            del self.productos[id_producto]
        # Buscar en DB y eliminar
        producto_db = ProductoDB.query.get(id_producto)
        if producto_db:
            db.session.delete(producto_db)
            db.session.commit()   
#>>>Cargar productos desde DB<<<
    def cargar_productos_desde_db(self):
        from inventario.bd import ProductoDB
        productos_db = ProductoDB.query.all()
        for prod_db in productos_db:
            prod = Producto(
               id_producto=prod_db.id,
               nombre=prod_db.nombre,
               cantidad=prod_db.cantidad,
               precio=prod_db.precio,
               categoria=prod_db.categoria,
               talla=prod_db.talla,
               color=prod_db.color,
               imagen=prod_db.imagen
            )
            self.productos[prod.id_producto] = prod

    # --- Búsqueda y mostrar ---
    def buscar_producto_db(self, nombre):
        from inventario.bd import ProductoDB
        productos_db = ProductoDB.query.filter(ProductoDB.nombre.ilike(f"%{nombre}%")).all()
    
        productos_encontrados = []
        for prod_db in productos_db:
            prod = Producto(
                prod_db.id,
                prod_db.nombre,
                prod_db.cantidad,
                prod_db.precio,
                prod_db.categoria,
                prod_db.talla,
                prod_db.color,
                prod_db.imagen
            )
            productos_encontrados.append(prod)
        return productos_encontrados
     # --- Mostrar todos los productos en memoria ---

    def mostrar_productos(self):
        self.cargar_productos_desde_db()
        return self.productos.values()
