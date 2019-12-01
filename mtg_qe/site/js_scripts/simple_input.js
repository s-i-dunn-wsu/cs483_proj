// Samuel Dunn
// CS 483, Fall 2019
// This file supplies an onload call for any page that displays the basic "simple query" input field.

// it is safe to assume that ./sanitize_query_text.js is loaded ahead of this script.
function applySimpleInputSanitizer() {
    var form = document.getElementById("searchForm");
    form.onsubmit = function() {
        // find and sanitize searchbar's value.
        var searchbar = document.getElementById('searchInput');
        searchbar.value = sanitizeText(searchbar.value);
    }
}