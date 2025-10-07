// JS_IS_SPINNER_BUSY
// Separate spinner probe (selectors configurable)
return (function (selectors) {
	function visible(el){
		if (!el) return false;
		var cs = getComputedStyle(el);
		if (cs.visibility==='hidden' || cs.display==='none' || cs.opacity==='0') return false;
		var r = el.getBoundingClientRect();
		return r.width>0 && r.height>0;
	}
	try {
		var sels = Array.isArray(selectors) ? selectors : [];
		for (var i=0;i<sels.length;i++){
			var nodes = document.querySelectorAll(sels[i]);
			for (var j=0;j<nodes.length;j++){
				if (visible(nodes[j])) return true;
			}
		}
		return false;
	} catch (e) {
		return false; // if probe fails, treat as not-busy (avoid blocking)
	}
})(arguments[0]);
