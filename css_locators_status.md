# css= locators: implementation status

Spec: [css_locators_spec.md](css_locators_spec.md). Branch: `support_css_selectors`. Local commits only, never push.
Remove or move this file and the spec before opening the PR.

## How to resume

1. Read the spec, then this file.
2. Check `git log --oneline master..support_css_selectors` for the phase commits.
3. Continue with the first unchecked phase below.
4. Never stage the user's local change in `QWeb/__init__.py` (commented-out `Dialogs` import). When a phase changes that file, stage only your own lines, e.g. with `git diff QWeb/__init__.py > p.patch`, edit the patch, then `git apply --cached p.patch`.

## Environment

* Python: pyenv 3.13.14 (`~/.pyenv/versions/3.13.14/bin/python`), with `requirements_test.txt` installed by the user.
* QWeb is installed with `pip install -e .`, so Selenium and the other runtime dependencies are there.
* pylint 2.17.7, as pinned in `requirements_test.txt`, crashes on Python 3.13 (astroid `visit_typealias`). CI runs static analysis on Python 3.11, so run pylint there, or treat a pylint crash on 3.13 as an environment issue.
* Python 3.11.15 has Robot Framework 7.4.1 and QWeb, but no test tools.
* Acceptance tests need Chrome and chromedriver.

## Phases

- [ ] **Phase 1: parser, exception, unit tests**
  - [x] `QWebInvalidSelectorError` in `QWeb/internal/exceptions.py`
  - [x] `parse_locator` in `QWeb/internal/locator.py`
  - [x] unit tests in `test/unit/test_locator.py`
  - [x] ruff check and ruff format pass on the new files
  - [x] pytest passes (112 unit tests on 3.13); mypy and ruff are clean except the local `Dialogs` change
  - [ ] commit
- [ ] **Phase 2:** light-DOM CSS in the element search, syntax check before the frame search (fails at once), not-found retries, frames, `tag=` / `selector=` ignored with a warning, acceptance tests
- [ ] **Phase 3:** `:has-text` / `:text-is` filter in JS, innermost wins, acceptance tests
- [ ] **Phase 4:** Shadow DOM CSS search and tests
- [ ] **Phase 5:** route `element_type=css` through the new path, with a deprecation warning
- [ ] **Phase 6:** docstrings, `docs/concepts/locators.md`, `docs/concepts/shadow_dom.md`
- [ ] **Phase 7:** full lint (ruff, mypy, flake8, pylint on 3.11) and the full acceptance run

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
