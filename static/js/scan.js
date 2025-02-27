$(document).ready(function () {
    $("#scanUrl").on("input", function () {
        let query = $(this).val().trim();
        if (query.length >= 3) {  
            $.ajax({
                url: "/buscar_activos",
                method: "GET",
                data: { q: query },
                success: function (data) {
                    let dataList = $("#activosList");
                    dataList.empty(); 
                    data.forEach(function (activo) {
                        dataList.append(`<option value="${activo.url}">`);
                    });
                },
                error: function (xhr, status, error) {
                    console.error("Error en la búsqueda de activos:", error);
                }
            });
        }
    });

    $("#scheduleSwitch").on("change", function() {
        if ($(this).is(":checked")) {
            $("#scheduleFields").removeClass("d-none");
        } else {
            $("#scheduleFields").addClass("d-none");
        }
    });

    $("#nuevoActivoSwitch").on("change", function() {
        if ($(this).is(":checked")) {
            $("#nuevoActivoFields").removeClass("d-none");
        } else {
            $("#nuevoActivoFields").addClass("d-none");
        }
    });

    $("#scanForm").on("submit", function (event) {
        event.preventDefault(); 

        let isScheduled = $("#scheduleSwitch").is(":checked");
        let fechaProgramada = isScheduled ? $("#datetimepicker").val() : "now";

        let formData = {
            target_url: $("#scanUrl").val(),
            strength: $("#ScanIntensity").val(),
            schedule: isScheduled,
            scanDateTime: fechaProgramada,
            nuevo_activo: $("#nuevoActivoSwitch").is(":checked"),
            responsable: $("#responsable").val(),
            emails: $("#emails").val(),
            tipo: $("#tipo").val(),
            periodicidad: $("#periodicidad").val()
        };

        $.ajax({
            url: "/programar_escaneo",
            method: "POST",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": csrf_token 
            },
            data: JSON.stringify(formData),
            success: function (response) {
                alert(response.success);
            },
            error: function (xhr, status, error) {
                alert(JSON.stringify(formData));
                console.error("Error al programar escaneo:", error);
            }
        });
    });
});