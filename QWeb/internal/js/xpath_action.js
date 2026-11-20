// xpath_action.js
// Evaluates an XPath in the page and clicks or types there.
// The matched node is not returned. ChromeDriver rejects some of these nodes
// with "stale element not found in the current frame".

var shownVisibility = true;
var shownOffset = true;
var shownViewport = false;

function xpathShown(el) {
    // Same rules as get_visible_elements_from_elements: css-visible, width when
    // on screen, and off-screen nodes stay unless InViewport is required.
    if (!el || el.nodeType !== 1) {
        return false;
    }
    if (!shownVisibility) {
        return true;
    }
    var style = window.getComputedStyle(el);
    var css = !!style && style.display !== "none" && style.visibility !== "hidden";
    if (!css) {
        return false;
    }
    var rect = el.getBoundingClientRect();
    var onscreen = rect.top >= 0 && rect.top < window.innerHeight &&
        rect.left >= 0 && rect.left < window.innerWidth;
    var offset = el.offsetWidth > 0 || rect.width > 0;
    // Same keep/drop result as get_visible_elements_from_elements.
    if (onscreen && shownOffset && !offset) {
        return false;
    }
    if (shownViewport && !onscreen) {
        return false;
    }
    return true;
}

function xpathBranches(expression) {
    var parts = [];
    var current = "";
    var paren = 0;
    var bracket = 0;
    var quote = "";
    for (var i = 0; i < expression.length; i++) {
        var ch = expression.charAt(i);
        if (quote) {
            current += ch;
            if (ch === quote) {
                quote = "";
            }
            continue;
        }
        if (ch === "'" || ch === '"') {
            quote = ch;
            current += ch;
            continue;
        }
        if (ch === "(") {
            paren++;
        } else if (ch === ")") {
            paren = Math.max(0, paren - 1);
        } else if (ch === "[") {
            bracket++;
        } else if (ch === "]") {
            bracket = Math.max(0, bracket - 1);
        } else if (ch === "|" && paren === 0 && bracket === 0) {
            if (current.trim()) {
                parts.push(current.trim());
            }
            current = "";
            continue;
        }
        current += ch;
    }
    if (current.trim()) {
        parts.push(current.trim());
    }
    return parts.length ? parts : [expression];
}

function xpathCollect(xpath) {
    var snapshot = document.evaluate(
        xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null
    );
    var nodes = [];
    for (var i = 0; i < snapshot.snapshotLength; i++) {
        var node = snapshot.snapshotItem(i);
        if (node && node.nodeType === 1 && xpathShown(node)) {
            nodes.push(node);
        }
    }
    return nodes;
}

function xpathMatches(xpath) {
    try {
        return xpathCollect(xpath);
    } catch (error) {
        var parts = xpathBranches(xpath);
        if (parts.length < 2) {
            throw error;
        }
        var nodes = [];
        for (var i = 0; i < parts.length; i++) {
            try {
                nodes = nodes.concat(xpathCollect(parts[i]));
            } catch (branchError) {
                continue;
            }
        }
        if (!nodes.length) {
            throw error;
        }
        return nodes;
    }
}

function xpathMark(el, highlight, color) {
    if (highlight !== "draw" && highlight !== "debug" && highlight !== "flash") {
        return;
    }
    var previous = el.style.border;
    el.style.border = "5px solid " + color;
    var wait = highlight === "flash" ? 300 : 2000;
    setTimeout(function () {
        el.style.border = highlight === "draw" ? "5px solid " + color : previous;
    }, wait);
}

function xpathInside(node, match) {
    var current = node;
    var guard = 0;
    while (current && guard++ < 40) {
        if (current === match) {
            return true;
        }
        if (current.parentElement) {
            current = current.parentElement;
            continue;
        }
        var root = current.getRootNode ? current.getRootNode() : null;
        current = root && root.host ? root.host : null;
    }
    return false;
}

function xpathBoxHit(root, x, y) {
    var nodes = root.querySelectorAll ? root.querySelectorAll("*") : [];
    var best = null;
    var bestArea = Infinity;
    for (var i = 0; i < nodes.length; i++) {
        var rect = nodes[i].getBoundingClientRect();
        var area = rect.width * rect.height;
        var covers = x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom;
        if (covers && area > 0 && area < bestArea) {
            best = nodes[i];
            bestArea = area;
        }
    }
    return best;
}

