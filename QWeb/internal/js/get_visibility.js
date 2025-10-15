// get_visibility.js
// Returns visibility info for a list of elements

function getVisibility(elems) {
    var elemObjects = [];
    for (var i = 0; i < elems.length; i++) {
        var rects = elems[i].getBoundingClientRect();
        var obj = {
            elem: elems[i],
            viewport: rects.top >= 0 && rects.top < window.innerHeight &&
                rects.left >= 0 && rects.left < window.innerWidth,
            css: getComputedStyle(elems[i]).display !== "none" &&
                getComputedStyle(elems[i]).visibility !== "hidden",
            offset: elems[i].offsetWidth > 0 || rects.width > 0
        };
        elemObjects.push(obj);
    }
    return elemObjects;
}

// Entrypoint for Selenium execute_script
return getVisibility(arguments[0]);
