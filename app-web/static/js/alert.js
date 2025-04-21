document.addEventListener("DOMContentLoaded", () => {
  const registroForm = $("#registroForm");
  const regist = document.getElementById("alert_regist");

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

  $("#registroExit").on("click", function () {
    Swal.fire({
      title: "¿Quién va a retirar el beneficio?",
      showCancelButton: true,
      confirmButtonText: "Titular",
      cancelButtonText: "Autorizado",
      reverseButtons: true,
    }).then((result) => {
      if (result.isConfirmed) {
        // Mostrar campos adicionales de merienda y observación para titular
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

          // Preguntar si desea agregar una observación
          Swal.fire({
            title: "¿Quieres agregar alguna observación?",
            showCancelButton: true,
            confirmButtonText: "Sí, agregar",
            cancelButtonText: "No agregar",
            reverseButtons: true,
          }).then((result) => {
            if (result.isConfirmed) {
              // Mostrar input para observación
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
            } else if (result.dismiss === Swal.DismissReason.cancel) {
              // Si no desea agregar observación, enviar formulario directamente
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
        // Flujo para autorizado
        const cedula = $("#cedula").val(); // Obtiene la cédula del titular desde un input
        fetch(`/obtener_autorizados?cedula=${cedula}`)
          .then((response) => response.json())
          .then((autorizados) => {
            if (autorizados.error) {
              Swal.fire({
                icon: "error",
                title: "Oops...",
                background: "#fff",
                color: "#000",
                text: autorizados.error,
                showCancelButton: true,
                confirmButtonText: "Asignar",
                cancelButtonText: "Cancelar",
                customClass: {
                  title: "swal-title",
                  text: "swal-text",
                },
              }).then((result) => {
                if (result.isConfirmed) {
                  // Mostrar campo para ingresar el nombre del autorizado
                  Swal.fire({
                    title: "Ingrese el Nombre del Autorizado:",
                    input: "text",
                    inputAttributes: {
                      autocapitalize: "off",
                      placeholder: "APELLIDO Y NOMBRE",
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
                      // Mostrar campo para ingresar la cédula del autorizado
                      Swal.fire({
                        title: "Ingrese la cédula del Autorizado:",
                        input: "number",
                        inputAttributes: {
                          autocapitalize: "off",
                          style: "width: 80%;",
                          maxlength: "8",
                        },
                        showCancelButton: true,
                        confirmButtonText: "Siguiente",
                        cancelButtonText: "Cancelar",
                        showLoaderOnConfirm: true,
                        customClass: {
                          validationMessage: "custom-validation-message", // Clase personalizada
                        },
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
                            // arreglarlo
                            Swal.showValidationMessage("La cédula debe tener máximo 8 dígitos");
                            return false;
                          }
                        },
                      }).then((result) => {
                        if (result.isConfirmed) {
                          // Mostrar campos adicionales de merienda y observación
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

                            // Preguntar si desea agregar una observación
                            Swal.fire({
                              title: "¿Quieres agregar alguna observación?",
                              showCancelButton: true,
                              confirmButtonText: "Sí, agregar",
                              cancelButtonText: "No agregar",
                              reverseButtons: true,
                            }).then((result) => {
                              if (result.isConfirmed) {
                                // Mostrar input para observación
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
                              } else if (result.dismiss === Swal.DismissReason.cancel) {
                                // Si no desea agregar observación, enviar formulario directamente
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
            } else {
              // Generar tabla si hay autorizados
              let tableHtml = `
                <table class="table custom-table table-striped table-responsive table-bordered" style="max-height: 300px; border-radius: 50px; overflow-y: auto; border-collapse: collapse" id="tabla1">
                  <thead style="background-color:rgb(136, 130, 130); color: #333; font-weight: bold;">
                    <tr >
                      <th scope="col" class="text-center">Cédula</th>
                      <th scope="col" class="text-center">Nombre</th>
                    </tr>
                  </thead>
                  <tbody>
              `;

              autorizados.forEach((autorizado) => {
                tableHtml += `
                  <tr>
                    <td>${autorizado.Cedula_autorizado}</td>
                    <td>${autorizado.Nombre_autorizado}</td>
                  </tr>
                `;
              });

              tableHtml += `
                  </tbody>
                </table>
              `;

              Swal.fire({
                title: "Autorizado",
                html: tableHtml,
                showCancelButton: true,
                confirmButtonText: "Entregar",
                cancelButtonText: "Cancelar",
                reverseButtons: true,
              }).then((result) => {
                if (result.isConfirmed) {
                  // Mostrar campos adicionales después de confirmar entrega
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

                    // Preguntar si desea agregar una observación
                    Swal.fire({
                      title: "¿Quieres agregar alguna observación?",
                      showCancelButton: true,
                      confirmButtonText: "Sí, agregar",
                      cancelButtonText: "No agregar",
                      reverseButtons: true,
                    }).then((result) => {
                      if (result.isConfirmed) {
                        // Mostrar input para observación
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
                      } else if (result.dismiss === Swal.DismissReason.cancel) {
                        // Si no desea agregar observación, enviar formulario directamente
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
          })
          .catch((error) => {
            Swal.fire({
              icon: "error",
              title: "Error",
              text: "No se pudo obtener la lista de autorizados.",
            });
          });
      }
    });
  });
});