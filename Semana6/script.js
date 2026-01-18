const nombre = document.getElementById("nombre");
const correo = document.getElementById("correo");
const password = document.getElementById("password");
const confirmarPassword = document.getElementById("confirmarPassword");
const edad = document.getElementById("edad");
const btnEnviar = document.getElementById("btnEnviar");

function validarNombre() {
    if (nombre.value.length >= 3) {
        nombre.className = "valido";
        document.getElementById("errorNombre").textContent = "";
        return true;
    } else {
        nombre.className = "invalido";
        document.getElementById("errorNombre").textContent = "Debe tener al menos 3 caracteres";
        return false;
    }
}

function validarCorreo() {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (regex.test(correo.value)) {
        correo.className = "valido";
        document.getElementById("errorCorreo").textContent = "";
        return true;
    } else {
        correo.className = "invalido";
        document.getElementById("errorCorreo").textContent = "Correo no válido";
        return false;
    }
}

function validarPassword() {
    const regex = /^(?=.*\d)(?=.*[!@#$%^&*]).{8,}$/;
    if (regex.test(password.value)) {
        password.className = "valido";
        document.getElementById("errorPassword").textContent = "";
        return true;
    } else {
        password.className = "invalido";
        document.getElementById("errorPassword").textContent =
            "Mínimo 8 caracteres, un número y un carácter especial";
        return false;
    }
}

function validarConfirmacion() {
    if (password.value === confirmarPassword.value && confirmarPassword.value !== "") {
        confirmarPassword.className = "valido";
        document.getElementById("errorConfirmar").textContent = "";
        return true;
    } else {
        confirmarPassword.className = "invalido";
        document.getElementById("errorConfirmar").textContent = "Las contraseñas no coinciden";
        return false;
    }
}

function validarEdad() {
    if (edad.value >= 18) {
        edad.className = "valido";
        document.getElementById("errorEdad").textContent = "";
        return true;
    } else {
        edad.className = "invalido";
        document.getElementById("errorEdad").textContent = "Debes ser mayor de 18 años";
        return false;
    }
}

function validarFormulario() {
    if (
        validarNombre() &&
        validarCorreo() &&
        validarPassword() &&
        validarConfirmacion() &&
        validarEdad()
    ) {
        btnEnviar.disabled = false;
    } else {
        btnEnviar.disabled = true;
    }
}

nombre.addEventListener("input", validarFormulario);
correo.addEventListener("input", validarFormulario);
password.addEventListener("input", validarFormulario);
confirmarPassword.addEventListener("input", validarFormulario);
edad.addEventListener("input", validarFormulario);

document.getElementById("formulario").addEventListener("submit", function (e) {
    e.preventDefault();
    alert("Formulario validado correctamente ✅");
});
