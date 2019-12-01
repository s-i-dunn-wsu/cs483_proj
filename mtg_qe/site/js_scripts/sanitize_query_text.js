// Samuel Dunn
// CS 483, Fall 2019

// This JS file supplied the `sanitizeText` method, which takes some string destined to be put into a query
// and returns the url & whoosh safe version of it.

function sanitizeText(text) {
    // Filter out any non-alphanumeric character
    // this regex replace should do the trick, however it is not unicode-aware.
    // maybe there's a lib that will convert characters to their closest ascii equivalent?
    sanitized = text.replace(/[^A-Za-z0-9 ]/g, ' ');
    console.log("Sanitized '" + text + "' to '" + sanitized + "'");
    return sanitized;
}