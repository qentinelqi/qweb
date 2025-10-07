// get_all_frames_from_shadow_dom.js
// Finds all iframe and frame elements in shadow DOM
// Assumes recursiveWalk (get_recursive_walk.js) is defined in the context
function find_all_frames_from_shadow_dom() {
    var results = [];
    var elem = recursiveWalk(document.body, function(node) {
        if (node.tagName == "IFRAME" || node.tagName == "FRAME") {
            results.push(node);
        }
    });
    return results;
}
// Entrypoint for Selenium execute_script
return find_all_frames_from_shadow_dom(arguments[0]);
