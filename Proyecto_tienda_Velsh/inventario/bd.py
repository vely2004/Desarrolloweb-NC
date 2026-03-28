from flask_sqlalchemy import SQLAlchemy

# Inicializar SQLAlchemy
db = SQLAlchemy()  

# Definir modelos
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    producto = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Cliente {self.nombre}>"
    
class ProductoDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50))
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    imagen = db.Column(db.String(100))

    def __repr__(self):
        return f"<Producto {self.nombre}>"