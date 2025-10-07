// get_text_elements_from_shadow_dom.js
// Finds elements in shadow DOM whose textContent matches or includes the given text

// Assumes recursiveWalk (get_recursive_walk.js) is defined in the context
function find_text_from_shadow_dom(text, partial) {
    var results = [];
    var unsupported_tags = ["script", "#document-fragment"];
    var elem = recursiveWalk(document.body, function(node) {
        if (node.textContent && node.textContent.replace(/\u00a0/g, ' ').includes(text) && !unsupported_tags.includes(node.nodeName.toLowerCase())) {
            var nodetext = [].reduce.call(node.childNodes, function(a, b) { return a + (b.nodeType === 3 ? b.textContent.trim() : ''); }, '');
            nodetext = nodetext.replace(/\u00a0/g, ' ');
            if (nodetext == text) {
                results.push(node);
            } else if (partial && nodetext.includes(text)) {
                results.push(node);
            }
        } else if (node.placeholder === text || node.value === text) {
            results.push(node);
        }
    });
    return results;
}

// Entrypoint for Selenium execute_script
// This file expects recursiveWalk to be defined in the context
return find_text_from_shadow_dom(arguments[0], arguments[1]);
