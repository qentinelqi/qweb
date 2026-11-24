# Feature spec: `css=` locators for QWeb *Element keywords (revised)

Status: decisions settled, ready to hand to a coding agent. Hand it everything from "Why" to "Before coding".

## Why

QWeb's *Element keywords (`ClickElement`, `VerifyElement`, …) take only XPath locators. Many testers, and most AI agents, find CSS selectors shorter and easier to read for the elements QWeb's text-first keywords can't reach.

* Browser devtools copy a CSS selector in one click ("Copy selector").
* CSS is the usual locator syntax in Selenium, Playwright and Browser library, so teams moving to QWeb already know it.
* Readable scripts matter: `css\=button.primary` reads better than `//button[contains(@class,'primary')]`.
* CSS can search open Shadow DOM, which XPath can't.

## What (behavior)

The keywords listed below accept a locator that starts with `css\=` and find elements by that CSS selector. Everything else about the keyword stays the same.

* `css\=<selector>`: find elements with that CSS selector.
* Bare XPath (`//…`, `(//…)[4]`), `xpath\=…` and the named argument `xpath=…`: unchanged.
* The prefix is case-sensitive and matched only at the start of the locator, after stripping leading whitespace: lowercase `css=`, like `xpath=`.
* With `css=`, the keyword keeps its usual behavior: `timeout` and retries, `index`, frame handling, visibility rules, error messages and screenshots on failure.
* ClickElement clicks exactly the element the locator matches. Like XPath, it doesn't search for a clickable parent or child.

### Keywords in scope (v1)

All in `QWeb/keywords/element.py`:

| Keyword | First argument | Notes |
|---|---|---|
| ClickElement | `xpath` | `index` is 1-based |
| RightClick | `xpath` | `index` is 1-based |
| HoverElement | `xpath` | `index` is 1-based |
| IsElement | `xpath` | |
| VerifyElement | `xpath` | |
| VerifyNoElement | `xpath` | |
| GetElementCount | `locator` | |
| GetWebElement | `locator` | only when `element_type` isn't given |
| GetAttribute | `locator` | only when `element_type` isn't given |
| VerifyAttribute | `locator` | only when `element_type` isn't given |
| GetCoordinates | `locator` | only when `element_type` isn't given |

Out of scope for v1, possible follow-up: the other keywords that accept XPath as an alternative to text. These are TypeText and the input keywords, the dropdown and checkbox keywords, UseList, UseTable, DragDrop, CaptureIcon, UseFrame and GetText.

### Argument name and escaping

* The first argument keeps its current name (`xpath` or `locator`) and stays required. Signatures in libdoc and RobotCode don't change.
* `css\=` must be escaped. An unescaped `ClickElement    css=div.card` is rejected by Robot Framework before QWeb runs: "expected 1 to 4 non-named arguments, got 0". QWeb can't improve that message, so the keyword docs must state the escaping rule clearly.
* Only the first `=` needs escaping: `css\=input[name="q"]` works. Split on the first `=` only.
* The argument's docstring changes to "XPath expression, or a CSS selector with the `css\=` prefix".
* In new documentation, show bare XPath and `css\=`. Keep `xpath\=` working, but don't feature the unescaped named form `xpath=`.

### `element_type=css` (deprecated)

GetWebElement, GetAttribute, VerifyAttribute and GetCoordinates already accept `element_type=css` with a bare selector. It stays supported but is deprecated:

* Route it internally through the same path as `css\=`, by prefixing the locator. Both forms then behave the same: text filters, Shadow DOM, and failing at once on invalid syntax. Failing at once is a small behavior change for this form; note it in the changelog.
* Log a deprecation warning (`logger.warn`) once per run on first use: "element_type=css is deprecated, use the css\= prefix".
* Mark it as deprecated in those four docstrings, with a `css\=` example next to it.

### Acceptance criteria

1. Given a page with `<button class="primary">Save</button>`, when I run `ClickElement    css\=button.primary`, then the button is clicked.
2. Given a selector that matches nothing, when I run `VerifyElement    css\=#missing    timeout=2s`, then it retries for about 2 s and fails with `QWebElementNotFoundError`. The message shows the locator including `css=`.
3. Given three matching elements, when I run `ClickElement    css\=li.item    index=2`, then the second one is clicked.
4. Given an invalid selector such as `css\=div[`, when any in-scope keyword runs, then it fails at once with an "invalid CSS selector" message that shows the selector, without waiting for the timeout.
5. Given a valid selector whose element appears after 1 s, when I run `VerifyElement    css\=#late    timeout=5s`, then it passes. Only invalid syntax fails at once.
6. Given a matching element inside an iframe, when I run `ClickElement    css\=#in-frame`, then it is found and clicked, the same as with XPath.
7. Given existing XPath tests, when the full test suite runs, then all of them still pass unchanged. This includes the unescaped `xpath=` tests in `test/acceptance/parallel/element.robot`.
8. Given `GetWebElement    button.primary    element_type=css`, then it still works and logs a deprecation warning.
9. Given the keyword docs, when I open the documentation of each in-scope keyword, then it shows a `css\=` example next to the XPath one and states the escaping rule.

