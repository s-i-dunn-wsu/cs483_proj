// Samuel Dunn
// CS 483, Fall 2019
// This file supplies js functions for the advanced search page.
// It is safe to assume that ./sanitize_query_text.js is loaded ahead of time.

function applyAdvancedSanitizer() {
    var form = document.getElementById('primaryForm');

    form.onsubmit = function() {
        // roll through all input fields and change their values to the sanitized version of that value.
        var children = form.getElementsByTagName("input");
        for (child of children) {
            child.value = sanitizeText(child.value);
        }
    };
}