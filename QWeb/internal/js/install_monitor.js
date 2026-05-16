// JS_INSTALL_MONITOR
// Installs network/DOM activity monitors into the page (fetch, XHR, MutationObserver).
// Always returns true on success (even if some patches are skipped).
// The optional `debug` flag (default: false) is used only for troubleshooting.
// ...full code below...
return (function (debug = true) {
	if (window.__xhrMon && window.__xhrMon.installed) return true;

	window.__xhrMon = Object.assign(window.__xhrMon || {}, {
		installed: true,
		pending: (window.__xhrMon && typeof window.__xhrMon.pending === "number") ? window.__xhrMon.pending : 0,
		fetchPatched: false,
		xhrPatched: false,
		lastMutationTs: performance.now(),
		observerStarted: false
	});

	const fetchPending = [];
	const xhrPending = [];
	Object.defineProperty(window.__xhrMon, "pending", {
		configurable: true,
		get: function() { return fetchPending.length + xhrPending.length; }
	});


	try {
		if (!window.__xhrMon.fetchPatched && typeof window.fetch === "function") {
			const _fetch = window.fetch;
			window.fetch = fetch;
			window.__xhrMon.fetchPatched = true;
			
			function fetch() {
				let promise = _fetch.apply(this, arguments);
				try {
					if (!promise) {
						if (debug) {
							console.warn("XHR Mon: No promise returned from fetch call:", promise);
						}
						return promise;
					}

					/* In case the finally/then callback function runs synchronously upon the call to promise.finally()/promise.then() ...
					 * The symbol is constructed first, so it is available to the closure(s), but fetchDone is scheduled async via setTimeout.
					 * This is because fetchDone should not run until AFTER fetchPending array has been populated with the symbol (below), yet we don't
					 * want to populate it with the symbol until promise.finally/promise.then has completed successfully. */
					const symbol = Symbol();
					if (typeof promise.finally === "function") {
						promise = promise.finally(function() { setTimeout(fetchDone, 0, symbol); });
					} else {
						promise = promise.then(
							function(result) { setTimeout(fetchDone, 0, symbol); return result; },
							function(error) { setTimeout(fetchDone, 0, symbol); throw error; }
						);
					}
					fetchPending.push(symbol);
					if (debug) {
						console.log("XHR monitor: fetch started, pending count:", window.__xhrMon.pending);
					}
				} catch(e) {
					if (debug) {
						console.error("XHR monitor: Error in fetch:", e);
					}
				}
				return promise;
			}

			function fetchDone(symbol) {
				try {
					const index = fetchPending.indexOf(symbol);
					if (index > -1) {
						fetchPending.splice(index, 1);
						if (debug) {
							console.log("XHR monitor: fetch ended, pending count:", window.__xhrMon.pending);
						}
					} else if (debug) {
						console.warn("XHR monitor: symbol not found in fetchPending array", symbol, fetchPending);
					}
				} catch(e) {
					if (debug) {
						console.error("XHR monitor: Error in fetchDone:", e);
					}
				}
			}
		}
	} catch(e){if (debug) console.warn("XHR monitor: fetch patch failed", e);}

	try {
		if (!window.__xhrMon.xhrPatched && window.XMLHttpRequest && window.XMLHttpRequest.prototype) {
			const _open = XMLHttpRequest.prototype.open;
			const _send = XMLHttpRequest.prototype.send;

			//These methods are often monkey-patched by front-end frameworks and SaaS websites, so we preserve the native methods here to circumvent any monkey-patched methods
			const _addEventListener = XMLHttpRequest.prototype.addEventListener;
			const _getReadyState = Object.getOwnPropertyDescriptor(XMLHttpRequest.prototype, "readyState").get;

			let reversionCheckScheduled = false;

			XMLHttpRequest.prototype.open = open;
			XMLHttpRequest.prototype.send = send;

			window.__xhrMon.xhrPatched = true;
			
			function open() {
				const returnVal = _open.apply(this, arguments);
				try {
					const readyState = _getReadyState.apply(this);
					if (readyState > 0) {
						if (!this.__xhrOpened) {
							this.__xhrOpened = true;
							_addEventListener.apply(this, ["readystatechange", onreadystatechange]);
						}
					} else if (debug) {
						console.warn("XHR monitor: xhr.open() called but readyState < 1, actual: ", readyState);
					}
				} catch (e) {
					if (debug) {
						console.error("XHR monitor: Error in xhr.open:", e);
					}
				}
				return returnVal;
			}

			function send() {
				const returnVal = _send.apply(this, arguments);
				try {
					if (this.__xhrOpened && !(this.__xhrSent || this.__xhrDone)) {
						const weakRef = new WeakRef(this);
						this.__xhrSent = weakRef;

						// Check for long-polling in request body
						let isLongPolling = false;
						if (arguments[0]) {
							try {
								const body = typeof arguments[0] === "string" ? arguments[0] : JSON.stringify(arguments[0]);
								if (body && body.indexOf('"connectionType":"long-polling"') !== -1) {
									isLongPolling = true;
								}
							} catch(e) {
								if (debug) {
									console.error("XHR monitor: error checking for isLongPolling in arguments[0]", e, arguments[0]);
								}
							}
						}
						if (!isLongPolling) {
							xhrPending.push(weakRef);
							if (!reversionCheckScheduled) {
								setTimeout(readyStateReversionCheck, 1000);
								reversionCheckScheduled = true;
							}
							if (debug) {
								console.log("XHR monitor: waiting for request, pending count:", window.__xhrMon.pending);
							}
						}
					}
				} catch(e) {
					if (debug) {
						console.error("XHR monitor: error in xhr.send", e);
					}
				}
				return returnVal;
			}

			function onreadystatechange() {
				try {
					if (this.__xhrDone) {
						return;
					}
					const readyState = _getReadyState.apply(this);
					if (readyState !== 4 && readyState !== 0) return;

					const weakRef = this.__xhrSent;
					if (typeof weakRef !== "object") {
						if (debug) {
							console.warn("XHR monitor: unexpected xhr-like object without __xhrSent set to a weakRef was passed to onreadystatechange event handler", this, weakRef);
						}
						return;
					}

					const index = xhrPending.indexOf(weakRef);
					if (index > -1) {
						this.__xhrDone = true;
						xhrPending.splice(index, 1);
						if (debug) {
							console.log("XHR monitor: request ended, pending count:", window.__xhrMon.pending);
						}
					} else if (debug) {
						console.warn("XHR monitor: weakRef not found in xhrPending array", weakRef, xhrPending);
					}
				} catch(e) {
					console.error("XHR monitor: error in onreadystatechange:", e);
				}
			}

			function readyStateReversionCheck() {
				try {
					for (let i = 0; i < xhrPending.length;) {
						const weakRef = xhrPending[i];
						const xhr = weakRef.deref();
						if (xhr === undefined) {
							xhrPending.splice(i, 1);
							if (debug) {
								console.warn("XHR monitor: already-sent request was garbage collected without triggering listener, pending count:", window.__xhrMon.pending);
							}
							continue;
						}
						const readyState = _getReadyState.apply(xhr);
						if (readyState === 0 || readyState === 4) {
							xhr.__xhrDone = true;
							xhrPending.splice(i, 1);
							if (debug) {
								console.warn("XHR monitor: already-sent request reverted to readyState 0 without triggering listener, pending count:", window.__xhrMon.pending);
							}
						} else {
							i++;
						}
					}
				} catch(e) {
					if (debug) {
						console.error("XHR monitor: error in readyStateReversionCheck:", e);
					}
				}
				if (xhrPending.length > 0) {
					setTimeout(readyStateReversionCheck, 1000);
				} else {
					reversionCheckScheduled = false;
				}
			}
		}
	} catch(e){ if (debug) console.warn("XHR monitor: xhr patch failed", e);}

	try {
		if (!window.__xhrMon.observerStarted && window.MutationObserver) {
			const obs = new MutationObserver(function(){ window.__xhrMon.lastMutationTs = performance.now(); });
			obs.observe(document.documentElement || document.body, {
				childList:true, subtree:true
			});
			window.__xhrMon.observerStarted = true;
		}
	} catch(e){if (debug) console.warn("XHR monitor: observer setup failed", e);}

	if (debug) console.log("XHR monitor: setup complete");
	return true;
})();
