// JS_INSTALL_MONITOR
// Installs network/DOM activity monitors into the page (fetch, XHR, MutationObserver).
// Always returns true on success (even if some patches are skipped).
// The optional `debug` flag (default: false) is used only for troubleshooting.
// ...full code below...
return (function (debug = false) {
	if (window.__xhrMon && window.__xhrMon.installed) return true;

	// to circumvent any website monkey-patching of native functions
	const _console = {
		log: console.log,
		warn: console.warn ? console.warn : console.log,
		error: console.error ? console.error : console.log
	};
	const Array_from = Array.from;
	const setTimeout = window.setTimeout;

	//use polyfills if neccessary
	const Object_getPrototypeOf = Object.getPrototypeOf ? Object.getPrototypeOf : function(obj) { return obj.__proto__; };
	const performance_now = window.performance && typeof window.performance.now === "function" ? window.performance.now.bind(window.performance) : window.Date.now.bind(window.Date);
	const Set = window.Set ? window.Set : SetPolyfill();
	const FinalizationRegistry = window.FinalizationRegistry ? window.FinalizationRegistry : FinalizationRegistryPolyfill();
	const WeakRef = window.FinalizationRegistry && window.WeakRef ? window.WeakRef : WeakRefPolyfill();
	const WeakSet = window.WeakSet ? window.WeakSet : WeakSetPolyfill();
	const WeakMap = window.WeakMap ? window.WeakMap : WeakMapPolyfill();
	const Symbol = window.Symbol ? window.Symbol : Object;

	const mon = window.__xhrMon = window.__xhrMon ? window.xhrMon : {
		installed: true,
		pending: window.__xhrMon && typeof window.__xhrMon.pending === "number" ? window.__xhrMon.pending : 0,
		fetchPatched: false,
		xhrPatched: false,
		lastMutationTs: performance_now(),
		observerStarted: false,
		performance_now: performance_now // for use by script wait_status_lite.js, in case of monkey-patching by the website
	};

	const fetchPending = selfAssign(new Set(), "add", "delete", "size");
	const xhrPending = selfAssign(new Set(), "add", "delete", "size");
	if (typeof xhrPending.toArray !== "function") {
		xhrPending.toArray = function toArray() { return Array_from(this); };
	}

	Object.defineProperty(mon, "pending", {
		get: function() { return fetchPending.size + xhrPending.size; },
		configurable: true
	});

	try {
		if (!mon.fetchPatched && typeof window.fetch === "function") {
			const fetchFinalizationRegistry = selfAssign(new FinalizationRegistry(fetchGcHandler), "register", "unregister");

			const _fetch = bindApply(window.fetch);
			const _finally = typeof Promise.prototype.finally === "function" ? bindApply(Promise.prototype.finally) : null;
			const _then = typeof Promise.prototype.then === "function" ? bindApply(Promise.prototype.then) : null;

			if (_finally || _then) {
				window.fetch = fetch;
				mon.fetchPatched = true;
			} else {
				console.warn("XHR Mon: window.fetch was present, but both Promise.prototype.finally and Promise.prototype.then are missing");
			}

			function fetch() {
				var promise = _fetch(this, arguments);
				try {
					if (!promise) {
						if (debug) {
							console.warn("XHR Mon: No promise returned from fetch call:", promise);
						}
						return promise;
					}

					if (_finally !== null) {
						promise = _finally(promise, [function() { setTimeout(fetchDone); }]);
					} else {
						promise = _then(promise, [
							function(result) { setTimeout(fetchDone); return result; },
							function(error) { setTimeout(fetchDone); throw error; }
						]);
					}

					const symbol = Symbol();
					fetchPending.add(symbol);
					fetchFinalizationRegistry.register(promise, symbol, symbol);

					if (debug) {
						_console.log("XHR monitor: fetch started, pending count:", mon.pending);
					}

					function fetchDone() {
						try {
							fetchPending.delete(symbol);
							fetchFinalizationRegistry.unregister(symbol);
							if (debug) {
								_console.log("XHR monitor: fetch ended, pending count:", mon.pending);
							}
						} catch(e) {
							if (debug) {
								_console.error("XHR monitor: Error in fetchDone:", e);
							}
						}
					}
				} catch(e) {
					if (debug) _console.error("XHR monitor: Error tracking fetch:", e);
				}
				try {
					return promise;
				} finally {
					promise = null;
				}
			}

			function fetchGcHandler(symbol) {
				if (fetchPending.delete(symbol)) {
					if (debug) {
						_console.log("XHR monitor: fetch promise garbage collected without resolving, pending count:", mon.pending);
					}
				} else if (debug) {
					_console.warn("XHR monitor: during fetch promise garbage collection handler, symbol not found in pending set", symbol);
				}
			}
		}
	} catch(e) {
		if (debug) _console.warn("XHR monitor: fetch patch failed", e);
	}

	try {
		if (!mon.xhrPatched && window.XMLHttpRequest && window.XMLHttpRequest.prototype) {
			const opened = selfAssign(new WeakSet(), "has", "add"); // xhrs that were opened and readyState reached 1.  instances are NOT removed from this set, even after sent/done
			const sent = selfAssign(new WeakMap(), "has", "set", "get"); // maps xhr -> weakRef object.  instances are NOT removed from this map, even after done
			const done = selfAssign(new WeakSet(), "has", "add");
			const xhrFinalizationRegistry = selfAssign(new FinalizationRegistry(xhrGcHandler), "register", "unregister");

			var reversionCheckScheduled = false;

			const xhrProto = window.XMLHttpRequest.prototype;
			const _open = bindApply(xhrProto.open);
			const _send = bindApply(xhrProto.send);
			const _addEventListener = bindApply(xhrProto.addEventListener);
			const _getReadyState = bindApply(Object.getOwnPropertyDescriptor(xhrProto, "readyState").get);
			
			xhrProto.open = open;
			xhrProto.send = send;

			mon.xhrPatched = true;

			function open(method, url) {
				const returnVal = _open(this, arguments);
				try {
					const readyState = _getReadyState(this);
					if (readyState >= 1) {
						if (!opened.has(this)) {
							opened.add(this);
							_addEventListener(this, ["readystatechange", onreadystatechange]);
						}
					} else {
						_console.warn("XHR monitor: open() called but readyState < 1, actual: ", readyState);
					}
				} catch(e) {
					console.error("XHR Monitor: Error in xhr.open:", e);
				}
				return returnVal;
			}
			
			function send() {
				const returnVal = _send(this, arguments);
				try {
					if (opened.has(this) && !(sent.has(this) || done.has(this))) {
						const weakRef = new WeakRef(this);
						sent.set(this, weakRef);

						// Check for long-polling in request body
						var isLongPolling = false;
						if (arguments[0]) {
							const body = typeof arguments[0] === "string" ? arguments[0] : JSON.stringify(arguments[0]);
							if (body && body.indexOf('"connectionType":"long-polling"') !== -1) {
								isLongPolling = true;
							}
						}
						if (!isLongPolling) {
							xhrPending.add(weakRef);
							xhrFinalizationRegistry.register(this, weakRef, this);

							if (!reversionCheckScheduled) {
								setTimeout(readyStateReversionCheck, 1000);
								reversionCheckScheduled = true;
							}

							if (debug) {
								_console.log("XHR monitor: request started, pending count:", mon.pending);
							}
						}
					}
				} catch(e) {
					if (debug) {
						_console.error("XHR monitor: Error tracking request:", e);
					}
				}
				return returnVal;
			}

			function onreadystatechange() {
				try {
					const readyState = _getReadyState(this);
					if (readyState !== 4 && readyState !== 0) return;

					if (!sent.has(this)) {
						if (debug) {
							_console.warn("XHR monitor: unexpected xhr-like object that was never sent() passed to onloadend event handler", this);
						}
						return;
					} else if (done.has(this)) {
						return;
					}

					const weakRef = sent.get(this);
					if (!weakRef) return;
					if (xhrPending.delete(weakRef)) {
						done.add(this);
						xhrFinalizationRegistry.unregister(this);
						if (debug) {
							_console.log("XHR monitor: request ended, pending count:", mon.pending);
						}
					} else if (debug) {
						_console.warn("XHR monitor: weakRef not found in pending set", weakRef);
					}
				} catch(e) {
					if (debug) {
						_console.error("XHR monitor: Error during request onloadend", e);
					}
				}
			}

			function readyStateReversionCheck() {
				const xhrPendingCopy = xhrPending.toArray();
				for (var i = 0; i < xhrPendingCopy.length; i++) {
					const weakRef = xhrPendingCopy[i];
					const xhr = weakRef.deref();
					if (xhr === undefined) {
						xhrPending.delete(weakRef);
						if (debug) {
							_console.warn("XHR monitor: xhr weakRef showing already garbage collected, pending count:", mon.pending);
						}
					} else if (_getReadyState(xhr) === 0) {
						xhrPending.delete(weakRef);
						done.add(xhr);
						xhrFinalizationRegistry.unregister(xhr);
						if (debug) {
							_console.log("XHR Monitor: already-sent request reverted to readyState 0, pending count:", mon.pending);
						}
					}
				}
				if (xhrPending.size > 0) {
					setTimeout(readyStateReversionCheck, 1000);
				} else {
					reversionCheckScheduled = false;
				}
			}

			function xhrGcHandler(weakRef) {
				if (xhrPending.delete(weakRef)) {
					if (debug) {
						_console.log("XHR monitor: request garbage collected without loadend event, pending count:", mon.pending, weakRef);
					}
				} else if (debug) {
					_console.warn("XHR monitor: during xhr garbage collection handler, weakRef not found in pending set", weakRef);
				}
			}
		}
	} catch(e) {
		if (debug) _console.warn("XHR monitor: xhr patch failed", e);
	}

	try {
		if (!mon.observerStarted && window.MutationObserver) {
			const obs = new MutationObserver(function() { mon.lastMutationTs = performance_now(); });
			obs.observe(document, { childList: true, subtree: true });
			mon.observerStarted = true;
		}
	} catch(e) {
		if (debug) _console.warn("XHR monitor: observer setup failed", e);
	}

	if (debug) _console.log("XHR monitor: setup complete");
	return true;


	// To circumvent any website monkey-patching of native functions
	// Note that bindApply is only called during the initialization script (NOT within any callbacks) ...
	// therefore, we can guarentee that Function.prototype.apply hasn't been monkey-patched yet (assuming the script is running on new document, before the DOM has been loaded)
	function bindApply(nativeFunc) {
		return Function.prototype.apply.bind(nativeFunc);
	}

	// assign property/descriptor from prototype to the self, to circumvent any website monkey-patching of prototype native functions
	function selfAssign(self) {
		for (var i = 1; i < arguments.length; i++) {
			const property = arguments[i];
			var proto = self;
			while (proto) {
				const desc = Object.getOwnPropertyDescriptor(proto, property);
				if (!desc) {
					proto = Object_getPrototypeOf(proto);
				} else {
					Object.defineProperty(self, property, desc);
					break;
				}
			}
			if (debug && !proto) {
				_console.warn("XHR monitor: Unable to find descriptor for property in object's prototype chain:", property, self);
			}
		}
		return self;
	}

	//polyfills for older browsers.  WeakRefs will become strongly referenced, so FinalizationRegistry can be a no-op

	function WeakRefPolyfill() {
		function WeakRef(ref) {
			this._ref = ref;
		}
		WeakRef.prototype.deref = function deref() {
			return this._ref;
		};
		return WeakRef;
	}

	function FinalizationRegistryPolyfill() {
		function FinalizationRegistry() {}
		FinalizationRegistry.prototype.register = function() {};
		FinalizationRegistry.prototype.unregister = function() {};
		return FinalizationRegistry;
	}

	function SetPolyfill() {
		const _indexOf = bindApply(Array.prototype.indexOf);
		const _push = bindApply(Array.prototype.push);
		const _splice = bindApply(Array.prototype.splice);

		function Set() {
			this._values = [];
		}

		Set.prototype.has = function has(value) {
			return _indexOf(this._values, [value]) !== -1;
		};

		Set.prototype.add = function add(value) {
			if (_indexOf(this._values, [value]) === -1) {
				_push(this._values, [value]);
			}
			return this;
		};

		Set.prototype.delete = function del(value) {
			var index = _indexOf(this._values, [value]);
			if (index === -1) return false;
			_splice(this._values, [index, 1]);
			return true;
		};

		Set.prototype.toArray = function toArray() {
			if (typeof Array_from === "function") {
				return Array_from(this._values);
			}
			var result = [];
			for (var i = 0; i < this._values.length; i++) {
				result.push(this._values[i]);
			}
			return result;
		};

		Object.defineProperty(Set.prototype, "size", {
			configurable: false,
			get: function() { return this._values.length; }
		});

		return Set;
	}

	function WeakSetPolyfill() {
		const _defineProperty = Object.defineProperty;
		const _Object = Object;

		function WeakSet() {
			this._id = "__WeakSet_" + (Math.random() * 1e9) + "_" + performance_now() + "__";
		}

		WeakSet.prototype.has = function has(value) {
			return value[this._id] === true;
		};

		WeakSet.prototype.add = function add(value) {
			if (_Object(value) !== value) throw new TypeError("Invalid value used in weak set");
			_defineProperty(value, this._id, {
				value: true,
				writable: true,
				configurable: false,
				enumerable: false
			});
			return this;
		};

		return WeakSet;
	}

	function WeakMapPolyfill() {
		const _defineProperty = Object.defineProperty;
		const _Object = Object;

		function WeakMap() {
			this._id = "__WeakMap_" + (Math.random() * 1e9) + "_" + performance_now() + "__";
		}

		WeakMap.prototype.has = function has(key) {
			return this._id in key;
		};

		WeakMap.prototype.set = function set(key, value) {
			if (_Object(key) !== key) throw new TypeError("Invalid value used as weak map key");
			_defineProperty(key, this._id, {
				value: value,
				writable: true,
				configurable: false,
				enumerable: false
			});
			return this;
		};

		WeakMap.prototype.get = function get(key) {
			return key[this._id];
		};

		return WeakMap;
	}
})();
