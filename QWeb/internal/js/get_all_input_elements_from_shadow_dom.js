// get_all_input_elements_from_shadow_dom.js
// Finds all input and textarea elements in shadow DOM
// Assumes recursiveWalk is defined in the context
function find_all_input_elements_from_shadow_dom() {
    var results = [];
    var elem = recursiveWalk(document.body, function(node) {
        if (node.tagName == "INPUT" || node.tagName == "TEXTAREA") {
            results.push(node);
        }
    });
    return results;
}
// Entrypoint for Selenium execute_script
return find_all_input_elements_from_shadow_dom(arguments[0]);
