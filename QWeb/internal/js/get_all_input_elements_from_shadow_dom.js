// get_all_input_elements_from_shadow_dom.js
// Finds input and textarea elements in the document tree (including shadow roots).
// Optional arguments[0]: input type filter (e.g. "file"). When set, only matching
// INPUT elements are returned (TEXTAREA has no type attribute and is omitted).
// Assumes recursiveWalk (get_recursive_walk.js) is defined in the context
function find_all_input_elements_from_shadow_dom(inputType) {
    var results = [];
    var typeFilter =
        inputType != null && inputType !== "" ? String(inputType).toLowerCase() : null;
    recursiveWalk(document.body, function(node) {
        if (node.tagName == "INPUT") {
            if (!typeFilter || (node.type && node.type.toLowerCase() === typeFilter)) {
                results.push(node);
            }
        } else if (node.tagName == "TEXTAREA" && !typeFilter) {
            results.push(node);
        }
    });
    return results;
}
// Entrypoint for Selenium execute_script
return find_all_input_elements_from_shadow_dom(arguments[0]);
