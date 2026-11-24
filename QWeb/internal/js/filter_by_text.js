// filter_by_text.js
// Filters elements by visible text for css= locators with :has-text() / :text-is().
// Text is innerText, trimmed, with whitespace runs collapsed (same as locator.normalize_text).
// Matching is case-sensitive. "has-text" is a substring match, "text-is" an exact match.
// Innermost match wins: an element that contains another match is dropped.

function filterByText(elems, kind, text) {
    function normalize(value) {
        return (value || "").replace(/\s+/g, " ").trim();
    }
    var matches = [];
    for (var i = 0; i < elems.length; i++) {
        var elemText = normalize(elems[i].innerText);
        var ok = kind === "text-is" ? elemText === text : elemText.indexOf(text) !== -1;
        if (ok) {
            matches.push(elems[i]);
        }
    }
    var innermost = [];
    for (var j = 0; j < matches.length; j++) {
        var containsOther = false;
        for (var k = 0; k < matches.length; k++) {
            if (j !== k && matches[j].contains(matches[k])) {
                containsOther = true;
                break;
            }
        }
        if (!containsOther) {
            innermost.push(matches[j]);
        }
    }
    return innermost;
}

// Entrypoint for Selenium execute_script
return filterByText(arguments[0], arguments[1], arguments[2]);
