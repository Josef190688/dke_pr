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

    // Event-Listener für Kontextmenü-Actions
    let showDepositButton = document.getElementById('show-deposit');
    showDepositButton.addEventListener("click", function (event) {
        alert("Action: " + this.textContent + "\nRow ID: " + selectedRowID);
    });
    let editPersonButton = document.getElementById('edit-person');
    editPersonButton.addEventListener("click", function (event) {
        alert("Action: " + this.textContent + "\nRow ID: " + selectedRowID);
    });
    let deletePersonButton = document.getElementById('delete-person');
    deletePersonButton.addEventListener("click", function (event) {
        fetch(`/persons/${selectedRowID}`, {
            method: 'DELETE',
        })
        .then(response => {
            console.log('hab einen response', response);
            if (response.status === 204) {
                window.location.href = "/index";
            } else if (response.status === 302) {
                // Weiterleitung empfangen
                let redirectUrl = response.headers.get('Location');
                console.log('status ist 302', redirectUrl)
                // Hier können Sie die gewünschte Aktion ausführen, z.B. zur neuen URL weiterleiten
                window.location.href = redirectUrl;
            } else {
                // Hier können Sie mit der normalen Antwort umgehen
                return response.text();
            }
        })
        .catch(error => {
            console.error('Fehler beim Löschen der Person:', error);
        });
        
    });
});
