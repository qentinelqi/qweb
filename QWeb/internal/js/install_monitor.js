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
		lastMutationTs: performance.now(),
		observerStarted: false
	});

	try {
		if (!window.__xhrMon.fetchPatched && typeof window.fetch === "function") {
			const _fetch = window.fetch;
			window.fetch = function() {
				let p = _fetch.apply(this, arguments);
				try {
					const dec = function(){ try { window.__xhrMon.pending--; } catch(e) {} };
					p = p && typeof p.finally === "function"
						? p.finally(dec)
						: p.then(function(r){ dec(); return r; }, function(e){ dec(); throw e; });
					window.__xhrMon.pending++;
				} catch(e) {
					if (debug) console.error("XHR monitor: error in fetch", e);
				}
				return p;
			};
			window.__xhrMon.fetchPatched = true;
		}
	} catch(e){if (debug) console.warn("XHR monitor: fetch patch failed", e);}

	try {
		if (!window.__xhrMon.xhrPatched && window.XMLHttpRequest && window.XMLHttpRequest.prototype) {
			const _open = XMLHttpRequest.prototype.open;
			const _send = XMLHttpRequest.prototype.send;
			const _addEventListener = XMLHttpRequest.prototype.addEventListener;
			const _getReadyState = Object.getOwnPropertyDescriptor(XMLHttpRequest.prototype, "readyState").get;
			XMLHttpRequest.prototype.open = function() {
				const returnVal = _open.apply(this, arguments);
				try {
					if (!this.__xhrOpened) {
						_addEventListener.call(this, "loadend", done, { once:true });
						_addEventListener.call(this, "abort", done, { once:true });
						_addEventListener.call(this, "error", done, { once:true });
						_addEventListener.call(this, "timeout", done, { once:true });
						_addEventListener.call(this, "readystatechange", readystatechange);
						this.__xhrOpened = true;
					}
				} catch(e) {
					if (debug) console.error("XHR monitor: error in open", e);
				}
				return returnVal;
			};
			XMLHttpRequest.prototype.send = function() {
				const returnVal = _send.apply(this, arguments);
				try {
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
					if (this.__xhrOpened && !isLongPolling && !this.__xhrSent) {
						try {
							this.__xhrSent = true;
							window.__xhrMon.pending++;
							if (debug) {
								console.log("XHR monitor: waiting for request, pending count:", window.__xhrMon.pending);
							}
						} catch(e) {
							if (debug) console.error("XHR monitor: error in send", e);
						}
					}
				} catch(e) {
					if (debug) console.error("XHR monitor: error in send", e);
				}
				return returnVal;
			};
			function done() {
				try {
					if (!(this.__xhrOpened && this.__xhrSent) || this.__xhrDone) {
						return;
					}
					this.__xhrDone = true;
					window.__xhrMon.pending--;
					if (debug) {
						console.log("XHR monitor: request ended, pending count:", window.__xhrMon.pending);
					}
				} catch(e) {
					if (debug) console.error("XHR monitor: error in done", e);
				}
			}
			function readystatechange() {
				const readyState = _getReadyState.apply(this);
				if (readyState === 4 || readyState === 0) {
					done.apply(this);
				}
			}
			window.__xhrMon.xhrPatched = true;
		}
	} catch(e){ if (debug) console.warn("XHR monitor: xhr patch failed", e);}

	try {
		if (!window.__xhrMon.observerStarted && window.MutationObserver) {
			const obs = new MutationObserver(function(){ window.__xhrMon.lastMutationTs = performance.now(); });
			obs.observe(document.documentElement || document.body || document, {
				childList:true, subtree:true
			});
			window.__xhrMon.observerStarted = true;
		}
	} catch(e){if (debug) console.warn("XHR monitor: observer setup failed", e);}

	if (debug) console.log("XHR monitor: setup complete");
	return true;
})();
