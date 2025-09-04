# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 -            Qentinel Group.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------
import time
from robot.api import logger
from selenium.common.exceptions import JavascriptException
from typing import Optional
from QWeb.internal import javascript
from QWeb.internal.exceptions import QWebDriverError
from QWeb.keywords import config


# Install monitor (fetch/XMLHttpRequest + MutationObserver). Idempotent.
JS_INSTALL_MONITOR = r"""
return (function () {
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
  } catch(e){}

  try {
    if (!window.__xhrMon.xhrPatched && window.XMLHttpRequest && window.XMLHttpRequest.prototype) {
      const _open = XMLHttpRequest.prototype.open;
      const _send = XMLHttpRequest.prototype.send;
      XMLHttpRequest.prototype.open = function() { this.__xhrTracked = true; return _open.apply(this, arguments); };
      XMLHttpRequest.prototype.send = function() {
        if (this.__xhrTracked) {
          try { window.__xhrMon.pending++; } catch(e) {}
          this.addEventListener("loadend", function(){ try { window.__xhrMon.pending--; } catch(e) {} }, { once:true });
        }
        return _send.apply(this, arguments);
      };
      window.__xhrMon.xhrPatched = true;
    }
  } catch(e){}

  try {
    if (!window.__xhrMon.observerStarted && window.MutationObserver) {
      const obs = new MutationObserver(function(){ window.__xhrMon.lastMutationTs = Date.now(); });
      obs.observe(document.documentElement || document.body, {
        childList:true, subtree:true
      });
      window.__xhrMon.observerStarted = true;
    }
  } catch(e){}

  return true;
})();
"""
# This was modified above:
# obs.observe(document.documentElement || document.body, {
#        childList:true, subtree:true, attributes:true, characterData:true
#      });

# Lightweight status (no spinner logic here anymore)
JS_STATUS_LITE = r"""
return (function (quietMs) {
  var ready = (document.readyState === "complete");

  var jqActive = null;
  try {
    if (typeof jQuery !== "undefined" && jQuery && typeof jQuery.active === "number") jqActive = jQuery.active;
  } catch(e){}

  var pending = 0, last = Date.now();
  try {
    pending = (window.__xhrMon && typeof window.__xhrMon.pending === "number") ? window.__xhrMon.pending : 0;
    last    = (window.__xhrMon && window.__xhrMon.lastMutationTs) ? window.__xhrMon.lastMutationTs : last;
  } catch(e){}

  var now = Date.now();
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
"""

# Separate spinner probe (selectors configurable)
JS_IS_SPINNER_BUSY = r"""
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
"""


def setup_xhr_monitor() -> bool:
    try:
        ok = javascript.execute_javascript(JS_INSTALL_MONITOR)
        if ok is not True:
            logger.debug(f"setup_xhr_monitor returned non-True: {ok}")
        return bool(ok)
    except JavascriptException as e:
        logger.debug(f"setup_xhr_monitor failed: {e}")
        raise QWebDriverError(e)  # pylint: disable=W0707


def get_light_status(quiet_ms: int = 400) -> Optional[dict]:
    """Full status dict. None on failure."""
    try:
        st = javascript.execute_javascript(JS_STATUS_LITE, quiet_ms)
        if isinstance(st, dict):
            return st
        logger.debug(f"get_light_status: unexpected return {type(st)}")
        return None
    except JavascriptException as e:
        logger.debug(f"get_light_status failed: {e}")
        return None


def is_spinner_busy(selectors: Optional[list[str]] = None) -> Optional[bool]:
    """Return True/False if spinner appears visible; None on probe failure."""
    try:
        busy = javascript.execute_javascript(JS_IS_SPINNER_BUSY, selectors)
        # Selenium returns a JS boolean → Python bool; still validate
        if isinstance(busy, bool):
            return busy
        logger.debug(f"is_spinner_busy: unexpected return {type(busy)}")
        return None
    except JavascriptException as e:
        logger.debug(f"is_spinner_busy failed: {e}")
        return None


def _parse_spinner_selectors() -> Optional[list[str]]:
    raw = config.get_config("SpinnerCSS")
    if raw is None:
        return None

    # Normalize common "empty" markers to None
    if isinstance(raw, str) and raw.strip().lower() in ("", "none", "null", "false", "off"):
        return None

    # Otherwise interpret as comma-separated CSS selectors
    if isinstance(raw, str):
        return [s.strip() for s in raw.split(",") if s.strip()]

    return None


def wait_xhr(timeout: float = 15.0,
             poll_interval: float = 0.1) -> None:
    """
    Order: readyState -> network idle -> spinner gone -> DOM quiet (bounded).
    - `quiet_ms`: quiet window needed to call DOM "settled"
    """
    DOM_QUIET_MAX_MS = 1500     # Max time to wait for DOM quiet
    DOM_CAP_MULTIPLIER = 1.5    # Cap multiplier for DOM quiet time
    spinner_css = _parse_spinner_selectors()
    quiet_ms = config.get_config("RenderWait")
    # wait at max configured quite_ms + multiplier or max amount (to avoid getting stuck)
    dom_quiet_cap_ms = min(quiet_ms * DOM_CAP_MULTIPLIER, DOM_QUIET_MAX_MS)
    setup_xhr_monitor()
    start = time.time()

    while time.time() - start < timeout:
        st = get_light_status(quiet_ms=quiet_ms)   # ready/networkIdle/domQuiet (no spinner)

        if st is None:
            logger.debug("wait_xhr: status probe failed (treating as not ready)")
            time.sleep(poll_interval)
            continue

        if not st.get("ready"):
            logger.debug("wait_xhr: waiting for document.readyState=complete")
            time.sleep(poll_interval)
            continue

        if not st.get("networkIdle"):
            logger.debug(
                f"wait_xhr: waiting for network idle "
                f"(pending={st.get('pending')} jqActive={st.get('jqActive')})"
            )
            time.sleep(poll_interval)
            continue

        # Spinner BEFORE DOM quiet (optional)
        if spinner_css:
            busy = is_spinner_busy(spinner_css)
            if busy is None:
                logger.debug("wait_xhr: spinner probe failed (ignoring); "
                             "proceeding to bounded DOM quiet")
            elif busy:
                logger.debug("wait_xhr: spinner visible")
                time.sleep(poll_interval)
                continue

        # BOUNDED DOM quiet (last, and capped)
        if st.get("domQuiet"):
            return

        logger.debug(f"wait_xhr: waiting for DOM quiet ({quiet_ms}ms window; "
                     f"capped {dom_quiet_cap_ms}ms)")
        dom_phase_start = time.time()
        while (time.time() - dom_phase_start) * 1000.0 < dom_quiet_cap_ms:
            st2 = get_light_status(quiet_ms=quiet_ms)
            if st2 and st2.get("domQuiet"):
                return
            time.sleep(poll_interval)

        # Cap reached; accept minor DOM churn and proceed
        logger.debug("wait_xhr: DOM quiet cap reached, proceeding")
        return

    logger.debug(f"Page was not ready after {timeout} seconds. Trying to continue..")
