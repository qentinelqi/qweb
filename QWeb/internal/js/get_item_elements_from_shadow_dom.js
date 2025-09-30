// get_item_elements_from_shadow_dom.js
// Finds item elements in shadow DOM matching supported tags or a given tag
// Assumes recursiveWalk is defined in the context
function find_item_elements_from_shadow_dom(tag) {
    var results = [];
    var supported_tags = tag === null ? ["A", "SPAN", "IMG", "LI", "H1", "H2", "H3", "H4", "H5", "H6", "DIV", "SVG", "P", "BUTTON", "INPUT", "TEXTAREA"] : [tag.toUpperCase()];
    var elem = recursiveWalk(document.body, function(node) {
        if (supported_tags.includes(node.tagName)) {
            results.push(node);
        }
    });
    return results;
}
// Entrypoint for Selenium execute_script
return find_item_elements_from_shadow_dom(arguments[0], arguments[1]);
