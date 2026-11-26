# css= locators: implementation status

Spec: [css_locators_spec.md](css_locators_spec.md). Branch: `support_css_selectors`. Local commits only, never push.
Remove or move this file and the spec before opening the PR.

## How to resume

1. Read the spec, then this file.
2. Check `git log --oneline master..support_css_selectors` for the phase commits.
3. Continue with the first unchecked phase below.
4. The user's old local `Dialogs` workaround in `QWeb/__init__.py` is gone: the optional-tkinter fix is merged (59c2b5d). `QWeb/__init__.py` can be committed normally.
5. Don't run `ruff format` on whole files: it reformats unrelated existing code, which the spec forbids. Format only new files, or check that `git diff` shows only your own lines.

## Environment

* Python: pyenv 3.13.14 (`~/.pyenv/versions/3.13.14/bin/python`), with `requirements_test.txt` installed by the user.
* QWeb is installed with `pip install -e .`, so Selenium and the other runtime dependencies are there.
* pylint 2.17.7, as pinned in `requirements_test.txt`, crashes on Python 3.13 (astroid `visit_typealias`). CI runs static analysis on Python 3.11, so run pylint there, or treat a pylint crash on 3.13 as an environment issue.
* Python 3.11.15 has Robot Framework 7.4.1 and QWeb, but no test tools.
* docutils 0.23 was installed in pyenv 3.13.14 (needed for `libdoc -F REST`, as used by `duties.py`).
* Chrome 158 and Selenium Manager's chromedriver work. Run acceptance suites from the repo root through the top suite, so `__init__.robot` sets `${BASE_URI}`:
  `python -m robot -d <out> -v BROWSER:chrome --suite "Css Locators" test/acceptance`

## Phases

- [x] **Phase 1: parser, exception, unit tests**
  - [x] `QWebInvalidSelectorError` in `QWeb/internal/exceptions.py`
  - [x] `parse_locator` in `QWeb/internal/locator.py`
  - [x] unit tests in `test/unit/test_locator.py`
  - [x] ruff check and ruff format pass on the new files
  - [x] pytest passes (112 unit tests on 3.13); mypy and ruff are clean except the local `Dialogs` change
  - [x] commit (19f33b3)
- [x] **Phase 2: light-DOM CSS search**
  - [x] `get_webelements` is a wrapper that checks `css=` syntax, then calls the frame-decorated `_get_webelements_from_frames`
  - [x] `get_unique_element_by_xpath` checks the syntax, then `get_webelements_in_active_area` searches with `By.CSS_SELECTOR`
  - [x] `javascript.get_css_selector_error`: syntax check on an empty document fragment, in the current frame, with no frame switching
  - [x] `tag=` / `selector=` dropped with a warning in `QWeb._xpath_decorator` (`_drop_kwargs_ignored_with_css`)
  - [x] test page `test/resources/css_locators.html` (+ `css_locators_frame.html`) and suite `test/acceptance/parallel/css_locators.robot` (18 tests)
  - [x] the css, Element, Selectors, Frame and Text suites pass (133 tests); unit tests, ruff check, mypy and flake8 (E9/F) pass
  - [x] all parallel suites: 415/420 pass with pabot; the same 5 fail without these changes (environment: screenshot paths under pabot, the debugfile test needs `-b debug.txt`, and ClearKey/PressKey hotkeys on macOS)
  - [x] commit (72a1fd9)
- [x] **Phase 3: `:has-text` / `:text-is` filters**
  - [x] `QWeb/internal/js/filter_by_text.js` + `javascript.filter_elements_by_text`: normalized `innerText`, case-sensitive, substring or exact match, innermost wins; one JS call for all candidates
  - [x] `element.get_css_elements(search_root, locator)`: `find_elements(By.CSS_SELECTOR)` → visibility check → text filter. Used by both the frame search and the active-area search
  - [x] removed the Phase 2 "not supported yet" error
  - [x] 10 new acceptance tests (cards, nested cards, quotes, whitespace, case and `PartialMatch`/`CaseInsensitive`, timeout, misplaced filter, frame, XPath unaffected); the css, Element, Selectors and Frame suites pass (83 tests); unit tests, ruff and mypy pass
  - [x] commit (see `git log`)
- [x] **Phase 4: Shadow DOM CSS search**
  - [x] `QWeb/internal/js/get_css_elements_from_shadow_dom.js` + `javascript.get_css_elements_from_shadow_dom`: `recursiveWalk` collects the search root and every open shadow root under it, then runs `querySelectorAll` on each tree separately
  - [x] `element.get_css_elements` uses it when `ShadowDOM` is on (the root is the active-area element, or the document in the frame search); otherwise `By.CSS_SELECTOR`. Visibility and text filters apply the same way
  - [x] 6 new tests in `test/acceptance/serial/shadow_dom.robot`: setting off/on, click/count/attribute, text filters, boundary limit, invalid syntax at once, XPath unchanged. The suite passes (16 tests); css + Element (65) and unit tests pass; ruff and mypy pass
  - [x] commit (see `git log`)