function xpathDeepest(x, y, start) {
    var target = start;
    var guard = 0;
    while (target && guard++ < 15) {
        var root = target.shadowRoot;
        if (!root) {
            break;
        }
        var inner = null;
        try {
            inner = root.elementFromPoint(x, y);
        } catch (error) {
            inner = null;
        }
        if (!inner || inner === target) {
            inner = xpathBoxHit(root, x, y);
        }
        if (!inner || inner === target) {
            break;
        }
        target = inner;
    }
    return target;
}

function xpathHitTarget(el) {
    // A driver click lands on the center of the matched box. The browser then
    // delivers it to the topmost descendant, including one inside a shadow root.
    el.scrollIntoView({block: "center", inline: "nearest"});
    var rect = el.getBoundingClientRect();
    var x = rect.left + rect.width / 2;
    var y = rect.top + rect.height / 2;
    var top = document.elementFromPoint(x, y) || el;
    var hit = xpathDeepest(x, y, top);
    if (hit && xpathInside(hit, el)) {
        return hit;
    }
    return xpathDeepest(x, y, el) || el;
}

function xpathQuote(text) {
    if (text.indexOf('"') === -1) {
        return '"' + text + '"';
    }
    if (text.indexOf("'") === -1) {
        return "'" + text + "'";
    }
    return "concat('" + text.split("'").join("', \"'\", '") + "')";
}

function xpathNearest(el, anchors) {
    var rect = el.getBoundingClientRect();
    var x = rect.left + rect.width / 2;
    var y = rect.top + rect.height / 2;
    var best = Infinity;
    for (var i = 0; i < anchors.length; i++) {
        var other = anchors[i].getBoundingClientRect();
        var dx = x - (other.left + other.width / 2);
        var dy = y - (other.top + other.height / 2);
        best = Math.min(best, dx * dx + dy * dy);
    }
    return best;
}

function xpathText(el) {
    var value = el.innerText || el.textContent || "";
    return String(value).replace(/\u00a0/g, " ").replace(/\s+/g, " ").trim();
}

function xpathSetValue(el, value) {
    var owner = el.tagName === "TEXTAREA" ? window.HTMLTextAreaElement : window.HTMLInputElement;
    var descriptor = owner ? Object.getOwnPropertyDescriptor(owner.prototype, "value") : null;
    if (descriptor && descriptor.set) {
        descriptor.set.call(el, value);
    } else {
        el.value = value;
    }
}

function xpathType(el, text) {
    el.focus();
    xpathSetValue(el, "");
    var current = "";
    for (var i = 0; i < text.length; i++) {
        var ch = text.charAt(i);
        current += ch;
        el.dispatchEvent(new KeyboardEvent("keydown", {key: ch, bubbles: true, cancelable: true}));
        xpathSetValue(el, current);
        el.dispatchEvent(new InputEvent("input", {
            bubbles: true,
            cancelable: true,
            data: ch,
            inputType: "insertText"
        }));
        el.dispatchEvent(new KeyboardEvent("keyup", {key: ch, bubbles: true, cancelable: true}));
    }
    el.dispatchEvent(new Event("change", {bubbles: true}));
    return el.value == null ? "" : String(el.value);
}

