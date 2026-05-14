// JS_STATUS_LITE
// Lightweight status (no spinner logic here anymore)
return (function (quietMs) {
	var ready = (document.readyState === "complete");

	var jqActive = null;
	try {
		if (typeof jQuery !== "undefined" && jQuery && typeof jQuery.active === "number") jqActive = jQuery.active;
	} catch(e){}

	var performance_now = (window.__xhrMon && typeof window._xhrMon.performance_now === "function") ? window._xhrMon.performance_now : (window.performance && typeof window.performance.now === "function") ? window.performance.now.bind(window.performance) : window.Date.now.bind(window.Date);
	var pending = 0, last = performance_now();
	try {
		pending = (window.__xhrMon && typeof window.__xhrMon.pending === "number") ? window.__xhrMon.pending : 0;
		last    = (window.__xhrMon && window.__xhrMon.lastMutationTs) ? window.__xhrMon.lastMutationTs : last;
	} catch(e){}

	var now = performance_now();
	var domQuiet = (now - last) >= (quietMs || 400);
	var networkIdle = (pending === 0) && (jqActive === null || jqActive === 0);
	var idle = ready && networkIdle && domQuiet;

	return {
		idle: idle,
		ready: ready,
		networkIdle: networkIdle,
		domQuiet: domQuiet,
		pending: pending,
		jqActive: jqActive
	};
})(arguments[0]);
