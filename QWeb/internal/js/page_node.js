// page_node.js
// Keeps XPath matches that ChromeDriver cannot wrap. The nodes stay in the
// page; Python refers to them by a handle in window.__qwebHeld.

function pageBag() {
    if (!window.__qwebHeld) {
        window.__qwebHeld = [];
    }
    return window.__qwebHeld;
}

function pageHold(node) {
    // Drop nodes Lightning has already removed. A long session never reloads,
    // and keeping every old match pins those views in memory.
    var bag = pageBag();
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

function pageBranches(expression) {
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

function pageShown(el, flags) {
    // Same rules as get_visible_elements_from_elements.
    if (!el || el.nodeType !== 1) {
        return false;
    }
    if (!flags.visibility) {
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
    if (onscreen && flags.offset && !offset) {
        return false;
    }
    if (flags.viewport && !onscreen) {
        return false;
    }
    return true;
}

function pageParent(node) {
    if (!node) {
        return null;
    }
    if (node.parentElement) {
        return node.parentElement;
    }
    var root = node.getRootNode ? node.getRootNode() : null;
    return root && root.host ? root.host : null;
}

function pageChainHas(node, target) {
    var current = node;
    while (current) {
        if (current === target) {
            return true;
        }
        current = pageParent(current);
    }
    return false;
}

function pageHit(doc, x, y) {
    var hit = doc.elementFromPoint(x, y);
    var guard = 0;
    while (hit && hit.shadowRoot && guard < 10) {
        guard++;
        var inner = null;
        try {
            inner = hit.shadowRoot.elementFromPoint(x, y);
        } catch (error) {
            inner = null;
        }
        if (!inner || inner === hit) {
            break;
        }
        hit = inner;
    }
    return hit;
}

function pageScrollParents(el) {
    var parents = [];
    var node = pageParent(el);
    var doc = el.ownerDocument || document;
    while (node) {
        var view = node.ownerDocument && node.ownerDocument.defaultView;
        var style = view ? view.getComputedStyle(node) : null;
        var overflow = style ? style.overflowY + style.overflow : "";
        var canScroll = overflow.indexOf("auto") >= 0 || overflow.indexOf("scroll") >= 0;
        if (canScroll && node.scrollHeight > node.clientHeight + 1) {
            parents.push(node);
        }
        node = pageParent(node);
    }
    parents.push(doc.scrollingElement || doc.documentElement);
    return parents;
}

function pageNudge(el, delta) {
    // Positive delta scrolls content up. Use the container that actually moves
    // this node; a small inner scroller must not swallow the request.
    var parents = pageScrollParents(el);
    var best = null;
    var bestShift = 0;
    for (var i = 0; i < parents.length; i++) {
        var parent = parents[i];
        var beforeTop = el.getBoundingClientRect().top;
        var beforeScroll = parent.scrollTop;
        parent.scrollTop = beforeScroll + delta;
        var shift = beforeTop - el.getBoundingClientRect().top;
        parent.scrollTop = beforeScroll;
        var rightWay = delta > 0 ? shift > 1 : shift < -1;
        if (rightWay && Math.abs(shift) > Math.abs(bestShift)) {
            best = parent;
            bestShift = shift;
        }
    }
    if (!best) {
        return false;
    }
    best.scrollTop += delta;
    return true;
}

function pageBottomBar(el, view) {
    // The Save / Cancel bar is wide and sits in the lower part of the view.
    // The field in front of it can hang below the buttons, so probe that band
    // instead of only the field's center.
    var doc = el.ownerDocument || document;
    var rect = el.getBoundingClientRect();
    var best = null;
    var y = view.innerHeight - 2;
    while (y > view.innerHeight * 0.45) {
        var hit = pageHit(doc, Math.min(view.innerWidth / 2, Math.max(2, rect.left + 8)), y);
        if (hit && !pageChainHas(hit, el) && !pageChainHas(el, hit)) {
            var box = hit.getBoundingClientRect();
            var wide = box.width >= 60 && box.height >= 16 && box.height < view.innerHeight * 0.5;
            var low = box.bottom > view.innerHeight * 0.55;
            var overField = box.bottom > rect.top - 8 && box.top < rect.bottom + 24;
            if (wide && low && overField && (!best || box.width > best.width)) {
                best = box;
            }
        }
        y -= 24;
    }
    return best;
}

function pageTopBar(el, view) {
    // The record actions bar is wide and sticks to the top. A row just under
    // it can sit with its top edge behind those buttons.
    var doc = el.ownerDocument || document;
    var rect = el.getBoundingClientRect();
    var best = null;
    var wideEnough = Math.min(view.innerWidth * 0.45, 280);
    var y = 2;
    while (y < view.innerHeight * 0.45) {
        var hit = pageHit(doc, Math.min(view.innerWidth / 2, Math.max(2, rect.left + 8)), y);
        if (hit && !pageChainHas(hit, el) && !pageChainHas(el, hit)) {
            var box = hit.getBoundingClientRect();
            var wide = box.width >= wideEnough && box.height >= 16 &&
                box.height < view.innerHeight * 0.35;
            var high = box.top < view.innerHeight * 0.35 && box.bottom < view.innerHeight * 0.55;
            var overField = box.bottom > rect.top - 8 && box.top < rect.bottom;
            if (wide && high && overField && (!best || box.bottom > best.bottom)) {
                best = box;
            }
        }
        y += 24;
    }
    return best;
}

function pagePointClear(el) {
    var rect = el.getBoundingClientRect();
    var view = (el.ownerDocument && el.ownerDocument.defaultView) || window;
    var x = rect.left + rect.width / 2;
    var y = rect.top + rect.height / 2;
    if (x < 0 || y < 0 || x >= view.innerWidth || y >= view.innerHeight) {
        return false;
    }
    var hit = pageHit(el.ownerDocument || document, x, y);
    if (!hit) {
        return false;
    }
    return pageChainHas(hit, el) || pageChainHas(el, hit);
}

function pageUncover(el) {
    // The short scroll leaves the field under the Save bar, often with the
    // field's center below the buttons. That bar is at the bottom of the view,
    // so the field has to move up until its bottom edge clears the bar.
    var rect = el.getBoundingClientRect();
    var view = (el.ownerDocument && el.ownerDocument.defaultView) || window;
    var bar = pageBottomBar(el, view);
    if (bar && rect.bottom > bar.top - 12) {
        return pageNudge(el, Math.max(12, rect.bottom - bar.top + 12));
    }
    var topBar = pageTopBar(el, view);
    if (topBar && rect.top < topBar.bottom + 8) {
        return pageNudge(el, -Math.max(12, topBar.bottom + 12 - rect.top));
    }
    if (pagePointClear(el) && rect.top >= 0 && rect.bottom <= view.innerHeight) {
        return false;
    }
    if (rect.bottom > view.innerHeight - 1) {
        return pageNudge(el, rect.bottom - view.innerHeight + 12);
    }
    if (rect.top < 0) {
        return pageNudge(el, rect.top - 12);
    }
    var doc = el.ownerDocument || document;
    var x = Math.min(view.innerWidth - 1, Math.max(0, rect.left + rect.width / 2));
    var y = Math.min(view.innerHeight - 1, Math.max(0, rect.top + rect.height / 2));
    var hit = pageHit(doc, x, y);
    if (!hit || pageChainHas(hit, el) || pageChainHas(el, hit)) {
        return false;
    }
    var cover = hit.getBoundingClientRect();
    if ((cover.top + cover.bottom) / 2 < view.innerHeight / 2) {
        return pageNudge(el, -Math.max(12, cover.bottom - rect.top + 12));
    }
    return pageNudge(el, Math.max(12, rect.bottom - cover.top + 12));
}

function pageClickable(el) {
    var tag = (el.tagName || "").toLowerCase();
    var type = (el.getAttribute("type") || "").toLowerCase();
    var role = el.getAttribute("role");
    return tag === "button" || tag === "a" || tag === "label" ||
        type === "submit" || type === "button" || type === "reset" ||
        role === "button" || role === "tab" || el.hasAttribute("href");
}

function pageClickTarget(el) {
    // "Show actions for Contact Roles" is assistive text inside the icon button.
    // The click belongs on that button, which is the visible control.
    var current = el;
    var guard = 0;
    while (current && guard++ < 8) {
        if (current.nodeType === 1 && pageClickable(current)) {
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

function pageChoiceControl(el) {
    var type = (el.getAttribute("type") || "").toLowerCase();
    return (el.tagName || "").toLowerCase() === "input" && (type === "radio" || type === "checkbox");
}

function pageChoiceLabel(el) {
    if (el.id) {
        var root = el.getRootNode ? el.getRootNode() : document;
        var scope = root && root.querySelector ? root : document;
        var escaped = window.CSS && CSS.escape ? CSS.escape(el.id) : el.id.replace(/"/g, '\\"');
        var found = scope.querySelector('label[for="' + escaped + '"]');
        if (found) {
            return found;
        }
    }
    var current = el;
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

function pageChoiceCover(el) {
    // A hidden radio keeps a small parent whose center is the visible control.
    var parent = el.parentElement;
    if (!parent) {
        return null;
    }
    var rect = parent.getBoundingClientRect();
    if (rect.width < 2 || rect.height < 2 || rect.width > 80 || rect.height > 80) {
        return null;
    }
    var view = (el.ownerDocument && el.ownerDocument.defaultView) || window;
    var hit = view.document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
    if (!hit || hit === el || !parent.contains(hit)) {
        return null;
    }
    return hit;
}

function pageActionTarget(el) {
    if (!el || el.nodeType !== 1) {
        return el;
    }
    if (pageChoiceControl(el)) {
        return el;
    }
    var cls = typeof el.className === "string" ? el.className : "";
    var rect = el.getBoundingClientRect();
    var hiddenLabel = cls.indexOf("assistive-text") !== -1 || rect.width < 2 || rect.height < 2;
    if (!hiddenLabel) {
        return el;
    }
    return pageClickTarget(el);
}

function pageReveal(el) {
    if (!el || !el.scrollIntoView) {
        return;
    }
    try {
        el.scrollIntoView({block: "nearest", inline: "nearest"});
    } catch (ignoreScroll) {
        el.scrollIntoView(false);
    }
    for (var attempt = 0; attempt < 4; attempt++) {
        if (!pageUncover(el)) {
            break;
        }
    }
}

function pageCollect(xpath, flags, root) {
    var base = root && root.nodeType === 1 ? root : document;
    var snapshot = document.evaluate(
        xpath, base, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null
    );
    var nodes = [];
    for (var i = 0; i < snapshot.snapshotLength; i++) {
        var node = snapshot.snapshotItem(i);
        if (node && node.nodeType === 1 && pageShown(node, flags) && nodes.indexOf(node) === -1) {
            nodes.push(node);
        }
    }
    return nodes;
}

function pageMatches(xpath, flags, root) {
    try {
        return pageCollect(xpath, flags, root);
    } catch (error) {
        var parts = pageBranches(xpath);
        if (parts.length < 2) {
            throw error;
        }
        var nodes = [];
        var failed = null;
        for (var i = 0; i < parts.length; i++) {
            try {
                var branch = pageCollect(parts[i], flags, root);
                for (var j = 0; j < branch.length; j++) {
                    if (nodes.indexOf(branch[j]) === -1) {
                        nodes.push(branch[j]);
                    }
                }
            } catch (branchError) {
                failed = branchError;
            }
        }
        if (!nodes.length && failed) {
            throw failed;
        }
        return nodes;
    }
}

function pageListItems(start, listTag, direct) {
    // UseList locates a list by text inside it, then reads the rows.
    // closest() stays in the same tree, including a shadow root.
    var root = start;
    if (!direct) {
        var wanted = String(listTag || "ul").toLowerCase();
        var guard = 0;
        while (root && guard++ < 15) {
            if (root.nodeType === 1 && (root.tagName || "").toLowerCase() === wanted) {
                break;
            }
            if (root.parentElement) {
                root = root.parentElement;
                continue;
            }
            var hostRoot = root.getRootNode ? root.getRootNode() : null;
            root = hostRoot && hostRoot.host ? hostRoot.host : null;
        }
        if (!root || root.nodeType !== 1 || (root.tagName || "").toLowerCase() !== wanted) {
            return [];
        }
    }
    var selector = direct ? String(listTag || "*") : "li, dt, dd";
    var found = root.querySelectorAll ? root.querySelectorAll(selector) : [];
    var handles = [];
    for (var n = 0; n < found.length; n++) {
        handles.push(pageHold(found[n]));
    }
    return handles;
}

function pageNode(handle) {
    var el = pageBag()[handle];
    if (!el || (el.isConnected === false)) {
        return null;
    }
    return el;
}

function pagePin(el) {
    // The match comes first. Parents follow, for the case where ChromeDriver
    // can wrap the label but not the node the XPath actually hit.
    var tokens = [];
    var current = el;
    var guard = 0;
    while (current && current.nodeType === 1 && guard++ < 8) {
        var token = "q" + Math.random().toString(36).slice(2);
        var pinned = false;
        try {
            current.setAttribute("data-qweb-ref", token);
            if (document.querySelector('[data-qweb-ref="' + token + '"]') === current) {
                tokens.push(token);
                pinned = true;
            }
        } catch (error) {
            pinned = false;
        }
        if (!pinned) {
            try {
                current.removeAttribute("data-qweb-ref");
            } catch (ignore) {
                // The node rejected the attribute. Keep walking.
            }
        }
        if (current.parentElement) {
            current = current.parentElement;
            continue;
        }
        var root = current.getRootNode ? current.getRootNode() : null;
        current = root && root.host ? root.host : null;
    }
    return tokens;
}

var command = arguments[0];
var payload = arguments[1];
var extra = arguments[2];
var flags = arguments[3] || {visibility: true, offset: true, viewport: false};

if (command === "hold") {
    var matches;
    var holdRoot = extra && extra.nodeType === 1 ? extra : null;
    try {
        matches = pageMatches(String(payload || ""), flags, holdRoot);
    } catch (error) {
        throw new Error("qweb-invalid-xpath " + error.message);
    }
    var handles = [];
    for (var h = 0; h < matches.length; h++) {
        handles.push(pageHold(matches[h]));
    }
    return handles;
}

if (command === "export") {
    var exported;
    try {
        exported = pageMatches(String(payload || ""), flags);
    } catch (error) {
        throw new Error("qweb-invalid-xpath " + error.message);
    }
    var tokens = [];
    for (var t = 0; t < exported.length; t++) {
        var chain = pagePin(exported[t]);
        if (chain.length) {
            tokens.push(chain);
        }
    }
    return tokens;
}

if (command === "list-from") {
    var startNode = extra && extra.nodeType === 1 ? extra : null;
    if (!startNode) {
        return {handles: []};
    }
    return {handles: pageListItems(startNode, flags || "ul", payload === true)};
}

if (command === "export-from") {
    var fromRoot = extra && extra.nodeType === 1 ? extra : document;
    var fromFlags = {visibility: false, offset: false, viewport: false};
    var fromNodes;
    try {
        fromNodes = pageMatches(String(payload || ""), fromFlags, fromRoot);
    } catch (error) {
        throw new Error("qweb-invalid-xpath " + error.message);
    }
    var fromTokens = [];
    for (var f = 0; f < fromNodes.length; f++) {
        var fromToken = pagePin(fromNodes[f]);
        if (fromToken.length) {
            fromTokens.push(fromToken);
        }
    }
    return fromTokens;
}

var el = pageNode(payload);
if (!el) {
    return {error: "stale"};
}
if (command === "list-items") {
    return {handles: pageListItems(el, extra || "ul", flags === true)};
}
if (command === "text") {
    return {value: el.innerText || el.textContent || ""};
}
if (command === "tag") {
    return {value: (el.tagName || "").toLowerCase()};
}
if (command === "attr") {
    var name = String(extra || "");
    if (name === "innerText" || name === "textContent" || name === "innerHTML" || name === "outerHTML") {
        return {value: el[name] || ""};
    }
    // Typing updates the live value. The value attribute stays at the original HTML.
    var tag = (el.tagName || "").toLowerCase();
    if (name === "value" && (tag === "input" || tag === "textarea" || tag === "select")) {
        return {value: el.value != null ? String(el.value) : ""};
    }
    return {value: el.getAttribute(name)};
}
if (command === "attrs") {
    var attrMap = {};
    var attrList = el.attributes || [];
    for (var a = 0; a < attrList.length; a++) {
        attrMap[attrList[a].name] = attrList[a].value;
    }
    return {value: attrMap};
}
if (command === "focus") {
    try {
        el.scrollIntoView({block: "center", inline: "nearest"});
    } catch (ignore) {
        el.scrollIntoView(true);
    }
    el.focus();
    return {value: true};
}
if (command === "rect") {
    var rect = el.getBoundingClientRect();
    return {
        value: {
            x: rect.left + window.pageXOffset,
            y: rect.top + window.pageYOffset,
            width: rect.width || el.offsetWidth || 0,
            height: rect.height || el.offsetHeight || 0
        }
    };
}
if (command === "shown") {
    var shownRect = el.getBoundingClientRect();
    var shownStyle = window.getComputedStyle(el);
    var shownCss = shownStyle.display !== "none" && shownStyle.visibility !== "hidden";
    var shownWidth = el.offsetWidth > 0 || shownRect.width > 0;
    return {
        value: {
            viewport: shownRect.top >= 0 && shownRect.top < window.innerHeight &&
                shownRect.left >= 0 && shownRect.left < window.innerWidth,
            css: shownCss,
            offset: shownWidth
        }
    };
}
if (command === "checked") {
    var checked = el.hasAttribute("aria-checked")
        ? el.getAttribute("aria-checked") === "true"
        : !!el.checked;
    return {value: checked};
}
if (command === "center") {
    var aim = pageActionTarget(el);
    pageReveal(aim);
    var centerRect = aim.getBoundingClientRect();
    var centerX = centerRect.left + centerRect.width / 2;
    var centerY = centerRect.top + centerRect.height / 2;
    var centerWin = el.ownerDocument && el.ownerDocument.defaultView;
    while (centerWin && centerWin !== window) {
        var frameEl = centerWin.frameElement;
        if (!frameEl) {
            break;
        }
        var frameRect = frameEl.getBoundingClientRect();
        centerX += frameRect.left;
        centerY += frameRect.top;
        centerWin = frameEl.ownerDocument && frameEl.ownerDocument.defaultView;
    }
    return {value: {x: centerX, y: centerY}};
}
if (command === "click") {
    pageActionTarget(el).click();
    return {value: true};
}
if (command === "activate-choice") {
    if (!pageChoiceControl(el) || el.checked) {
        return {value: !!el.checked};
    }
    var choiceLabel = pageChoiceLabel(el);
    if (choiceLabel) {
        choiceLabel.click();
    }
    if (!el.checked) {
        var choiceCover = pageChoiceCover(el);
        if (choiceCover) {
            choiceCover.click();
        }
    }
    return {value: !!el.checked};
}
if (command === "hover") {
    ["mouseover", "mouseenter", "mousemove"].forEach(function (name) {
        el.dispatchEvent(new MouseEvent(name, {bubbles: true, cancelable: true, view: window}));
    });
    return {value: true};
}
if (command === "highlight") {
    var marked = pageActionTarget(el);
    var previous = marked.style.border;
    marked.style.border = "5px solid " + (extra || "blue");
    var restore = flags === "flash" || flags === "debug";
    setTimeout(function () {
        marked.style.border = restore ? previous : "5px solid " + (extra || "blue");
    }, flags === "flash" ? 300 : 2000);
    return {value: true};
}
if (command === "find") {
    var found = [];
    try {
        var snapshot = document.evaluate(
            String(extra || ""), el, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null
        );
        for (var i = 0; i < snapshot.snapshotLength; i++) {
            var node = snapshot.snapshotItem(i);
            if (node && node.nodeType === 1) {
                found.push(pageHold(node));
            }
        }
    } catch (error) {
        return {error: "invalid", message: error.message};
    }
    return {handles: found};
}
return {error: "unknown"};
