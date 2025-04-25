// Manejo de archivos
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('files');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }

    const addUrlButton = document.querySelector('button[onclick="agregarURL()"]');
    if (addUrlButton) {
        // Reemplazamos el onclick por un event listener
        addUrlButton.removeAttribute('onclick');
        addUrlButton.addEventListener('click', agregarURL);
    }
});

function handleFileSelect(e) {
    const fileLabel = document.querySelector('.file-name');
    const selectedFilesDiv = document.querySelector('.selected-files');
    const files = Array.from(this.files);
    
    if (files.length > 0) {
        fileLabel.textContent = `${files.length} archivo(s) seleccionado(s)`;
        
        // Mostrar lista de archivos
        selectedFilesDiv.innerHTML = files.map(file => `
            <div class="file-item">
                <span>${file.name}</span>
                <span class="remove-file" data-name="${file.name}">&times;</span>
            </div>
        `).join('');
        
        // Agregar eventos para remover archivos
        addRemoveFileListeners(e.target);
    } else {
        resetFileInput();
    }
}

function addRemoveFileListeners(fileInput) {
    document.querySelectorAll('.remove-file').forEach(button => {
        button.addEventListener('click', function() {
            removeFile(this, fileInput);
        });
    });
}

function removeFile(button, fileInput) {
    const fileName = button.dataset.name;
    const newFileList = new DataTransfer();
    
    Array.from(fileInput.files)
        .filter(file => file.name !== fileName)
        .forEach(file => newFileList.items.add(file));
    
    fileInput.files = newFileList.files;
    
    // Actualizar la interfaz
    if (fileInput.files.length === 0) {
        resetFileInput();
    } else {
        document.querySelector('.file-name').textContent = 
            `${fileInput.files.length} archivo(s) seleccionado(s)`;
        button.parentElement.remove();
    }
}

function resetFileInput() {
    document.querySelector('.file-name').textContent = 'Ningún archivo seleccionado';
    document.querySelector('.selected-files').innerHTML = '';
}

function agregarURL() {
    const container = document.getElementById('url-inputs');
    const newInput = document.createElement('div');
    newInput.className = 'url-input';
    newInput.innerHTML = `
        <input type="url" name="urls[]" placeholder="https://ejemplo.com/noticia" required>
        <button type="button" class="remove-url">&times;</button>
    `;
    
    // Agregar evento para remover URL
    const removeButton = newInput.querySelector('.remove-url');
    removeButton.addEventListener('click', function() {
        newInput.remove();
    });
    
    container.appendChild(newInput);
}

// Validación de formularios
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        if (this.id === 'file-form' && document.getElementById('files').files.length === 0) {
            e.preventDefault();
            alert('Por favor, seleccione al menos un archivo');
        }
        
        if (this.id === 'url-form' && document.querySelectorAll('[name="urls[]"]').length === 0) {
            e.preventDefault();
            alert('Por favor, ingrese al menos una URL');
        }
    });
});