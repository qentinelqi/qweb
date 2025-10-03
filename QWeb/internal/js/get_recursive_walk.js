// get_recursive_walk.js
// Defines recursiveWalk as a global function for traversing DOM and shadow DOM

function recursiveWalk(node, func) {
    var done = func(node);
    if (done) {
        return true;
    }
    if ('shadowRoot' in node && node.shadowRoot) {
        var done = recursiveWalk(node.shadowRoot, func);
        if (done) {
            return true;
        }
    }
    node = node.firstChild;
    while (node) {
        var done = recursiveWalk(node, func);
        if (done) {
            return true;
        }
        node = node.nextSibling;
    }
}
