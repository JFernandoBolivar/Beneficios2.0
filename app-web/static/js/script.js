document.addEventListener("DOMContentLoaded", () => {
    const ver_datos = document.getElementById("ver_datos");
    const exit = document.getElementById("exit");
    const exit4 = document.getElementById("exit4");
    const exit2 = document.getElementById("exit2");
    const exit3 = document.getElementById("exit3");
    const exit_tabla_buttons = document.querySelectorAll('.exit_tabla');
    const next = document.getElementById("next");
    const next2 = document.getElementById("next2");
    const closes_buttons = document.querySelectorAll('#closes');
    const open = document.querySelectorAll('#downloadPDF1');

    if (exit) {
        exit.addEventListener("click", () => {
            const alertDiv = document.querySelector(".alert");
            if (alertDiv) {
                alertDiv.style.display = "none";
            }
        });
    }

    if (exit4) {
        button.addEventListener('click', () => {
            const content27 = document.querySelector(".excel2");
            if (content27) {
                content27.style.display = "none";
            }
        });
    };


    if (exit2) {
        exit2.addEventListener("click", () => {
            const select = document.querySelector(".container_data");
            if (select) {
                select.style.display = "none";
            }
        });
    }

    if (ver_datos) {
        ver_datos.addEventListener("click", () => {
            const content2 = document.querySelector(".container_data");
            if (content2) {
                content2.style.display = "flex";
            }
        });
    }

    exit_tabla_buttons.forEach(button => {
        button.addEventListener('click', () => {
            window.location.href = "/";
        });
    });

    open.forEach(button => {
        button.addEventListener('click', () => {
            const content27 = document.querySelector(".excel2");
            if (content27) {
                content27.style.display = "flex";
            }
        });
    });

    if (next) {
        next.addEventListener('click', () => {
            window.location.href = "/listado_no_registrado";
        });
    }
    if (next2) {
        next2.addEventListener('click', () => {
            window.location.href = "/listado";
        });
    }
    if (exit3) {
        exit3.addEventListener('click', () => {
            window.location.href = "/";
        });
    }

    closes_buttons.forEach(button => {
        button.addEventListener('click', () => {
            const containerTablas = document.querySelector(".container_tablas");
            if (containerTablas) {
                containerTablas.style.display = "none";
            }
        });
    });




});