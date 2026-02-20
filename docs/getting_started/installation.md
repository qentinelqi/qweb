# Installation & Setup

## Requirements

Before installing QWeb, ensure your environment meets the following requirements:

*   **Python:** Versions 3.10 – 3.13
*   **Robot Framework:** Version 5.0.1 or above

!!! warning "macOS Apple Silicon (M1/M2/M3)"
    Support for Macs with Apple Silicon requires **macOS 12 (Monterey)** or above. If you are on an older version, a custom installation may be required.

## Installation

Select your operating system below for specific instructions.

=== "Windows"

    Installing QWeb on Windows is straightforward via pip. Open your command prompt or PowerShell and run:

    ```bash
    pip install QWeb
    ```

=== "Linux / macOS"

    ### 1. System Dependencies
    On Linux (specifically Ubuntu/Debian), you may need to install system-level dependencies for image comparison and GUI support:

    ```bash
    sudo apt-get install python3-tk python3-dev scrot
    ```

    ### 2. Install QWeb
    Once dependencies are ready, install the library:

    ```bash
    python3 -m pip install -U pip
    python3 -m pip install QWeb
    ```

    !!! failure "Avoid Snap Packages"
        Some Linux distributions (like Ubuntu) install browsers via **Snap** by default. This often causes issues with automation due to non-standard binary paths and sandboxing.
        
        **Recommendation:** Install Google Chrome via the terminal instead:
        ```bash
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        sudo apt-get install -y ./google-chrome-stable_current_amd64.deb
        ```

## Browser Drivers

QWeb relies on **Selenium Manager** (available since Selenium 4.10.0) to automatically handle browser drivers.

### Automatic Management (Preferred)
You do **not** need to manually download `chromedriver` or `geckodriver`.

1.  Ensure you have a supported browser installed (Chrome, Firefox, Edge).
2.  Run your test.
3.  Selenium Manager will detect your browser version and automatically download the correct driver to your cache.

### Chrome for Testing
If you need a specific browser version for testing that doesn't match your installed version, QWeb supports **Chrome for Testing**.
*   If you specify a `browser_version` in `OpenBrowser`, and your local Chrome matches it, QWeb uses the local version.
*   If they do not match, QWeb will automatically download the standalone "Chrome for Testing" binary for that specific version.

!!! info "Manual Driver Management"
    Manual driver management (downloading binaries and adding them to PATH) is supported but **not recommended**. It is brittle and requires constant maintenance as browsers update. Only use manual management in exceptional cases (e.g., air-gapped internal networks).