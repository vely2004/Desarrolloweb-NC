from flask import Flask, render_template, request

app = Flask(__name__)

# Ruta de inicio
@app.route('/')
def inicio():
    return render_template("index.html")

# Rutas por categorías 
@app.route('/categoria/<tipo>')
def categoria(tipo):
    if tipo == "deportivos":
        return render_template("deportivos.html")
    elif tipo == "elegantes":
        return render_template("elegantes.html")
    elif tipo == "botas":
        return render_template("botas.html")
    elif tipo == "mocasines":
        return render_template("mocasines.html")
    else:
        return "Categoría no encontrada", 404
# Otras páginas
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

        return render_template(
            "pedido_confirmado.html",
            nombre=nombre,
            producto=producto
        )
    return render_template("pedido.html")

@app.route('/contacto')
def contacto():
    return render_template("contacto.html")

# Ruta
if __name__ == '__main__':
    app.run(debug=True)