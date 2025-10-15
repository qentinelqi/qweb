// JS_INSTALL_MONITOR
// Installs network/DOM activity monitors into the page (fetch, XHR, MutationObserver).
// Always returns true on success (even if some patches are skipped).
// The optional `debug` flag (default: false) is used only for troubleshooting.
// ...full code below...
return (function (debug = false) {
	if (window.__xhrMon && window.__xhrMon.installed) return true;

	window.__xhrMon = Object.assign(window.__xhrMon || {}, {
		installed: true,
		pending: (window.__xhrMon && typeof window.__xhrMon.pending === "number") ? window.__xhrMon.pending : 0,
		fetchPatched: false,
		xhrPatched: false,
		lastMutationTs: Date.now(),
		observerStarted: false
	});

	try {
		if (!window.__xhrMon.fetchPatched && typeof window.fetch === "function") {
			const _orig = window.fetch;
			window.fetch = function() {
				try { window.__xhrMon.pending++; } catch(e) {}
				const p = _orig.apply(this, arguments);
				const dec = function(){ try { window.__xhrMon.pending--; } catch(e) {} };
				return p && typeof p.finally === "function"
					? p.finally(dec)
					: p.then(function(r){ dec(); return r; }, function(e){ dec(); throw e; });
			};
			window.__xhrMon.fetchPatched = true;
		}
	} catch(e){if (debug) console.warn("XHR monitor: fetch patch failed", e);}

		try {
		if (!window.__xhrMon.xhrPatched && window.XMLHttpRequest && window.XMLHttpRequest.prototype) {
			const _open = XMLHttpRequest.prototype.open;
			const _send = XMLHttpRequest.prototype.send;
			XMLHttpRequest.prototype.open = function() { this.__xhrTracked = true; return _open.apply(this, arguments); };
			XMLHttpRequest.prototype.send = function() {
				// Check for long-polling in request body
				let isLongPolling = false;
				if (arguments[0]) {
					try {
						const body = typeof arguments[0] === "string" ? arguments[0] : JSON.stringify(arguments[0]);
						if (body && body.indexOf('"connectionType":"long-polling"') !== -1) {
							isLongPolling = true;
						}
					} catch(e) {}
				}
				if (this.__xhrTracked && !isLongPolling) {
					try {
						window.__xhrMon.pending++;
						if (debug) {
							console.log("XHR monitor: waiting for request, pending count:", window.__xhrMon.pending);
						}
					} catch(e) {}
					this.addEventListener("loadend", function(){
						try {
							window.__xhrMon.pending--;
							if (debug) {
								console.log("XHR monitor: request ended, pending count:", window.__xhrMon.pending);
							}
						} catch(e) {}
					}, { once:true });
				}
				return _send.apply(this, arguments);
			};
			window.__xhrMon.xhrPatched = true;
		}
	} catch(e){ if (debug) console.warn("XHR monitor: xhr patch failed", e);}

	try {
		if (!window.__xhrMon.observerStarted && window.MutationObserver) {
			const obs = new MutationObserver(function(){ window.__xhrMon.lastMutationTs = Date.now(); });
			obs.observe(document.documentElement || document.body, {
				childList:true, subtree:true
			});
			window.__xhrMon.observerStarted = true;
		}
	} catch(e){if (debug) console.warn("XHR monitor: observer setup failed", e);}

	if (debug) console.log("XHR monitor: setup complete");
	return true;
})();