### Examples

```robotframework
*** Test Cases ***
CSS Locators In Element Keywords
    ClickElement     css\=button.primary
    VerifyElement    css\=#user-menu > li:nth-child(2)
    ClickElement     css\=input[name="email"]
    ClickElement     css\=li.item    index=2
    ${count}=        GetElementCount    css\=li.item

XPath Still Works
    ClickElement     //button[@id="save"]
    ClickElement     (//li[@class="item"])[2]
    ClickElement     xpath\=//div[@class="user-menu"]//button
    ClickElement     xpath=//div[@class="user-menu"]//button
```

## Text filters inside the `css=` locator

Plain CSS can't match on text, so `css=` gets two pseudo-classes, written inside the locator string:

* `:has-text("…")`: visible text **contains** the given text.
* `:text-is("…")`: whole visible text **equals** the given text.

They use the Playwright names, but not Playwright's matching rules (see below).

### Behavior

* QWeb strips the filter, runs the rest of the selector through the normal CSS search, then keeps only the matches whose text passes the filter.
* The text used is `innerText`, trimmed, with runs of whitespace collapsed to one space. The filter text is normalized the same way.
* **Matching is always case-sensitive.** The `PartialMatch` and `CaseInsensitive` settings and the `partial_match` argument don't affect these filters. The pseudo-class alone chooses between a substring match (`:has-text`) and an exact one (`:text-is`).
* Anchor texts given in an `anchor` argument are still found by text search, so they keep following `PartialMatch` and `CaseInsensitive`. Only the filter inside the locator ignores them.
* **Innermost match wins.** If one match contains another match, for example a wrapper card around an inner card, drop the outer one. `index` is applied after that.
* Zero matches after filtering is treated like any missing element: QWeb retries until the timeout, then fails. It never falls back to an unfiltered match.
* v1 allows one filter per locator, only at the end: `div.card:has-text("Hello")` works. `div.card:has-text("Hello") > button` and two filters are refused at once as invalid syntax.
* The filter text can be in double or single quotes. Single quotes avoid escaping when the text contains double quotes: `:has-text('Say "hi"')`. Inside the quotes, a backslash escapes the next character. In Robot Framework source, a literal backslash must be written as `\\`, so an escaped quote is written `:has-text("Say \\"hi\\"")`.
* An XPath locator is never parsed for these filters.

### Acceptance criteria

1. Given three `div.card` elements, one containing "Hello", when I run `ClickElement    css\=div.card:has-text("Hello")`, then that card is clicked.
2. Given no card contains "Hello", when I run `VerifyElement    css\=div.card:has-text("Hello")    timeout=2s`, then it fails after about 2 s and the message shows both the selector and the text.
3. Given cards with the texts "Hello" and "Hello world", then `:text-is("Hello")` matches only the first, and `:has-text("Hello")` matches both.
4. Given a card with the text "hello", then `:has-text("Hello")` doesn't match it, even with `SetConfig    CaseInsensitive    True` or `PartialMatch    False`.
5. Given text containing quotes, then `:has-text('Say "hi"')` and `:has-text("Say \\"hi\\"")` both match `Say "hi"`.
6. Given a wrapper `div.card` that contains an inner `div.card`, both containing "Hello", then `css\=div.card:has-text("Hello")` matches only the inner card.
7. Given `css\=div.card:has-text("Hello") > button`, then the keyword fails at once with an invalid-selector message.
8. Given any XPath locator, then the text filters have no effect and XPath behavior is unchanged.

## Shadow DOM

With `SetConfig    ShadowDOM    True`, `css=` locators also search open shadow roots. XPath behavior under `ShadowDOM` doesn't change: XPath still can't reach shadow content.

### Behavior