- [x] **Phase 5: `element_type=css` deprecated**
  - [x] the `get_webelement` branch prefixes the locator with `css=` (unless it already has one) and uses `element.get_webelements`. So it fails at once on invalid syntax and supports text filters and Shadow DOM. `element.get_webelements_by_css` is no longer used; it's kept for external callers
  - [x] deprecation warning once per run (`_warn_element_type_css_deprecated` in `QWeb/keywords/element.py`)
  - [x] marked as deprecated in the GetWebElement, GetAttribute, VerifyAttribute and GetCoordinates docstrings; the CSS examples now use `css\=` with escaped `=` (the old examples had unescaped `=`, which Robot Framework would treat as a named argument)
  - [x] 2 new tests in `css_locators.robot`; the existing `element_type=css` tests in `element.robot` pass unchanged (css + Element: 67 tests); unit tests, ruff and mypy pass
  - [x] commit (see `git log`)
- [x] **Phase 6: docs**
  - [x] new library intro section "CSS locators" (`.. _Css_locators:`, before Shadow DOM in `QWeb/__init__.py`): prefix, escaping, behavior, `tag`/`selector`, deprecation, text filters, Shadow DOM. Also a feature-list entry, the "Xpaths and CSS selectors" subsection with its caution, and the Shadow DOM section text and tip
  - [x] docstrings of the 11 keywords: `css\=` examples, locator parameter text, links `` `CSS locators <#css-locators>`_ `` (libdoc doesn't link backtick names to reST sections). Summaries of ClickElement and HoverElement; HoverElement's unescaped `=` example fixed
  - [x] `docs/concepts/locators.md` (XPath or CSS section, text filters, notes, escaping tip, table) and `docs/concepts/shadow_dom.md` (CSS in Shadow DOM, fixed escaping in examples)
  - [x] checks: libdoc `-F REST` builds without docutils system messages; the intro heading and the `css-locators` id exist, and all 10 keyword links point to `#css-locators`; a dry run of all 35 `css\=` doc examples passes; unit tests, ruff and mypy pass
  - [ ] not verified: clicking the links in a real browser. The browser pane can't open local files here, so check the links in `docs/QWeb.html` after the next `duty docs` build
  - [x] commit (see `git log`)
- [x] **Phase 7: locator guide** (requested by the user)
  - [x] "Locator strategies" in the `QWeb/__init__.py` intro reworked: a "One keyword family per locator type" table (Text / Item / Element / Icon) and the reasons (search rules per type, no prefix or guessing, readable intent, settings per family), then the order of preference. The Item description now matches the code: any attribute value of common tags (`text._get_item_by_css`), plus `tag`. New "Keywords that work with several locator types" part (input/dropdown/checkbox keywords, GetWebElement and friends with `element_type`, *Element with `tag`). Fixed the `hrrps://` typo in an existing example
  - [x] mirrored in `docs/concepts/locators.md`: family table and reasons at the top, Item attribute list corrected, the "Summary" section replaced by "5. Keywords that work with several locator types" (the table moved to the top)
  - [x] checks: libdoc `-F REST` with 0 system messages and the table renders; dry run of the new examples and of all 35 `css\=` doc examples passes; ruff and mypy pass
  - [x] commit (see `git log`)
- [x] **Phase 8: full lint and acceptance run**
  - [x] ruff check, mypy, flake8 (E9/F63/F7/F82) and pylint 2.17.7 on Python 3.11 (installed in pyenv 3.11.15 for this) all pass; pylint gives 10.00/10 with no messages, same as master. Fixed one long docstring line
  - [x] flake8 complexity (non-blocking CI step): split `locator._parse_css` (was 20) and moved the search out of `element.get_webelements_in_active_area` (was 12), so neither is flagged now. The E203 slice is gone. The remaining new note, `QWeb._run_on_failure_decorator` (11), comes from the merged tkinter fix, not this work
  - [x] full acceptance run with pabot and the CI suite ordering (Chrome, macOS, `-b debug.txt`): 505/516 pass. All 11 failures are environmental or flaky: 10 fail the same way on master (Dragdrop ×6, Browser Windowed ×3, Input Windowed ×1), and "Verify File Download Slow Bandwidth" timed out only under parallel load and passes when run alone
  - [x] after the refactor: css, Element, Shadow Dom, Selectors, Frame and Download suites pass (105 tests); unit tests (114) pass; libdoc `-F REST` has 0 system messages
  - [x] commit (see `git log`)

## Rebase on master (2026-11-26)

* Rebased onto `origin/master` b04292e (PRs #233 virtual checkbox fallback and #234 test fixes) with no conflicts. History is now linear: the tkinter merge commit is gone and its commit (`Make robot Dialogs import optional…`) sits in the chain. The old tip is kept as the local branch `support_css_selectors-before-rebase`.
* After the rebase: 123 unit tests; ruff, mypy, flake8 (E9/F) and pylint (3.11) pass; Css Locators, Element, Shadow Dom, Virtual Checkbox, Checkbox, Input Headless, Selectors, Frame and Text pass, except 3 Element tests in a combined single-process run.
* Those 3 (Hover Element by WebElement instance, GetAttributeOK, VerifyAttributeOK) also fail on clean `origin/master` when Checkbox runs before Element in one process. `checkbox.robot` leaves `SetConfig CssSelectors off` at the end of a test, which breaks item lookups in later suites. With pabot (CI) each suite has its own process. Element passes 37/37 alone. This is an existing test-isolation issue, not part of this branch.

## Before opening the PR

* Remove or move `css_locators_spec.md` and this file.
* Add a changelog entry: new `css=` locators, `:has-text` / `:text-is`, Shadow DOM support for `css=`, `element_type=css` deprecated, and `element_type=css` with an invalid selector now failing at once.
* After the next `duty docs` build, click a `CSS locators` link in a keyword's docs in `docs/QWeb.html` (not verified in a browser here).
* Not tested on Firefox, Edge or Safari; CI covers them.

## Decisions made during implementation

These are not in the spec; review them.

* **Parser module:** the parser lives in its own module, `QWeb/internal/locator.py`, not in `element.py` as the spec says. It has no Selenium dependencies and is easy to unit-test. `element.py` will import it in Phase 2.
* **XPath input unchanged:** XPath strings are returned exactly as today. Only the `xpath=` prefix is removed, with no whitespace stripping. Whitespace is stripped only around `css=` locators.
* **Rejected at once (`QWebInvalidSelectorError`):**
  * an empty text filter (`:has-text("")`)
  * a text filter with no selector before it (`css=:has-text("x")`); the message suggests `css=*:has-text("x")`
  * a text filter combined with a top-level selector list (`css=a, b:has-text("x")`), because in CSS the filter would apply only to the last part
  * a text filter nested inside another pseudo-class (`:not(:has-text(...))`)
  * an unquoted filter text, a missing closing quote, or a missing closing parenthesis
* **Space or combinator before the filter:** `div :has-text("x")` and `div > :has-text("x")` mean any descendant or child, so the parser turns them into `div *` and `div > *`.
* **Text normalization:** the filter text is normalized in the parser (trimmed, whitespace collapsed). The element text will be normalized the same way in JS (Phase 3).
* **Syntax checked by the browser:** the parser only checks the prefix and the text-filter syntax. Whether the CSS selector itself is valid (e.g. `div[`) is checked by the browser in Phase 2.
* **Escaping (spec corrected):** every `=` in a locator must be escaped, not only the first: `css\=input[name\="q"]`. The keywords take `**kwargs`, so Robot Framework treats any unescaped `=` as a named argument. Confirmed with a dry run; the same applies to bare XPath.
* **Text filters before Phase 3:** a `css=` locator with `:has-text` / `:text-is` raises `QWebInvalidSelectorError` ("not supported yet") in `check_css_syntax`, so a filter is never silently ignored. Phase 3 replaces this.
* **Error message wording:** for `css=`, the inner messages of `get_unique_element_by_xpath` say "Locator css=… did not find any elements". XPath messages are unchanged.
* **CSS in the active area:** CSS is searched with `active_area.find_elements(By.CSS_SELECTOR, …)`, with no `.//` rewrite like XPath gets.
* **Where `tag=` / `selector=` are dropped:** in `QWeb._xpath_decorator`, the outermost keyword wrapper, so the warning is logged once per keyword call, not once per retry. It's limited to the keywords in `locator.CSS_LOCATOR_KEYWORDS` from `QWeb.keywords.element`, and it's skipped when `element_type` is given.
* **Filter order:** visibility check first, then the text filter and innermost-wins. A hidden inner match therefore doesn't remove its visible outer match.
* **For the Phase 6 docs:** (1) two or more spaces inside a filter text must be written with `${SPACE}`, because Robot Framework splits arguments on runs of spaces. (2) ClickElement clicks the center of the matched element, so clicking an outer card whose center is covered by a nested card hits the nested one. This is normal Selenium click behavior, the same as with XPath.
* **Shadow DOM result order:** light-DOM matches of the search root come first, then each shadow tree in walk order. `index` counts in that order.
* **Shadow DOM search root:** when the active area is an element, the walk starts there and also covers the element's own shadow root, if it has one.
* **Changelog note (behavior change):** `element_type=css` with an invalid selector now fails at once instead of waiting for the timeout.
