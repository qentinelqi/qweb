// find_by_xpath.js
// Evaluates an XPath with document.evaluate.
// One argument: the XPath, evaluated from document.
// Two arguments: a context node, then the XPath.
//
// ChromeDriver rejects an entire find_elements result when any returned node
// fails its parent-chain check ("stale element not found in the current frame").
// Native XPath can include such a node. querySelectorAll stays on the tree
// ChromeDriver accepts, so matches are marked and read back that way.

var root = arguments.length > 1 ? arguments[0] : document;
var xpath = arguments.length > 1 ? arguments[1] : arguments[0];
var doc = root.nodeType === 9 ? root : (root.ownerDocument || document);

function connectedToDocument(node) {
    try {
        var current = node;
        while (current && current.parentNode) {
            current = current.parentNode;
        }
        while (current && current.host) {
            current = current.host;
            while (current && current.parentNode) {
                current = current.parentNode;
            }
        }
        return current === doc;
    } catch (error) {
        return false;
    }
}

var snapshot = doc.evaluate(xpath, root, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
var mark = "data-qweb-xpath";
var token = Math.random().toString(36).slice(2);
var marked = [];
for (var i = 0; i < snapshot.snapshotLength; i++) {
    var node = snapshot.snapshotItem(i);
    if (!node || node.nodeType !== 1 || !node.setAttribute) {
        continue;
    }
    try {
        node.setAttribute(mark, token);
        marked.push(node);
    } catch (error) {
        continue;
    }
}

var selected = doc.querySelectorAll('[' + mark + '="' + token + '"]');
for (var k = 0; k < marked.length; k++) {
    try {
        if (marked[k].getAttribute(mark) === token) {
            marked[k].removeAttribute(mark);
        }
    } catch (error) {
        continue;
    }
}

// querySelectorAll only sees nodes ChromeDriver can wrap. A snapshot that
// also contains a synthetic-shadow node has to keep that node too: returning
// only the wrappable ones drops the match the driver found, and returning the
// shadow node makes ChromeDriver reject the whole result. The shadow match
// stays in the page and comes back as a handle.
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
var nodes = [];
var order = [];
for (var n = 0; n < snapshot.snapshotLength; n++) {
    var candidate = snapshot.snapshotItem(n);
    if (!candidate || candidate.nodeType !== 1 || !connectedToDocument(candidate)) {
        continue;
    }
    var seen = -1;
    for (var s = 0; s < selected.length; s++) {
        if (selected[s] === candidate) {
            seen = s;
            break;
        }
    }
    if (seen !== -1) {
        order.push(nodes.length);
        nodes.push(candidate);
        continue;
    }
    order.push("m" + qwebHold(candidate));
}

// A frame inside a shadow tree cannot be switched to. Its document is still
// readable from this page, and the match stays here instead of being returned.
var absolute = xpath.charAt(0) === "/" || xpath.charAt(0) === "(";
if (absolute && !order.length) {
    var frameDocs = [];
    function shadowFrameDocs(node, inShadow) {
        if (!node || frameDocs.length > 8) {
            return;
        }
        if (node.nodeType === 1) {
            if (inShadow && (node.tagName === "IFRAME" || node.tagName === "FRAME")) {
                try {
                    if (node.contentDocument) {
                        frameDocs.push(node.contentDocument);
                    }
                } catch (ignore) {
                    // Another origin. The frame walker handles same-document frames.
                }
            }
            if (node.shadowRoot) {
                shadowFrameDocs(node.shadowRoot, true);
            }
        }
        var kids = node.children || [];
        for (var c = 0; c < kids.length; c++) {
            shadowFrameDocs(kids[c], inShadow);
        }
    }
    shadowFrameDocs(document.documentElement, false);
    for (var d = 0; d < frameDocs.length; d++) {
        try {
            var innerSnap = frameDocs[d].evaluate(
                xpath, frameDocs[d], null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null
            );
            for (var f = 0; f < innerSnap.snapshotLength; f++) {
                var innerNode = innerSnap.snapshotItem(f);
                if (!innerNode || innerNode.nodeType !== 1) {
                    continue;
                }
                order.push("m" + qwebHold(innerNode));
            }
        } catch (ignoreFrame) {
            continue;
        }
    }
}
return {nodes: nodes, order: order};
