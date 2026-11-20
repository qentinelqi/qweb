// shadow_action.js
// Finds a visible match inside open or synthetic shadow roots and, when asked,
// clicks it there. The matched node is never returned: ChromeDriver rejects the
// whole result when a shadow node fails its parent-chain check.

var shownVisibility = true;
var shownOffset = true;
var shownViewport = false;

function shadowShown(el) {
    // Same rules as get_visible_elements_from_elements.
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

function shadowText(el) {
    try {
        var value = el.tagName === "INPUT" ? (el.value || "") : (el.innerText || "");
        return value.replace(/\u00a0/g, " ").replace(/\s+/g, " ").trim();
    } catch (error) {
        return "";
    }
}

function shadowOwnText(el) {
    var text = "";
    for (var i = 0; i < el.childNodes.length; i++) {
        if (el.childNodes[i].nodeType === 3) {
            text += el.childNodes[i].textContent;
        }
    }
    return text.replace(/\u00a0/g, " ").replace(/\s+/g, " ").trim();
}

function shadowClickable(el) {
    var tag = el.tagName.toLowerCase();
    var type = (el.getAttribute("type") || "").toLowerCase();
    var role = el.getAttribute("role");
    return tag === "button" || tag === "a" || tag === "label" ||
        type === "submit" || type === "button" || type === "reset" ||
        role === "button" || role === "tab" ||
        el.hasAttribute("href") || el.hasAttribute("ng-click") ||
        el.hasAttribute("data-ng-click") ||
        (tag === "li" && el.hasAttribute("data-value")) ||
        (tag === "input" && type === "radio");
}

function shadowItem(el, tagFilter) {
    var tag = el.tagName.toLowerCase();
    if (tagFilter) {
        return tag === tagFilter;
    }
    return tag === "a" || tag === "span" || tag === "img" || tag === "li" ||
        tag === "h1" || tag === "h2" || tag === "h3" || tag === "h4" ||
        tag === "h5" || tag === "h6" || tag === "div" || tag === "svg" ||
        tag === "p" || tag === "button" || tag === "input";
}

function shadowWalk(node, visit) {
    if (!node) {
        return;
    }
    if (node.nodeType === 1) {
        visit(node);
        if (node.shadowRoot) {
            shadowWalk(node.shadowRoot, visit);
        }
    }
    var kids = node.children || [];
    for (var i = 0; i < kids.length; i++) {
        shadowWalk(kids[i], visit);
    }
}

function shadowClickTarget(el) {
    // ClickText normally matches the clickable element, such as the anchor,
    // rather than the span that holds its label.
    var current = el;
    var guard = 0;
    while (current && guard++ < 15) {
        if (current.nodeType === 1 && shadowClickable(current)) {
            return current;
        }
        if (current.parentElement) {
            current = current.parentElement;
            continue;
        }
        var root = current.getRootNode ? current.getRootNode() : null;
        current = root && root.host ? root.host : null;
    }
    return el;
}

function shadowActivate(el, dbl) {
    var target = shadowClickTarget(el);
    if (!dbl) {
        target.click();
        return target;
    }
    var event = document.createEvent("MouseEvents");
    event.initEvent("dblclick", true, true);
    target.dispatchEvent(event);
    return target;
}

function shadowCenter(el) {
    var rect = el.getBoundingClientRect();
    return {x: rect.left + rect.width / 2, y: rect.top + rect.height / 2};
}

function shadowDistance(first, second) {
    var start = shadowCenter(first);
    var end = shadowCenter(second);
    var dx = start.x - end.x;
    var dy = start.y - end.y;
    return dx * dx + dy * dy;
}

function shadowHover(el) {
    var target = shadowClickTarget(el);
    target.scrollIntoView({block: "center", inline: "nearest"});
    var nodes = el === target ? [target] : [el, target];
    var names = ["pointerover", "mouseover", "mousemove", "mouseenter"];
    for (var i = 0; i < nodes.length; i++) {
        for (var n = 0; n < names.length; n++) {
            nodes[i].dispatchEvent(new MouseEvent(names[n], {
                bubbles: true,
                cancelable: true,
                view: window
            }));
        }
    }
}

function shadowCheckbox(el) {
    var tag = (el.tagName || "").toLowerCase();
    var type = (el.getAttribute("type") || "").toLowerCase();
    var role = (el.getAttribute("role") || "").toLowerCase();
    return (tag === "input" && type === "checkbox") || role === "checkbox";
}

function shadowChecked(el) {
    if (el.hasAttribute("aria-checked")) {
        return el.getAttribute("aria-checked") === "true";
    }
    return !!el.checked;
}

function shadowBoxFrom(label, boxes) {
    if (shadowCheckbox(label)) {
        return label;
    }
    var owner = label.closest ? label.closest("label") : null;
    if (owner) {
        var htmlFor = owner.getAttribute("for");
        if (htmlFor) {
            for (var i = 0; i < boxes.length; i++) {
                if (boxes[i].id === htmlFor) {
                    return boxes[i];
                }
            }
        }
        var nested = owner.querySelector('input[type="checkbox"], [role="checkbox"]');
        if (nested) {
            return nested;
        }
    }
    var node = label;
    var guard = 0;
    while (node && guard++ < 6) {
        if (shadowCheckbox(node)) {
            return node;
        }
        if (node.querySelectorAll) {
            var found = node.querySelectorAll('input[type="checkbox"], [role="checkbox"]');
            if (found.length === 1) {
                return found[0];
            }
        }
        if (node.parentElement) {
            node = node.parentElement;
            continue;
        }
        var root = node.getRootNode ? node.getRootNode() : null;
        node = root && root.host ? root.host : null;
    }
    var best = null;
    var bestDistance = Infinity;
    for (var b = 0; b < boxes.length; b++) {
        var distance = shadowDistance(label, boxes[b]);
        if (distance < bestDistance) {
            bestDistance = distance;
            best = boxes[b];
        }
    }
    return best;
}

function shadowCheckboxAct(kind, locator, partial, index, anchorText) {
    var exact = [];
    var loose = [];
    var boxes = [];
    var anchors = [];
    var wanted = locator.toLowerCase();
    shadowWalk(document.body, function (el) {
        if (!el || el.nodeType !== 1) {
            return;
        }
        if (shadowCheckbox(el)) {
            boxes.push(el);
        }
        if (!shadowShown(el)) {
            return;
        }
        var own = shadowOwnText(el);
        if (!own) {
            return;
        }
        if (anchorText && own === anchorText) {
            anchors.push(el);
        }
        if (own === locator) {
            exact.push(el);
        } else if (partial && own.length < 80 && own.toLowerCase().indexOf(wanted) !== -1) {
            loose.push(el);
        }
    });
    var labels = exact.length ? exact : loose;
    if (anchorText) {
        if (!anchors.length) {
            return false;
        }
        labels.sort(function (left, right) {
            var leftDistance = Infinity;
            var rightDistance = Infinity;
            for (var a = 0; a < anchors.length; a++) {
                leftDistance = Math.min(leftDistance, shadowDistance(left, anchors[a]));
                rightDistance = Math.min(rightDistance, shadowDistance(right, anchors[a]));
            }
            return leftDistance - rightDistance;
        });
    }
    if (!labels.length || index < 0 || index >= labels.length || !boxes.length) {
        return false;
    }
    var best = shadowBoxFrom(labels[index], boxes);
    if (!best) {
        return false;
    }
    if (kind === "checkbox-exists") {
        return true;
    }
    if (kind === "checkbox-state") {
        return shadowChecked(best);
    }
    if (kind === "checkbox-enabled") {
        return !best.disabled;
    }
    var wantOn = kind === "checkbox-on";
    if (shadowChecked(best) !== wantOn) {
        var wrapping = best.closest ? best.closest("label") : null;
        if (wrapping) {
            wrapping.click();
        }
        if (shadowChecked(best) !== wantOn) {
            best.click();
        }
    }
    return shadowChecked(best) === wantOn;
}

var kind = arguments[0];
shownVisibility = arguments[8] !== false;
shownOffset = arguments[9] !== false;
shownViewport = arguments[10] === true;
var locator = String(arguments[1] || "");
var index = arguments[2] || 0;
var partial = !!arguments[3];
var tagFilter = String(arguments[4] || "").toLowerCase();
var highlight = String(arguments[5] || "").toLowerCase();
var color = arguments[6] || "blue";
var anchorText = String(arguments[7] || "");
if (kind.indexOf("checkbox") === 0) {
    return shadowCheckboxAct(kind, locator, partial, index, anchorText);
}
var wanted = locator.toLowerCase();
var exact = [];
var loose = [];
var fuzzy = [];
var anchors = [];

function keep(list, el) {
    list.push(el);
}

shadowWalk(document.body, function (el) {
    if (!shadowShown(el)) {
        return;
    }
    var label = shadowText(el);
    var own = shadowOwnText(el);
    if (anchorText && (own === anchorText || (shadowClickable(el) && label === anchorText))) {
        anchors.push(el);
    }
    var itemKind = kind.indexOf("item") !== -1;
    if (itemKind) {
        if (!shadowItem(el, tagFilter)) {
            return;
        }
        var names = ["title", "alt", "data-tooltip", "tooltip", "aria-label", "data-icon"];
        for (var n = 0; n < names.length; n++) {
            var attr = (el.getAttribute(names[n]) || "").replace(/\s+/g, " ").trim();
            if (!attr) {
                continue;
            }
            if (attr === locator) {
                keep(exact, el);
                return;
            }
            if (attr.toLowerCase() === wanted) {
                keep(loose, el);
                return;
            }
            if (partial && attr.length < 80 && attr.toLowerCase().indexOf(wanted) !== -1) {
                keep(fuzzy, el);
                return;
            }
        }
        return;
    }
    if (shadowClickable(el) && label) {
        if (label === locator) {
            keep(exact, el);
        } else if (label.toLowerCase() === wanted) {
            keep(loose, el);
        } else if (partial && label.length < 80 && label.toLowerCase().indexOf(wanted) !== -1) {
            keep(fuzzy, el);
        }
    }
    if (kind.indexOf("text") !== -1 && own) {
        if (own === locator) {
            keep(exact, el);
        } else if (partial && own.length < 80 && own.toLowerCase().indexOf(wanted) !== -1) {
            keep(fuzzy, el);
        }
    }
    // TextMatch also accepts the value of button, submit, reset and checkbox inputs.
    // ContainingTextMatch does the same, except it leaves checkbox values out.
    if (kind.indexOf("text") !== -1 && (el.tagName || "").toLowerCase() === "input") {
        var inputType = (el.getAttribute("type") || "").toLowerCase();
        var valued = inputType === "button" || inputType === "reset" ||
            inputType === "submit" || inputType === "checkbox";
        var inputValue = String(el.value || "").replace(/\u00a0/g, " ").replace(/\s+/g, " ").trim();
        if (valued && inputValue) {
            if (inputValue === locator) {
                keep(exact, el);
            } else if (inputType !== "checkbox" && partial && inputValue.length < 80 &&
                inputValue.toLowerCase().indexOf(wanted) !== -1) {
                keep(fuzzy, el);
            }
        }
    }
});

var matches = exact.length ? exact : (loose.length ? loose : fuzzy);
if (kind.indexOf("click") !== -1) {
    var clicked = [];
    for (var c = 0; c < matches.length; c++) {
        var choice = shadowClickTarget(matches[c]);
        if (clicked.indexOf(choice) === -1) {
            clicked.push(choice);
        }
    }
    if (clicked.length) {
        matches = clicked;
    }
}
if (anchorText) {
    if (!anchors.length) {
        return false;
    }
    matches.sort(function (left, right) {
        var leftDistance = Infinity;
        var rightDistance = Infinity;
        for (var a = 0; a < anchors.length; a++) {
            leftDistance = Math.min(leftDistance, shadowDistance(left, anchors[a]));
            rightDistance = Math.min(rightDistance, shadowDistance(right, anchors[a]));
        }
        return leftDistance - rightDistance;
    });
    index = 0;
}
if (!matches.length || index < 0 || index >= matches.length) {
    return false;
}
var match = matches[index];
if (highlight === "draw" || highlight === "debug" || highlight === "flash") {
    var previous = match.style.border;
    match.style.border = "5px solid " + color;
    if (highlight === "flash") {
        setTimeout(function () { match.style.border = previous; }, 300);
    } else if (highlight === "debug") {
        setTimeout(function () { match.style.border = previous; }, 2000);
        return "debug";
    }
}
if (kind.indexOf("hover") === 0) {
    shadowHover(match);
    return true;
}
if (kind.indexOf("click") === -1) {
    return true;
}
shadowActivate(match, kind.indexOf("dblclick") === 0);
return true;
