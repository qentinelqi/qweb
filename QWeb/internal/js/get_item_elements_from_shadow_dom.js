// get_item_elements_from_shadow_dom.js
// Item matches from light DOM and from shadow roots.
// Shadow nodes are not returned to the driver. They stay in the page as handles.
// Assumes recursiveWalk (get_recursive_walk.js) is defined in the context.

function qwebHold(node) {
    if (!window.__qwebHeld) {
        window.__qwebHeld = [];
    }
    var bag = window.__qwebHeld;
    if (bag.length > 200) {
        for (var i = 0; i < bag.length; i++) {
            if (bag[i] && bag[i].isConnected === false) {
                bag[i] = null;
            }
        }
    }
    for (var held = bag.length - 1; held >= 0; held--) {
        if (bag[held] === node) {
            return held;
        }
    }
    bag.push(node);
    return bag.length - 1;
}

function itemAttrHit(node, text, partial) {
    var attrs = node.attributes;
    if (!attrs) {
        return false;
    }
    var wanted = String(text);
    for (var j = 0; j < attrs.length; j++) {
        var value = (attrs[j].value || "").trim();
        if (value === wanted) {
            return true;
        }
        if (partial && value.indexOf(wanted) !== -1) {
            return true;
        }
    }
    return false;
}

function find_item_elements_from_shadow_dom(tag, text, partial) {
    var supported = tag === null || tag === undefined
        ? ["A", "SPAN", "IMG", "LI", "H1", "H2", "H3", "H4", "H5", "H6", "DIV", "SVG", "P", "BUTTON", "INPUT", "TEXTAREA"]
        : [String(tag).toUpperCase()];
    var nodes = [];
    var order = [];
    recursiveWalk(document.body, function (node) {
        if (!node || !node.tagName || supported.indexOf(node.tagName) === -1) {
            return;
        }
        if (!itemAttrHit(node, text, partial)) {
            return;
        }
        var root = node.getRootNode ? node.getRootNode() : document;
        if (root === document) {
            return;
        }
        order.push("m" + qwebHold(node));
    });
    return {nodes: nodes, order: order};
}

// Entrypoint for Selenium execute_script
return find_item_elements_from_shadow_dom(arguments[0], arguments[1], arguments[2]);
