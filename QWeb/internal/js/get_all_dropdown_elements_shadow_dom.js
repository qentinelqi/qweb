// get_all_dropdown_elements_from_shadow_dom.js
// Finds all select elements in shadow DOM
// Assumes recursiveWalk  (get_recursive_walk.js) is defined in the context
function find_all_select_elements_from_shadow_dom() {
    var results = [];
    var elem = recursiveWalk(document.body, function(node) {
        if (node.tagName == "SELECT") {
            results.push(node);
        }
    });
    return results;
}
// Entrypoint for Selenium execute_script
return find_all_select_elements_from_shadow_dom(arguments[0]);
