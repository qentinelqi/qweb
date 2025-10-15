// JS_IS_SPINNER_BUSY
// Separate spinner probe (selectors configurable)
return (function (selectors, cfg) {
  var debug = !!(cfg && cfg.debug);
  var minPx = (cfg && cfg.minPx) || 4;
  var clamp = function(v,a,b){ return Math.min(Math.max(v,a), b); };

  function isHidden(el){
    var cs = getComputedStyle(el);
    return cs.display==='none' || cs.visibility==='hidden' || cs.opacity==='0';
  }
  function rectIfPaints(el){
    if (!el || !(el instanceof Element) || isHidden(el)) return null;
    var r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return null;
    var vw = innerWidth || document.documentElement.clientWidth;
    var vh = innerHeight || document.documentElement.clientHeight;
    var ix = Math.max(0, Math.min(r.right, vw) - Math.max(r.left, 0));
    var iy = Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
    return (ix * iy) >= minPx ? r : null;
  }
//   find the deepest descendant that actually “paints” (i.e., not display:none/visibility:hidden/opacity:0, has non-zero size, and at least minPx area inside viewport).
  function pickDeepPainted(el){
    var best = null;
    (function walk(n){
      if (!(n instanceof Element)) return;
      var r = rectIfPaints(n);
      if (r) best = { node: n, rect: r }; // deepest wins
      if (n.shadowRoot) n.shadowRoot.querySelectorAll('*').forEach(walk);
      if (n.children) Array.prototype.forEach.call(n.children, walk);
    })(el);
    if (best) return best;
    var r = rectIfPaints(el);
    return r ? { node: el, rect: r } : null;
  }
  function isTopmost(target, host, rect){
    var pts = [
      [rect.left + rect.width/2, rect.top + rect.height/2],
      [rect.left + 2, rect.top + 2],
      [rect.right - 2, rect.bottom - 2],
    ].map(function(p){ return [clamp(p[0],1,innerWidth-1), clamp(p[1],1,innerHeight-1)]; });
    for (var i=0;i<pts.length;i++){
      var x = pts[i][0], y = pts[i][1];
      var chain = document.elementsFromPoint ? document.elementsFromPoint(x,y)
                                             : [document.elementFromPoint(x,y)].filter(Boolean);
      if (!chain || !chain.length) continue;
      var first = chain[0];
      if (first === target || first === host || host.contains(first)) return true;
    }
    return false;
  }

  try {
    var sels = Array.isArray(selectors) ? selectors : [];
    for (var i=0;i<sels.length;i++){
      var sel = sels[i];
      var nodes = document.querySelectorAll(sel);
      if (debug) console.log('"%s" → %d candidate(s)', sel, nodes.length);
      for (var j=0;j<nodes.length;j++){
        var host = nodes[j];
        var picked = pickDeepPainted(host);
        if (!picked) continue;
        if (isTopmost(picked.node, host, picked.rect)) {
          if (debug) console.log('Visible spinner', {selector: sel, host: host, target: picked.node});
          return true; // IMPORTANT: return a boolean
        } else if (debug) {
          console.log('Occluded or not topmost', {selector: sel, host: host});
        }
      }
    }
    return false;
  } catch (e) {
    if (debug) console.warn('Probe error:', e);
    return false;
  }
// minPx = how many on-screen pixels are enough to call it visible?
})(arguments[0], { debug: false, minPx: 4 });