* With `ShadowDOM` off, use Selenium's `By.CSS_SELECTOR`, light DOM only.
* With `ShadowDOM` on, use one JavaScript call. It reuses `recursiveWalk` (`QWeb/internal/js/get_recursive_walk.js`) to collect the search root plus every open `shadowRoot` under it. It then runs `root.querySelectorAll(selector)` on each root and returns the results without duplicates, in walk order. The search root is the active-area element, the same container the XPath search uses.
* Results go through the same visibility check, text filters and `index` as light-DOM results.
* Selectors work when all their parts are in the same tree: `button.primary`, `#id`, `div.card > span` inside one shadow root. Light-DOM content placed into shadow slots is found as normal light-DOM content.
* Limits, to document: a selector can't cross a shadow boundary. `my-host .inner`, where `.inner` is inside `my-host`'s shadow root, doesn't match. Crossing a boundary would need Playwright-style `>>` chaining, which is out of scope. `::part()` and `::slotted()` aren't supported, and closed shadow roots aren't reached.

### Acceptance criteria

1. Given an element inside an open shadow root, when `ShadowDOM` is on and I run `ClickElement    css\=<selector>`, then it is clicked.
2. Given the same element with `ShadowDOM` off, then `VerifyNoElement    css\=<selector>` passes.
3. Given `:has-text` on a shadow element with `ShadowDOM` on, then filtering works the same as in the light DOM.
4. Given a selector that crosses a shadow boundary, then it doesn't match. This test documents the limit.

## Errors and timing

* **Invalid syntax fails at once.** This covers a malformed selector, a misplaced or malformed text filter, and an empty selector (`css\=`).
  * Raise a new exception, e.g. `QWebInvalidSelectorError`, derived from `QWebException`. It must **not** derive from `QWebValueError` or `QWebElementNotFoundError`, because `timeout_decorator` retries both.
  * Check the syntax once, in the top-level document, before the frame search starts. The syntax is the same in every frame, and raising inside a child frame would leave the driver in that frame, because `frame.all_frames` doesn't switch back on other exceptions.
  * The message shows the selector.
* **Not found retries until the timeout.** A valid selector that matches nothing, or matches nothing after filtering, is retried until `timeout` / `DefaultTimeout`. It then fails with the usual `QWebElementNotFoundError`. Inner messages say "Locator css=… did not find any elements" instead of "XPath … did not find".
* **Invalid XPath is unchanged.** It keeps retrying until the timeout, as today.

## Out of scope / do not change

* The text-based keywords (`ClickText`, `TypeText`, `ClickItem`, …) and their search logic.
* The `css=False/off` kwarg of the text keywords. It turns off the clickable-first search; leave it as is.
* The `CssSelectors` config option, which controls the text-based input search.
* Default locator handling: a bare locator without a prefix is still XPath. No guessing whether a string "looks like CSS".
* Unescaped `css=` as a named argument, and any change to the first argument's name or default.
* Other locator strategies (`id=`, `name=`, `>>` chains), and `:text-is` / `:has-text` with XPath.
* Known issue, not part of this change: ClickElement, RightClick and HoverElement don't pass `**kwargs` to the element search, and VerifyNoElement doesn't either. So kwargs like `visibility=False` are ignored there. CSS inherits the same behavior.
* Refactoring unrelated code, renaming public keywords or arguments, reformatting files.
* New dependencies.

## Constraints and edge cases

### Constraints

* Put prefix parsing in one place: a `parse_locator(locator) -> (strategy, value, text_filter)` helper in `QWeb/internal/element.py`. Call it from the two shared search functions, `get_unique_element_by_xpath` and `get_webelements`. Don't copy it into each keyword.
* Today the `xpath=` check is copied in about 10 places (`element.py`, `input_.py`, `lists.py`, `dragdrop.py`, `dropdown.py`, `checkbox.py`, `table.py`, `text.py`, `util.xpath_validator`). Leave the out-of-scope ones alone.
* Use Selenium's own `By.CSS_SELECTOR`, plus a JS file in `QWeb/internal/js/` for the Shadow DOM search and the text filter. Don't add a selector library.
* Do the text filter and the innermost-wins step in one JavaScript call over all candidates. Don't use one `.text` call per element.
* Fully backward compatible: no existing test may change behavior.
* Match the existing code style, type hints and docstring format.

### Edge cases

