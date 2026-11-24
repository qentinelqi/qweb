// get_css_elements_from_shadow_dom.js
// Finds elements matching a CSS selector in the search root and in every open
// shadow root under it. Each tree (document or shadow root) is queried on its own,
// so a selector can't cross a shadow boundary.
// Assumes recursiveWalk (get_recursive_walk.js) is defined in the context

function getCssElementsFromShadowDom(root, selector) {
    root = root || document;
    var trees = [root];
    recursiveWalk(root, function(node) {
        // shadow roots are DocumentFragments with a host element
        if (node !== root && node.nodeType === 11 && node.host) {
            trees.push(node);
        }
    });
    var results = [];
    for (var i = 0; i < trees.length; i++) {
        var found = trees[i].querySelectorAll(selector);
        for (var j = 0; j < found.length; j++) {
            results.push(found[j]);
        }
    }
    return results;
}

// Entrypoint for Selenium execute_script
return getCssElementsFromShadowDom(arguments[0], arguments[1]);
