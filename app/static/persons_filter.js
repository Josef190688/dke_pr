var highlightedCells = [];

// Filterfunktion für die Tabelle
function filterTable() {
    var input = document.getElementById("table-filter");
    var filter = input.value.toLowerCase();
    var filterTerms = filter.split(" ");
    var table = document.getElementById("my-table");
    var rows = table.getElementsByTagName("tr");

    // Entfernen der vorherigen Markierungen
    removeHighlight();

    for (var i = 0; i < rows.length; i++) {
        var cell2 = rows[i].getElementsByTagName("td")[1]; // Zweite Spalte
        var cell3 = rows[i].getElementsByTagName("td")[2]; // Dritte Spalte
        var cell4 = rows[i].getElementsByTagName("td")[3]; // Vierte Spalte

        if (cell2 && cell3 && cell4) {
            var text2 = cell2.innerText.toLowerCase();
            var text3 = cell3.innerText.toLowerCase();
            var text4 = cell4.innerText.toLowerCase();

            let isMatch = false;

            if (filter === "") {
                rows[i].style.display = "";
            } else {
                const cellsAndTermsToHighligt = new Map();
                for (const term of filterTerms) {
                    if (term !== "") {
                        var match2 = text2.indexOf(term) > -1;
                        var match3 = text3.indexOf(term) > -1;
                        var match4 = text4.indexOf(term) > -1;
                        if (!(match2 || match3 || match4)) {
                            isMatch = false;
                            break;
                        } else {
                            if (match2) {
                                cellsAndTermsToHighligt.set(cell2, term);
                                isMatch = true;
                            }
                            if (match3) {
                                cellsAndTermsToHighligt.set(cell3, term);
                                isMatch = true;
                            }
                            if (match4) {
                                cellsAndTermsToHighligt.set(cell4, term);
                                isMatch = true;
                            }
                        }
                    }
                };
                if (isMatch) {
                    rows[i].style.display = "";
                    cellsAndTermsToHighligt.forEach((value, key) => {
                        highlightMatch(key, value);
                    });
                } else {
                    rows[i].style.display = "none";
                }
            }
        }
    }
}

// Funktion zum Markieren der Übereinstimmung
function highlightMatch(cell, filterTerm) {
    var text = cell.innerHTML;
    var highlightedText = text.replace(
        new RegExp("(" + escapeRegExp(filterTerm) + ")", "gi"),
        "<mark>$1</mark>"
    );
    cell.innerHTML = highlightedText;
    highlightedCells.push(cell);
}

// Funktion zum Entfernen der Markierungen
function removeHighlight() {
    for (var i = 0; i < highlightedCells.length; i++) {
        var cell = highlightedCells[i];
        var text = cell.innerHTML;
        var unhighlightedText = text.replace(/<mark>/gi, "").replace(/<\/mark>/gi, "");
        cell.innerHTML = unhighlightedText;
    }
    highlightedCells = [];
}

// Hilfsfunktion zum Escapen von Sonderzeichen in einem regulären Ausdruck
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// Ereignislistener für die Eingabe im Texteingabefeld
var input = document.getElementById("table-filter");
input.addEventListener("input", filterTable);