* Leading or trailing whitespace around the locator and the selector is stripped.
* `=` inside the selector, as in `css\=input[name="q"]`: split on the first `=` only.
* `tag=` combined with `css=`. `tag=` switches to attribute search, where the locator is an attribute value. With a `css=` locator, ignore `tag=`, use the CSS selector, and log a warning: "tag= is ignored with a css= locator; put the tag in the selector, e.g. css\=button.primary". The keyword must not fall into the attribute search.
* `selector=` combined with `css=`. `_xpath_decorator` in `QWeb/__init__.py` would build `//*[@attr="css=…"]` from it. For the in-scope keywords only, when the first argument starts with `css=`, skip the XPath building, drop `selector=`, and log a warning: "selector= is ignored with a css= locator". All other keywords keep today's behavior.
* Hidden elements follow the same visibility rules as XPath: `Visibility`, `InViewport`, `OffsetCheck`.
* iframes use the same `frame.all_frames` handling as XPath, including `StayInCurrentFrame`.
* The active area, `ActiveAreaXpath` or `ACTIVE_AREA_FUNCTION`: CSS is searched inside the active-area element. The container itself is still found by XPath.
* `SearchMode` highlighting works for CSS matches.

## Context and verification

### Pointers

* Repo: qentinelqi/qweb.
* Element search: `QWeb/internal/element.py`. The functions are `get_unique_element_by_xpath` (line ~148), `get_webelements` (~184), `get_webelements_by_css` (~212, the existing CSS search, also searching all frames), `get_webelements_in_active_area` (~235) and `get_visible_elements_from_elements`.
* Keywords: `QWeb/keywords/element.py`. The `element_type=css` branch is in `get_webelement` (~521).
* Retry behavior: `QWeb/internal/decorators.py` (`timeout_decorator`, `_equal_sign_handler`).
* Frame search: `QWeb/internal/frame.py` (`all_frames`).
* JS helpers: `QWeb/internal/javascript.py`, `QWeb/internal/js/get_recursive_walk.js` and `get_visibility.js`.
* Exceptions: `QWeb/internal/exceptions.py`.
* Docs to update: `docs/concepts/locators.md` (section "Element Locators" and the keyword table) and `docs/concepts/shadow_dom.md`.

### Expected files to change

* `QWeb/internal/element.py`: the parser, CSS dispatch, Shadow DOM branch and text filter.
* `QWeb/internal/javascript.py` and new files in `QWeb/internal/js/`: the Shadow DOM CSS search and the text filter.
* `QWeb/internal/exceptions.py`: `QWebInvalidSelectorError`.
* `QWeb/keywords/element.py`: docstrings, and the `element_type=css` deprecation and routing.
* `QWeb/__init__.py`: `_xpath_decorator` skips `selector=` for `css=` locators on the in-scope keywords. Don't stage the unrelated local `Dialogs` import change in this file.
* `docs/concepts/locators.md` and `docs/concepts/shadow_dom.md`.
* Tests: see below.

### Tests

* Unit tests (new `test/unit/test_locator.py`, or in `test/unit/test_element.py`) for `parse_locator`:
  * `xpath=`, bare `//`, `(//…)[n]` and `css=`
  * `=` inside the selector
  * whitespace
  * `:has-text` / `:text-is` with both quote styles and escaped quotes
  * a misplaced filter, two filters, an empty selector
* Acceptance tests in `test/acceptance/parallel/` for the light-DOM criteria: extend `element.robot` or add `css_locators.robot`. Use existing test pages where they fit, otherwise add a small page in `test/resources/`.
* Shadow DOM tests in `test/acceptance/serial/shadow_dom.robot`, using `test/resources/shadow_dom.html` (open shadow roots), extended if needed.
* iframe test using an existing frame page (e.g. `frame.html`).

### Commands (from CI)

```bash
pytest -v --cov=QWeb
```

```bash
ruff format QWeb && ruff check QWeb && mypy --show-error-codes QWeb && pylint QWeb
```

```bash
flake8 QWeb --count --select=E9,F63,F7,F82 --show-source --statistics
```

```bash
python -m robot -v BROWSER:chrome test/acceptance/parallel/element.robot
```

```bash
python test/acceptance/pabot_suite_ordering.py QWeb && python -m pabot.pabot --ordering test/acceptance/.pabot_order -e jailed -v BROWSER:chrome test/acceptance
```

The acceptance tests open pages from `test/resources` through `file://` by default. CI serves that folder on port 8000 instead, with `-v ON_HTTP_SERVER:True`.

## Before coding

Reply with:
* the files you will change, confirming or correcting the list above
* the `parse_locator` design, with its return type and the error cases
* how the Shadow DOM search and the text filter are split between Python and JavaScript
* your test plan, mapped to the acceptance criteria

Wait for approval before writing code.
