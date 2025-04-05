document.addEventListener("DOMContentLoaded", function () {
  const buscarCedulaInput = document.getElementById("buscarCedula");
  const buscarCedulaInput2 = document.getElementById("buscarCedula2");
  const buscarUnidadFisicaInput = document.getElementById("buscarUnidadFisica");
  const buscarEntregaInput = document.getElementById("buscarEntrega");
  const buscarEstadoInput = document.getElementById("buscarEstado");

  function filtrarTabla() {
    const filtroCedula = buscarCedulaInput.value.toLowerCase();
    const filtroUnidadFisica = buscarUnidadFisicaInput.value.toLowerCase();
    const filtroEntrega = buscarEntregaInput
      ? buscarEntregaInput.value.toLowerCase()
      : "";
    const filtroEstado = buscarEstadoInput
      ? buscarEstadoInput.value.toLowerCase()
      : "";
    const tablas = document.querySelectorAll("table");

    tablas.forEach((tabla) => {
      const filas = tabla.querySelectorAll("tbody tr");

      filas.forEach((fila) => {
        const textoCedula = fila.cells[0].textContent.toLowerCase();
        const textoUnidadFisica = fila.cells[2].textContent.toLowerCase();
        const textoEntrega = fila.cells[5]
          ? fila.cells[5].textContent.toLowerCase()
          : "";
        const textoEstado = fila.cells[3].textContent.toLowerCase();

        if (
          (filtroCedula === "" || textoCedula.includes(filtroCedula)) &&
          (filtroUnidadFisica === "" ||
            textoUnidadFisica.includes(filtroUnidadFisica)) &&
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

  buscarCedulaInput.addEventListener("keyup", filtrarTabla);
  buscarUnidadFisicaInput.addEventListener("keyup", filtrarTabla);
  if (buscarEntregaInput) {
    buscarEntregaInput.addEventListener("keyup", filtrarTabla);
  }
  if (buscarEstadoInput) {
    buscarEstadoInput.addEventListener("keyup", filtrarTabla);
  }
});
