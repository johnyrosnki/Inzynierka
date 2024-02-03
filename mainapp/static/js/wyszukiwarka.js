$(document).ready(function() {
    $("#searchInput").on("input", function() {
        var query = $(this).val();
        if (query.length >= 2) {
            $.ajax({
                type: 'GET',
                url: '{% url "wyszukiwarka" %}',
                data: {'query': query},
                success: function(data) {
                    displayResults(data);
                },
                error: function(error) {
                    console.log('Wystąpił błąd:', error);
                }
            });
        } else {
            $("#searchResults").empty();
        }
    });

    function displayResults(data) {
        $("#searchResults").empty();
        data.results.forEach(function(result) {
            var listItem = $("<li>").text(result.label);
            listItem.on("click", function() {
                window.location.href = result.url;
            });
            $("#searchResults").append(listItem);
        });
    }
});
function obslugaPodpowiedzi() {
    // Twoja istniejąca funkcja obsługująca podpowiedzi

    // Dodaj obsługę zdarzenia kliknięcia na podpowiedzi
    $('#id_podpowiedzi').on('click', 'li', function() {
        var imie = $(this).data('imie');
        var tytul = $(this).data('tytul');
        var rodzaj = $(this).data('rodzaj');

        if (rodzaj === 'autor') {
            // Przejdź do strony z listą książek danego autora
            var url = '/ksiazki_wedlug_autora/' + imie + '/';
            window.location.href = url;
        } else if (rodzaj === 'tytul') {
            // Przejdź do strony ze szczegółami danej książki
            var url = '/ksiazka_szczegoly/' + tytul + '/';
            window.location.href = url;
        }
    });
}

// Wywołanie funkcji

