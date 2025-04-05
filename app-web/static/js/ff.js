const buscarEstadoInput = document.getElementById('buscarEstado');
const tablast = document.querySelector('table');
const filast = tablast.querySelectorAll('tbody tr');

buscarEstadoInput.addEventListener('keyup', () => {
    const filtress = buscarEstadoInput.value.toLowerCase();

    const resultades = [];

    filast.forEach(filess => {
        const cedulass = filess.cells[3].textContent.toLowerCase();
        if (cedulass.includes(filtress)) {
            resultades.push(filess);
            filess.style.display = '';
        } else {
            filess.style.display = 'none';
        }
    });


    const tbody = tablast.querySelector('tbody');
    resultades.forEach(filess => {
        tbody.appendChild(filess);
    });
});

