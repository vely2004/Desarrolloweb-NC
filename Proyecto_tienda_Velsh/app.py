from flask import Flask

app = Flask(__name__)

@app.route('/')
def inicio():
    return "Bienvenido a Tienda Online Velsh - Calzado Femenino exclusivo y moderno"

@app.route('/producto/<nombre>')
def producto(nombre):
    return f"Zapato modelo: {nombre} - Disponible en Tienda Velsh."

@app.route('/categoria/<tipo>')
def categoria(tipo):
    return f"Categoría: {tipo} - Descubre nuestra colección en Velsh."

@app.route('/ofertas')
def ofertas():
    return "🔥 Ofertas especiales: 20% de descuento en artículos seleccionados."

if __name__ == '__main__':
    app.run(debug=True)