var kind = arguments[0];
shownVisibility = arguments[8] !== false;
shownOffset = arguments[9] !== false;
shownViewport = arguments[10] === true;
var xpath = arguments[1];
var index = arguments[2] || 0;
var typed = arguments[3] == null ? "" : String(arguments[3]);
var highlight = String(arguments[4] || "").toLowerCase();
var color = arguments[5] || "blue";
var sendTab = !!arguments[6];
var anchorText = String(arguments[7] || "");
var matches;
try {
    matches = xpathMatches(xpath);
} catch (error) {
    return false;
}
if (kind === "contains-text" || kind === "equals-text") {
    for (var t = 0; t < matches.length; t++) {
        var sample = xpathText(matches[t]);
        var same = kind === "equals-text" ? sample === typed : sample.indexOf(typed) !== -1;
        if (same) {
            xpathMark(matches[t], highlight, color);
            return highlight === "debug" ? "debug" : true;
        }
    }
    return false;
}
if (anchorText) {
    var anchorPlain = anchorText.replace(/\*/g, "").replace(/\s+/g, " ").trim();
    if (anchorPlain) {
        var anchorNodes = xpathCollect(
            "//*[normalize-space(translate(., '*', ''))=" + xpathQuote(anchorPlain) + "]"
        );
        if (!anchorNodes.length) {
            return false;
        }
        matches.sort(function (left, right) {
            return xpathNearest(left, anchorNodes) - xpathNearest(right, anchorNodes);
        });
        index = 0;
    }
}
if (!matches.length || index < 0 || index >= matches.length) {
    return false;
}
var match = matches[index];
xpathMark(match, highlight, color);
if (highlight === "debug") {
    return "debug";
}
if (kind === "exists") {
    return true;
}
if (kind === "focus") {
    match.focus();
    return true;
}
if (kind === "value") {
    return match.value == null ? "" : String(match.value);
}
if (kind === "tab") {
    match.dispatchEvent(new KeyboardEvent("keydown", {key: "Tab", keyCode: 9, bubbles: true}));
    return true;
}
if (kind === "text") {
    return xpathText(match);
}
if (kind === "type") {
    var value = xpathType(match, typed);
    if (sendTab) {
        match.dispatchEvent(new KeyboardEvent("keydown", {key: "Tab", bubbles: true}));
    }
    return value;
}
if (kind.indexOf("checkbox") === 0) {
    var box = match;
    var boxTag = (match.tagName || "").toLowerCase();
    var boxType = (match.getAttribute("type") || "").toLowerCase();
    var boxRole = (match.getAttribute("role") || "").toLowerCase();
    var isBox = (boxTag === "input" && boxType === "checkbox") || boxRole === "checkbox";
    if (!isBox && match.querySelector) {
        var nested = match.querySelector('input[type="checkbox"], [role="checkbox"]');
        if (nested) {
            box = nested;
        }
    }
    function boxChecked(node) {
        if (node.hasAttribute("aria-checked")) {
            return node.getAttribute("aria-checked") === "true";
        }
        return !!node.checked;
    }
    if (kind === "checkbox-exists") {
        return true;
    }
    if (kind === "checkbox-state") {
        return boxChecked(box);
    }
    if (kind === "checkbox-enabled") {
        return !box.disabled;
    }
    var wantOn = kind === "checkbox-on";
    if (boxChecked(box) !== wantOn) {
        var wrapping = box.closest ? box.closest("label") : null;
        if (wrapping) {
            wrapping.click();
        }
        if (boxChecked(box) !== wantOn) {
            box.click();
        }
    }
    return boxChecked(box) === wantOn;
}
function xpathChoiceControl(node) {
    var choiceType = (node.getAttribute("type") || "").toLowerCase();
    return node.tagName === "INPUT" && (choiceType === "radio" || choiceType === "checkbox");
}

function xpathChoiceLabel(node) {
    if (node.id) {
        var root = node.getRootNode ? node.getRootNode() : document;
        var scope = root && root.querySelector ? root : document;
        var escaped = window.CSS && CSS.escape ? CSS.escape(node.id) : node.id.replace(/"/g, '\\"');
        var found = scope.querySelector('label[for="' + escaped + '"]');
        if (found) {
            return found;
        }
    }
    var current = node;
    var guard = 0;
    while (current && guard++ < 6) {
        if ((current.tagName || "").toLowerCase() === "label") {
            return current;
        }
        if (current.parentElement) {
            current = current.parentElement;
            continue;
        }
        var hostRoot = current.getRootNode ? current.getRootNode() : null;
        current = hostRoot && hostRoot.host ? hostRoot.host : null;
    }
    return null;
}

function xpathChoiceCover(node) {
    var parent = node.parentElement;
    if (!parent) {
        return null;
    }
    var parentRect = parent.getBoundingClientRect();
    if (parentRect.width < 2 || parentRect.height < 2 || parentRect.width > 80 || parentRect.height > 80) {
        return null;
    }
    var cover = document.elementFromPoint(
        parentRect.left + parentRect.width / 2,
        parentRect.top + parentRect.height / 2
    );
    if (!cover || cover === node || !parent.contains(cover)) {
        return null;
    }
    return cover;
}

var choice = xpathChoiceControl(match);
var wasChecked = choice ? !!match.checked : null;
xpathHitTarget(match).click();
if (choice && wasChecked === false && !match.checked) {
    var choiceLabel = xpathChoiceLabel(match);
    if (choiceLabel) {
        choiceLabel.click();
    }
    if (!match.checked) {
        var choiceCover = xpathChoiceCover(match);
        if (choiceCover) {
            choiceCover.click();
        }
    }
}
return true;
