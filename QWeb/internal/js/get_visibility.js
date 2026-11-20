// get_visibility.js
// Returns visibility info for a list of elements.
// The elements themselves are not returned. ChromeDriver rejects the whole
// script result when one of them is a node it cannot wrap.

function getVisibility(elems) {
    var info = [];
    for (var i = 0; i < elems.length; i++) {
        var rects = elems[i].getBoundingClientRect();
        var style = getComputedStyle(elems[i]);
        var css = style.display !== "none" && style.visibility !== "hidden";
        var width = elems[i].offsetWidth > 0 || rects.width > 0;
        info.push({
            viewport: rects.top >= 0 && rects.top < window.innerHeight &&
                rects.left >= 0 && rects.left < window.innerWidth,
            css: css,
            offset: width
        });
    }
    return info;
}

// Entrypoint for Selenium execute_script
return getVisibility(arguments[0]);
