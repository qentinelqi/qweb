# Browser Management in QWeb

While QWeb handles driver downloads and management automatically you often need to customize *how* the browser launches, handle multiple tabs, or manage cookies.

## 1. Opening & Configuring Browsers (`OpenBrowser`)

Basic usage:

```robot
OpenBrowser    https://example.com    chrome
```

Beyond this, `OpenBrowser` supports powerful configuration options.

---

### 1.1 Using Chrome Preferences (`prefs=`)

Chrome allows fine-grained configuration via preference settings.

#### Example: Download PDFs instead of opening in browser

```robot
OpenBrowser    about:blank    chrome
...    prefs=download.prompt_for_download: False, plugins.always_open_pdf_externally: True
```

Useful when:

- Testing file downloads
- Preventing in-browser PDF viewer from intercepting files

---

#### Example: Disable Chrome Autofill Dialogs

```robot
OpenBrowser    about:blank    chrome
...    prefs="autofill.profile_enabled":false, "autofill.credit_card_enabled":false
```

Useful when:

- Testing checkout flows
- Avoiding browser popups interfering with automation

---

### 1.2 Controlling Window State

#### Window Size

By default, Chromium-based browsers open maximized.

To disable automatic maximization:

```robot
OpenBrowser    about:blank    chrome    maximize=False
```

This is useful when:

- Testing responsive layouts
- Running controlled viewport tests

You can also change the window size during runtime using SetConfig:

```robot
SetConfig    WindowSize     1920x1080
```
#### Headless mode

To open browser in headless mode, use:

```robot
OpenBrowser   about:blank   Chrome   headless=True

# alternative
OpenBrowser   about:blank   Chrome   --headless
```


---

### 1.3 Mobile Emulation

Simulate mobile devices without external tools.

#### Named device profile

```robot
OpenBrowser    http://google.com    chrome    emulation=iPhone SE
```

#### Custom resolution

```robot
OpenBrowser    http://google.com    chrome    emulation=375x812
```

Useful for:

- Responsive UI testing
- Mobile layout validation

### 1.4 Running on Selenium Grid (`remote_url=`)

Execute tests remotely via Selenium Grid.

```robot
OpenBrowser    http://google.com    chrome    remote_url=http://127.0.0.1:4444/wd/hub
OpenBrowser    http://google.com    safari    remote_url=http://127.0.0.1:4444/wd/hub
```

Useful when:

- Running tests in distributed environments
- Using Dockerized Selenium Grid
- Executing cross-browser tests

---

## 2. Navigation and URLs

Once the browser is open, you can navigate without having to close and reopen it.

```robot
GoTo
Back
Forward
RefreshPage
```

Example:

```robot
GoTo    https://example.com/dashboard
RefreshPage
```

**Checking State**
You can retrieve or assert the current URL and Title.

```robotframework
# Get values into variables
${title}=     GetTitle
${url}=       GetUrl

# Verify state directly
VerifyTitle   Expected Page Title
VerifyUrl     https://example.com/login
```

## 3. Managing Windows and Tabs

### Switching Browers & Windows
You can open multiple browser instances and move between them.

```robotframework
OpenBrowser     https://example.com   Chrome
OpenBrowser     https://www.github.com  Firefox
# Firefox is now the "active" browser
VerifyText      GitHub

# Switch by index
SwitchBrowser     1
VerifyText    Example Domain

# Switch to latest opened browser (here GitHub)
SwitchBrowser   NEW
VerifyText      GitHub
```

When clicking a link opens a new tab, you need to explicitly switch QWeb's focus to it. The easiest and most reliable way is using the `NEW` argument.

```robotframework
ClickText       Open in new tab
SwitchWindow    NEW
VerifyText      Welcome to the new tab!
```
You can also switch by index (e.g., `SwitchWindow    1` for the original tab) or by the internal window handle (`ListWindows`).



### Listing Information
If your test gets lost in multiple popups, you can log the current state to your report to debug:

```robotframework
# Logs information about all open tabs
ListWindows

# Logs about all opened browser instances
ListBrowsers
```

## 4. Cookies

Managing cookies is crucial for testing varying login states or bypassing repetitive setups.

```robotframework
# Read current cookies
${cookies}=         GetCookies

# Clear state (Great for 'Suite Teardown' or 'Appstates')
DeleteAllCookies
```

## 5. Closing Browsers

Always clean up at the end of your tests to prevent memory leaks or zombie processes. This is typically done in your `Test Teardown` or `Suite Teardown`.

```robotframework
# Closes ONLY the currently active tab/window
CloseWindow

# Closes all other tabs/windows except the first one
CloseOthers

# Closes the active browser application
CloseBrowser

# Closes ALL browsers opened during the test run
CloseAllBrowsers
```



