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



