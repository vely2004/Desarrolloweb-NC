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
    