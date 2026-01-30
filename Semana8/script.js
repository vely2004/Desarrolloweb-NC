// VALIDACIÓN DEL FORMULARIO
// Escucha cuando se intenta enviar el formulario
document.getElementById("contactForm").addEventListener("submit", function (e) {
    
    e.preventDefault(); 

    // Obtener valores de los campos
    let nombre = document.getElementById("nombre").value.trim();
    let email = document.getElementById("email").value.trim();
    let celular =document.getElementById("celular").value.trim();
    let producto = document.getElementById("producto").value.trim();
    let direccion = document.getElementById("direccion").value.trim();

    let valido = true; 

    // Limpiar errores anteriores
    document.getElementById("errorNombre").textContent = "";
    document.getElementById("errorEmail").textContent = "";
    document.getElementById("errorCelular").textContent = "";
    document.getElementById("errorProducto").textContent = "";
    document.getElementById("errorDireccion").textContent = "";
    document.getElementById("formAlert").classList.add("d-none");

    // ==== VALIDACIONES ====

    if (nombre === "") {
        document.getElementById("errorNombre").textContent = "El nombre es obligatorio";
        valido = false;
    }

    if (email === "") {
        document.getElementById("errorEmail").textContent = "El correo es obligatorio";
        valido = false;
    } else if (!email.includes("@")) {
        document.getElementById("errorEmail").textContent = "Correo no válido";
        valido = false;
    }

    if (celular === "") {
        document.getElementById("errorCelular").textContent = "El celular es obligatorio";
        valido = false;
    }

    if (producto === "") {
        document.getElementById("errorProducto").textContent = "Indique el producto que desea";
        valido = false;
    }

    if (direccion === "") {
        document.getElementById("errorDireccion").textContent = "La dirección es obligatoria";
        valido = false;
    }

    // 🔴 Alerta general
    let alerta = document.getElementById("formAlert");

    if (!valido) {
        alerta.textContent = "⚠️ Por favor complete correctamente el formulario.";
        alerta.classList.remove("d-none");
    } else {
        alerta.textContent = "✅ Pedido enviado correctamente.";
        alerta.classList.remove("d-none");
        alerta.classList.replace("alert-danger", "alert-success");
    }

});
