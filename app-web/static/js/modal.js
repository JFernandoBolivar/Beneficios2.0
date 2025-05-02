document.addEventListener("DOMContentLoaded", function () {
  const buscarCedulaInput = document.getElementById("buscarCedula");
  const buscarnombreInput2 = document.getElementById("buscarnombre2");
  const buscarUnidadFisicaInput = document.getElementById("buscarUnidadFisica");
  const buscarEntregaInput = document.getElementById("buscarEntrega");
  const buscarEstadoInput = document.getElementById("buscarEstado");

  function filtrarTabla() {
    const filtroCedula = buscarCedulaInput?.value.toLowerCase() || "";
    const filtronombre2 = buscarnombreInput2?.value.toLowerCase() || "";
    const filtroUnidadFisica = buscarUnidadFisicaInput?.value.toLowerCase() || "";
    const filtroEntrega = buscarEntregaInput?.value.toLowerCase() || "";
    const filtroEstado = buscarEstadoInput?.value.toLowerCase() || "";
    const tablas = document.querySelectorAll("table");

    tablas.forEach((tabla) => {
      const filas = tabla.querySelectorAll("tbody tr");

      filas.forEach((fila) => {
        const textoCedula = fila.cells[0]?.textContent.toLowerCase() || "";
        const textoNombre2 = fila.cells[1]?.textContent.toLowerCase() || "";
        const textoUnidadFisica = fila.cells[2]?.textContent.toLowerCase() || "";
        const textoEntrega = fila.cells[7]?.textContent.toLowerCase() || "";
        const textoEstado = fila.cells[3]?.textContent.toLowerCase() || "";

        // Divide el filtro de nombre en palabras y verifica si todas están presentes
        const palabrasNombre = filtronombre2.split(" ").filter((palabra) => palabra.trim() !== "");
        const coincideNombre = palabrasNombre.every((palabra) => textoNombre2.includes(palabra));

        if (
          (filtroCedula === "" || textoCedula.includes(filtroCedula)) &&
          (filtronombre2 === "" || coincideNombre) &&
          (filtroUnidadFisica === "" || textoUnidadFisica.includes(filtroUnidadFisica)) &&
          (filtroEntrega === "" || textoEntrega.includes(filtroEntrega)) &&
          (filtroEstado === "" || textoEstado.includes(filtroEstado))
        ) {
          fila.style.display = "";
        } else {
          fila.style.display = "none";
        }
      });
    });
  }

  buscarCedulaInput?.addEventListener("keyup", filtrarTabla);
  buscarnombreInput2?.addEventListener("keyup", filtrarTabla);
  buscarUnidadFisicaInput?.addEventListener("keyup", filtrarTabla);
  buscarEntregaInput?.addEventListener("keyup", filtrarTabla);
  buscarEstadoInput?.addEventListener("keyup", filtrarTabla);
});