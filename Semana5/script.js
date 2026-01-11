const imageUrlInput = document.getElementById("imageUrl");
const addImageBtn = document.getElementById("addImage");
const deleteImageBtn = document.getElementById("deleteImage");
const gallery = document.getElementById("gallery");

const defaultImages = [
    "assets/paisaje.jpg",
    "assets/paisaje2.jpg",
    "assets/paisaje-kat.jpg"
];

defaultImages.forEach(url => {
    const img = document.createElement("img");
    img.src = url;

    img.addEventListener("click", () => {
        selectImage(img);
    });

    gallery.appendChild(img);
});

let selectedImage = null;

// Agregar imagen
addImageBtn.addEventListener("click", () => {
    const url = imageUrlInput.value.trim();

    if (url === "") {
        alert("Por favor ingresa una URL válida.");
        return;
    }

    const img = document.createElement("img");
    img.src = url;

    img.addEventListener("click", () => {
        selectImage(img);
    });

    gallery.appendChild(img);
    imageUrlInput.value = "";
});

// Seleccionar imagen
function selectImage(img) {
    if (selectedImage) {
        selectedImage.classList.remove("selected");
    }
    selectedImage = img;
    selectedImage.classList.add("selected");
}

// Eliminar imagen seleccionada
deleteImageBtn.addEventListener("click", () => {
    if (selectedImage) {
        gallery.removeChild(selectedImage);
        selectedImage = null;
    } else {
        alert("No hay ninguna imagen seleccionada.");
    }
});

// Atajos de teclado
document.addEventListener("keydown", (event) => {
    if (event.key === "Delete") {
        if (selectedImage) {
            gallery.removeChild(selectedImage);
            selectedImage = null;
        }
    }

    if (event.key === "Enter") {
        addImageBtn.click();
    }
});
