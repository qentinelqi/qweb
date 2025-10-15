// get_clickable.js
// Finds clickable elements matching the locator (full and partial matches)

function getClickable(locator) {
    var full = [];
    var partial = [];
    var candidates = [];
    var text = "";
    var elems = document.querySelectorAll('button, a, label, *[type="submit"], *[type="button"], *[type="reset"], li[data-value], input[type="radio"], *[role="tab"], *[role="button"], *[ng-click], *[data-ng-click],[href]');
    for (var i = 0; i < elems.length; i++) {
        if (elems[i].tagName.toLowerCase() === 'input') {
            text = elems[i].value;
        } else {
            text = elems[i].innerText;
        }
        if (text.trim() === locator) {
            full.push(elems[i]);
        } else if (text.trim().toLowerCase() === locator.toLowerCase()) {
            partial.push(elems[i]);
        }
    }
    candidates = full.concat(partial);
    return candidates;
}

// Entrypoint for Selenium execute_script
return getClickable(arguments[0]);
