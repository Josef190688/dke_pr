// Kontextmenü und Hover-Verhalten für Tabellen implementieren
document.addEventListener("DOMContentLoaded", function () {
    let selectedRowID = null;
    let rows = document.querySelectorAll(".table-hover tbody tr");
    let contextMenu = document.getElementById('context-menu');

    rows.forEach(function (row) {
        row.addEventListener("click", function (event) {
            let id = this.getAttribute("data-row-id");
            if (id === selectedRowID) {
                selectedRowID = null;
                contextMenu.style.display = 'none';
                rows.forEach(function (row) {
                    row.classList.remove("active");
                });
            } else {
                selectedRowID = id;
                let buttonBoundaries = document.getElementById("context-menu-button").getBoundingClientRect();
                contextMenu.style.display = 'block';
                contextMenu.style.left = event.pageX - buttonBoundaries.left + window.pageXOffset + 'px';
                contextMenu.style.top = event.pageY - buttonBoundaries.top - window.pageYOffset + 'px';
                rows.forEach(function (row) {
                    row.classList.remove("active");
                });
                this.classList.add("active");

                // Löschen deaktivieren, wenn Depots vorhanden
                let deletePersonButton = document.getElementById('delete_person_button');
                if (deletePersonButton) {
                    let hasPositions = (this.getAttribute("data-has-positions") === "TRUE");
                    if (hasPositions) {
                        deletePersonButton.classList.add("disabled");
                    } else {
                        deletePersonButton.classList.remove("disabled");
                    }
                }
            }
        });
    });

    document.addEventListener("click", function (event) {
        let isClickedInsideRow = false;
        let target = event.target;
        while (target.parentNode) {
            if (target.matches(".table-hover tbody tr")) {
                isClickedInsideRow = true;
                break;
            }
            target = target.parentNode;
        }
        if (!isClickedInsideRow) {
            contextMenu.style.display = 'none';
            selectedRowID = null;
            rows.forEach(function (row) {
                row.classList.remove("active");
            });
        }
    });

    // Kontextemenü: Zur Depotübersicht
    let showDepositButton = document.getElementById('show-deposit');
    showDepositButton.addEventListener("click", function (event) {
        window.location.href = "/personen/" + selectedRowID + "/depots";
    });

    // Kontextmenü: Bearbeiten
    let editPersonButton = document.getElementById('edit-person');
    editPersonButton.addEventListener("click", function (event) {
        window.location.pathname = "/person_aktualisieren/" + selectedRowID;
    });

    // Kontextmenü: Löschen
    let deletePersonButton = document.getElementById('delete-person');
    deletePersonButton.addEventListener("click", function (event) {
        if (document.querySelector(`tr[data-row-id="${selectedRowID}"]`) && document.querySelector(`tr[data-row-id="${selectedRowID}"]`).getAttribute("data-has-positions") === "TRUE") {
            alert("Löschen nicht möglich, da die Personen noch Depots besitzt.");
        } else {
            let confirmDelete = confirm("Sind Sie sicher, dass Sie die Person löschen möchten?");
            if (confirmDelete) {
                fetch(`/api/personen/${selectedRowID}`, {
                    method: 'DELETE',
                })
                    .then(response => {
                        if (response.status === 204) {
                            window.location.href = "/index";
                        } else if (response.status === 302) {
                            let redirectUrl = response.headers.get('Location');
                            console.log('status ist 302', redirectUrl)
                            window.location.href = redirectUrl;
                        } else {
                            return response.text();
                        }
                    })
                    .catch(error => {
                        console.error('Fehler beim Löschen der Person:', error);
                    });
            }
        }
    });
});