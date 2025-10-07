// get_clickable_from_shadow_dom.js
// Finds clickable elements in shadow DOM matching the locator (full and partial matches)
// Assumes recursiveWalk (get_recursive_walk.js) is defined in the context
function find_clickable_from_shadow_dom(text, partial) {
    var results = [];
    var full = [];
    var parts = [];
    var clickable_types = ["button", "reset", "submit"];
    var elem = recursiveWalk(document.body, function(node) {
        try {
            if ((node.getAttribute('onclick')!=null) ||
               (node.getAttribute('href')!=null) ||
               (node.getAttribute('role')=='button') ||
               (clickable_types.includes(node.getAttribute('type')))) {
                var nodetext;
                if (node.tagName.toLowerCase() == "input" && node.type("radio")) {
                    nodetext = node.value;
                } else {
                    nodetext = node.innerText;
                }
                if(nodetext.trim() === text) {
                    full.push(node);
                } else if (partial && nodetext.trim().includes(text)) {
                    parts.push(node);
                }
            }
        } catch(ex) {}
    });
    results = full.concat(parts);
    return results;
}
// Entrypoint for Selenium execute_script
return find_clickable_from_shadow_dom(arguments[0], arguments[1]);
