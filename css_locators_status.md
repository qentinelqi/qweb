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
- [ ] **Phase 3:** `:has-text` / `:text-is` filter in JS, innermost wins, acceptance tests
- [ ] **Phase 4:** Shadow DOM CSS search and tests
- [ ] **Phase 5:** route `element_type=css` through the new path, with a deprecation warning
- [ ] **Phase 6:** docstrings, `docs/concepts/locators.md`, `docs/concepts/shadow_dom.md`
- [ ] **Phase 7: locator guide in the keyword documentation** (requested by the user; done after all features)
  - Where: the library intro docstring in `QWeb/__init__.py` (section `.. _Locators:` "Locator strategies", ~line 118), which libdoc shows at the top of the keyword docs. Rework that section; don't add a second one.
  - Explain the idea first: QWeb has **separate keyword families per locator type**, so the locator string needs no type prefix and QWeb never guesses. Each family has search rules suited to its type, and the keyword name tells the reader what is being matched.
  - **\*Text** (ClickText, VerifyText, HoverText, IsText, GetText, ClickWhile/ClickUntil, …): visible UI text. Clickable elements are preferred for click keywords, plus `anchor`, `PartialMatch` and `CaseInsensitive`. The preferred locator type.
  - **\*Item** (ClickItem, VerifyItem, HoverItem, IsItem, ClickItemWhile/ClickItemUntil): one attribute value of an element without visible text: `title`, `alt`, `aria-label`, `data-tooltip`, `tooltip`, `data-icon` (see `text.get_item_using_anchor`). Typical for icons and image buttons.
  - **\*Element** (ClickElement, VerifyElement, VerifyNoElement, IsElement, RightClick, HoverElement, GetElementCount): an exact technical locator, XPath (default) or `css\=`. Escape every `=`. Also `tag=`, to match any attribute value on a given tag.
  - **\*Icon:** image comparison (keep the existing part).
  - **Keywords that work with several types:**
    * GetWebElement, GetAttribute, VerifyAttribute and GetCoordinates take XPath or `css\=` by default, and text, item, input, dropdown or checkbox with `element_type`.
    * The input, dropdown and checkbox keywords (TypeText, DropDown, ClickCheckbox, …) take a label text, an attribute value or an XPath.
  - Add a short "which one to use" order: Text → Item → Element (CSS or XPath) → Icon.
  - Keep and cross-link the existing Anchors and Shadow DOM sections. Shadow DOM: Text and Item work there, and `css=` works with basic selectors; XPath doesn't.
  - Show one short example per family, with escaped `=`.
  - Check that libdoc renders it: `python -m robot.libdoc QWeb <out>/QWeb.html`, then open the HTML.
  - Mirror the guide in `docs/concepts/locators.md` (the mkdocs site), as the user decided. Same content, adapted to Markdown; keep the two in sync.
- [ ] **Phase 8:** full lint (ruff, mypy, flake8, pylint on 3.11) and the full acceptance run

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
