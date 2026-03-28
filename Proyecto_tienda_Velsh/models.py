# models.py
from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, mail, password, rol):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.mail = mail
        self.password = password
        self.rol = rol

    def get_id(self):
        return str(self.id_usuario)
    
class Producto:
    def __init__(self, id, nombre, categoria, talla, color, precio, stock, imagen):
        self.id = id
        self.nombre = nombre
        self.categoria = categoria
        self.talla = talla
        self.color = color
        self.precio = precio
        self.stock = stock
        self.imagen = imagen