const productos = [
    {
        nombre: "Laptop",
        precio: 850,
        descripcion: "Laptop para uso académico"
    },
    {
        nombre: "Mouse",
        precio: 15,
        descripcion: "Mouse inalámbrico ergonómico"
    },
    {
        nombre: "Teclado",
        precio: 25,
        descripcion: "Teclado mecánico retroiluminado"
    }
];

// Referencia al <ul>
const lista = document.getElementById("lista-productos");

// Función para crear el HTML de un producto (plantilla)
function crearProductoHTML(producto) {
    return `
        <li>
            <strong>${producto.nombre}</strong><br>
            Precio: $${producto.precio}<br>
            ${producto.descripcion}
        </li>
    `;
}

// Función para renderizar todos los productos
function renderizarProductos() {
    lista.innerHTML = ""; // Limpia la lista

    productos.forEach(producto => {
        lista.innerHTML += crearProductoHTML(producto);
    });
}

// Renderizar cuando carga la página
renderizarProductos();

// Botón para agregar nuevo producto
const botonAgregar = document.getElementById("btn-agregar");

botonAgregar.addEventListener("click", () => {

    const nombre = prompt("Ingrese el nombre del producto:");
    const precio = prompt("Ingrese el precio del producto:");
    const descripcion = prompt("Ingrese una descripción del producto:");

   
    if (nombre && precio && descripcion) {
        const nuevoProducto = {
            nombre: nombre,
            precio: precio,
            descripcion: descripcion
        };

        productos.push(nuevoProducto);
        renderizarProductos();
    } else {
        alert("Debes completar todos los datos.");
    }
});

