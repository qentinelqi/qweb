// get_by_attributes.js
// Returns elements matching attribute value, with full and partial matches

function getByAttributes(elems, locator, partial) {
    var matches = {};
    var full = [];
    var part = [];
    for (var i = 0; i < elems.length; i++) {
        var attrs = elems[i].attributes;
        if (attrs == null) {
            continue;
        }
        for (var j = 0; j < attrs.length; j++) {
            if (attrs[j].value.trim() == locator) {
                full.push(elems[i]);
                break;
            } else if (partial && attrs[j].value.includes(locator)) {
                part.push(elems[i]);
                break;
            }
        }
    }
    matches = { full: full, partial: part };
    return matches;
}

// Entrypoint for Selenium execute_script
return getByAttributes(arguments[0], arguments[1], arguments[2]);
