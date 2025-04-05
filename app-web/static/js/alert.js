document.addEventListener("DOMContentLoaded", () => {
  const exito = document.getElementById("registroExit");
  const regist = document.getElementById("alert_regist");
  const efects = document.getElementById("efects");
  const urlParams = new URLSearchParams(window.location.search);
  const erorfamily = urlParams.get("error_familiar");

  if (regist) {
    regist.addEventListener("click", (event) => {
      event.preventDefault();
      Swal.fire({
        icon: "error",
        title: "Oops...",
        background: "#fff",
        color: "#000",
        text: "El número de cédula ya se encuentra marcado como entregado.",
        customClass: {
          title: "swal-title",
          content: "swal-text",
        },
      });
    });
  }

  $(document).ready(function () {
    const registroForm = $("#registroForm");

    $("#registroExit").on("click", function () {
      Swal.fire({
        title: "¿Quién va a retirar el beneficio?",
        showCancelButton: true,
        confirmButtonText: "Titular",
        cancelButtonText: "Autorizado",
        reverseButtons: true,
      }).then((result) => {
        if (result.isConfirmed) {
          // Titular
          Swal.fire({
            title: "¿Recibirá la bolsa de meriendas?",
            showCancelButton: true,
            confirmButtonText: "Sí",
            cancelButtonText: "No",
            reverseButtons: true,
          }).then((result) => {
            const lunchValue = result.isConfirmed ? "1" : "0";
            $("<input>")
              .attr({
                type: "hidden",
                name: "lunch",
                value: lunchValue,
              })
              .appendTo(registroForm);

            Swal.fire({
              title: "¿Quieres agregar alguna observación?",
              showCancelButton: true,
              confirmButtonText: "Sí, agregar",
              cancelButtonText: "No agregar",
              reverseButtons: true,
              preConfirm: () => {
                Swal.fire({
                  title: "Ingrese la observación:",
                  input: "text",
                  inputAttributes: {
                    autocapitalize: "off",
                  },
                  showCancelButton: true,
                  confirmButtonText: "Registrar",
                  cancelButtonText: "Cancelar",
                  showLoaderOnConfirm: true,
                  preConfirm: (observacion) => {
                    if (observacion) {
                      $("<input>")
                        .attr({
                          type: "hidden",
                          name: "observacion",
                          value: observacion.toUpperCase(),
                        })
                        .appendTo(registroForm);
                    }
                    $("<input>")
                      .attr({
                        type: "hidden",
                        name: "entregado",
                        value: "1",
                      })
                      .appendTo(registroForm);
                    return true;
                  },
                }).then((result) => {
                  if (result.isConfirmed) {
                    registroForm.submit();
                  }
                });
              },
            }).then((result) => {
              if (result.dismiss === Swal.DismissReason.cancel) {
                $("<input>")
                  .attr({
                    type: "hidden",
                    name: "entregado",
                    value: "1",
                  })
                  .appendTo(registroForm);
                registroForm.submit();
              }
            });
          });
        } else if (result.dismiss === Swal.DismissReason.cancel) {
          // Autorizado
          Swal.fire({
            title: "Ingrese el Nombre del Autorizado:",
            input: "text",
            inputAttributes: {
              autocapitalize: "off",
              placeholder: "APELLIDO Y NOMBRE"
            },
            showCancelButton: true,
            confirmButtonText: "Siguiente",
            cancelButtonText: "Cancelar",
            showLoaderOnConfirm: true,
            preConfirm: (nombreFamiliar) => {
              if (nombreFamiliar) {
                $("<input>")
                  .attr({
                    type: "hidden",
                    name: "nombrefamiliar",
                    value: nombreFamiliar.toUpperCase(),
                  })
                  .appendTo(registroForm);
                return true;
              }
            },
          }).then((result) => {
            if (result.isConfirmed) {
              Swal.fire({
                title: "Ingrese la cédula del Autorizado:",
                input: "number",
                inputAttributes: {
                  autocapitalize: "off",
                  style: "width: 100%;",
                  maxlength: "8",
                },
                showCancelButton: true,
                confirmButtonText: "Siguiente",
                cancelButtonText: "Cancelar",
                showLoaderOnConfirm: true,
                preConfirm: (cedulaFamiliar) => {
                  if (cedulaFamiliar && cedulaFamiliar.length <= 8) {
                    $("<input>")
                      .attr({
                        type: "hidden",
                        name: "cedulafamiliar",
                        value: cedulaFamiliar,
                      })
                      .appendTo(registroForm);
                    return true;
                  } else {
                    Swal.showValidationMessage(
                      "La cédula debe tener máximo 8 dígitos"
                    );
                    return false;
                  }
                },
              }).then((result) => {
                if (result.isConfirmed) {
                  Swal.fire({
                    title: "¿Recibirá la bolsa de meriendas?",
                    showCancelButton: true,
                    confirmButtonText: "Sí",
                    cancelButtonText: "No",
                    reverseButtons: true,
                  }).then((result) => {
                    const lunchValue = result.isConfirmed ? "1" : "0";
                    $("<input>")
                      .attr({
                        type: "hidden",
                        name: "lunch",
                        value: lunchValue,
                      })
                      .appendTo(registroForm);

                    Swal.fire({
                      title: "¿Quieres agregar alguna observación?",
                      showCancelButton: true,
                      confirmButtonText: "Sí, agregar",
                      cancelButtonText: "No agregar",
                      reverseButtons: true,
                      preConfirm: () => {
                        Swal.fire({
                          title: "Ingrese la observación:",
                          input: "text",
                          inputAttributes: {
                            autocapitalize: "off",
                          },
                          showCancelButton: true,
                          confirmButtonText: "Registrar",
                          cancelButtonText: "Cancelar",
                          showLoaderOnConfirm: true,
                          preConfirm: (observacion) => {
                            if (observacion) {
                              $("<input>")
                                .attr({
                                  type: "hidden",
                                  name: "observacion",
                                  value: observacion.toUpperCase(),
                                })
                                .appendTo(registroForm);
                            }
                            $("<input>")
                              .attr({
                                type: "hidden",
                                name: "entregado",
                                value: "1",
                              })
                              .appendTo(registroForm);
                            return true;
                          },
                        }).then((result) => {
                          if (result.isConfirmed) {
                            registroForm.submit();
                          }
                        });
                      },
                    }).then((result) => {
                      if (result.dismiss === Swal.DismissReason.cancel) {
                        $("<input>")
                          .attr({
                            type: "hidden",
                            name: "entregado",
                            value: "1",
                          })
                          .appendTo(registroForm);
                        registroForm.submit();
                      }
                    });
                  });
                }
              });
            }
          });
        }
      });
    });
  });

  // Muestra alerta si la cédula del familiar ya está registrada
  if (erorfamily === "True") {
    Swal.fire({
      icon: "error",
      title: "Oops...",
      background: "#fff",
      color: "#000",
      text: "La cédula del familiar ya se encuentra registrada.",
      customClass: {
        title: "swal-title",
        content: "swal-text",
      },
    });
  }
});