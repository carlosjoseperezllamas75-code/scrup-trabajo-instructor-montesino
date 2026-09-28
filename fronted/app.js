const API_URL = 'http://127.0.0.1:5000';

// Cargar la lista general al iniciar index.html
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('tabla-baul')) {
        obtenerRegistros();
    }

    // Manejar el formulario de agregar registro
    const formAgregar = document.getElementById('form-agregar');
    if (formAgregar) {
        formAgregar.addEventListener('submit', agregarRegistro);
    }

    // Cargar datos en el formulario de edición si existe un ID en la URL
    const urlParams = new URLSearchParams(window.location.search);
    const idEdit = urlParams.get('id');
    if (idEdit && document.getElementById('form-editar')) {
        cargarRegistroParaEditar(idEdit);
        document.getElementById('form-editar').addEventListener('submit', (e) => actualizarRegistro(e, idEdit));
    }
});

// 1. Obtener todos los registros (GET)
function obtenerRegistros() {
    fetch(`${API_URL}/`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('tabla-baul');
            tbody.innerHTML = '';
            
            if (data.baul && data.baul.length > 0) {
                data.baul.forEach(item => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${item.id_baul}</td>
                            <td>${item.Plataforma}</td>
                            <td>${item.usuario}</td>
                            <td>••••••••</td>
                            <td>
                                <a href="edit.html?id=${item.id_baul}" class="btn-edit">Editar</a>
                                <button onclick="eliminarRegistro(${item.id_baul})" class="btn-delete">Eliminar</button>
                            </td>
                        </tr>
                    `;
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="5">No hay registros guardados.</td></tr>';
            }
        })
        .catch(err => console.error('Error al obtener registros:', err));
}

// 2. Agregar nuevo registro (POST)
function agregarRegistro(e) {
    e.preventDefault();
    
    const plataforma = document.getElementById('plataforma').value;
    const usuario = document.getElementById('usuario').value;
    const clave = document.getElementById('clave').value;

    fetch(`${API_URL}/registro/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plataforma, usuario, clave })
    })
    .then(res => res.json())
    .then(data => {
        if (data.mensaje === 'Registro agregado') {
            swal("¡Éxito!", "Registro guardado correctamente", "success")
                .then(() => window.location.href = 'index.html');
        } else {
            swal("Error", "No se pudo guardar el registro", "error");
        }
    })
    .catch(err => console.error('Error al agregar:', err));
}

// 3. Eliminar registro (DELETE)
function eliminarRegistro(id) {
    swal({
        title: "¿Estás seguro?",
        text: "Una vez eliminado, no podrás recuperar este registro",
        icon: "warning",
        buttons: true,
        dangerMode: true,
    })
    .then((willDelete) => {
        if (willDelete) {
            fetch(`${API_URL}/eliminar/${id}`, { method: 'DELETE' })
                .then(res => res.json())
                .then(data => {
                    if (data.mensaje === 'Eliminado') {
                        swal("Eliminado", "El registro ha sido borrado", "success");
                        obtenerRegistros();
                    } else {
                        swal("Error", "No se pudo eliminar el registro", "error");
                    }
                })
                .catch(err => console.error('Error al eliminar:', err));
        }
    });
}

// 4. Cargar datos individuales para editar (GET /id)
function cargarRegistroParaEditar(id) {
    fetch(`${API_URL}/consulta_individual/${id}`)
        .then(res => res.json())
        .then(data => {
            if (data.baul) {
                document.getElementById('plataforma').value = data.baul.Plataforma;
                document.getElementById('usuario').value = data.baul.usuario;
            }
        })
        .catch(err => console.error('Error al cargar datos:', err));
}

// 5. Modificar registro (PUT)
function modificar(id) {
    actualizarRegistro(event, id);
}

function actualizarRegistro(e, id) {
    if (e) e.preventDefault();

    const plataforma = document.getElementById('plataforma').value;
    const usuario = document.getElementById('usuario').value;
    const clave = document.getElementById('clave').value;

    fetch(`${API_URL}/actualizar/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plataforma, usuario, clave })
    })
    .then(response => {
        if (!response.ok) throw new Error(`Error: ${response.status}`);
        return response.json();
    })
    .then(response => {
        if (response.mensaje === "Error") {
            swal("Mensaje", "Error al actualizar el registro", "error");
        } else {
            swal("Éxito", "Registro actualizado exitosamente", "success")
                .then(() => location.href = "index.html");
        }
    })
    .catch(error => console.error('Error:', error));
}