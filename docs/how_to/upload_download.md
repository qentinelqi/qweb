# File Uploads & Downloads in QWeb

File handling in UI automation often fails due to:

- Environment differences
- Browser security restrictions
- Hardcoded file paths
- OS-dependent download folders

QWeb provides dedicated upload and download keywords to make file handling stable and portable.

## 1. Uploading Files (`UploadFile`)

To upload a file to an `<input type="file">` element:

```robot
UploadFile    Upload Document    invoice.pdf
```

`UploadFile` interacts directly with the file input element and sets the file path programmatically.  

!!! warning "Do Not Click the Upload Button First"
    In many applications, clicking an “Upload” or “Browse” button opens a native operating system file selection dialog.
    Example of what NOT to do:

    ```robot
    ClickText    Upload
    ```

    Native OS file dialogs are **not automatable** by Selenium or QWeb.

    Instead, always use:

    ```robot
    UploadFile    Upload Document    invoice.pdf
    ```

    `UploadFile` targets the underlying `<input type="file">` element directly and bypasses the OS dialog entirely.

### Resolving Files by Filename (Recommended)

Pass only a filename when the file lives in a standard project folder:

```robot
UploadFile    Upload Document    invoice.pdf
```

QWeb resolves bare filenames through default folders instead of requiring
absolute paths. The same resolution applies to other file keywords such as
`VerifyFile`, `UseFile`, `UsePdf`, `ZipFiles`, and `MoveFiles`.

#### Search order

If the given name is not already an existing path, QWeb searches in this order:

1. User Downloads folder
2. Suite-local `files/` and `images/` near `${SUITE SOURCE}` (see below)
3. `files/` and `images/` anywhere under `%{TEST_WORKSPACE_ROOT}` (when set)
4. `files/` and `images/` anywhere under `${EXECDIR}`
5. `${BASE_IMAGE_PATH}` if defined

Step 3 applies when `%{TEST_WORKSPACE_ROOT}` is set (typical for cloud debug runs).
When the variable is unset, QWeb skips that step.

#### How `files/` and `images/` folders are found

QWeb walks a directory tree and uses the **first** folder named `files` or
`images` it encounters (usually the shallowest). Most projects should have one
`files/` folder and one `images/` folder. If several exist, only the first match
is used — pass a full path when you need a file from a specific folder.

#### Suite-local `files/` and `images/`

`${SUITE SOURCE}` points to the suite **file**, not its directory. QWeb looks
for `files/` and `images/` in the parent directory of the folder that contains
the suite file. This allows a nested test folder to use its own files before
any workspace-wide folder.

```text
my_project/
  tests/
    smoke/
      files/
        invoice.pdf
      accounts/
        create_account.robot
```

For `my_project/tests/smoke/accounts/create_account.robot`, QWeb checks
`my_project/tests/smoke/files/` first. The same rule applies when `files/` sits
at project root:

```text
my_project/
  files/
    invoice.pdf
  tests/
    smoke.robot
```

#### Cloud debug runs and `%{TEST_WORKSPACE_ROOT}`

Full suite runs usually start from the project root and resolve files correctly.
When a single test file is run in debug mode, `${EXECDIR}` points to that file's
directory instead of the project root, and the suite-relative lookup above may
no longer reach your `files/` folder.

Set the `TEST_WORKSPACE_ROOT` environment variable (available in tests as
`%{TEST_WORKSPACE_ROOT}`) to the project root before starting Robot:

```bash
export TEST_WORKSPACE_ROOT="/home/services/suite/CNS Tests"
robot Assessment/upload.robot
```

QWeb then searches for `files/` and `images/` under that root after Downloads
and suite-local folders. When the variable is unset, that step is skipped.

#### Recommended project layout

Store upload and reference files in suite-local or project-level folders:

```text
project/
  files/
    invoice.pdf
  images/
    icon.png
  tests/
    upload.robot
```

#### Why avoid absolute paths

Portable tests should not depend on machine-specific locations:

```robot
# Avoid
UploadFile    Upload Document    C:\Users\John\Desktop\invoice.pdf
```

Absolute paths break in CI, cloud runners, and on other developer machines.

---

### Uploading Inside Tables

If a file input exists inside a table:

```robot
UseTable      Attachments
UploadFile    r1c1    document.pdf
```

Table coordinate syntax works with `UploadFile`.

---

## 2. Download Handling (`ExpectFileDownload`, `VerifyFileDownload`)

File downloads are asynchronous, so the stable pattern in QWeb is a two-step flow:

1. Call `ExpectFileDownload` to enable download polling
2. Trigger the download action
3. Call `VerifyFileDownload` to wait (optionally) and confirm the download completed

This avoids race conditions where the test continues before the file is fully written.

### 2.1 Expecting a Download (`ExpectFileDownload`)

`ExpectFileDownload` turns on polling for a file download event.  
Run it every time before the action that starts the download and before `VerifyFileDownload`.

```robot
ExpectFileDownload
ClickText    Download
VerifyFileDownload    timeout=20s    # file should be downloaded in 20 seconds
```

### 2.2 Verifying a Download (`VerifyFileDownload`)

`VerifyFileDownload` verifies that a file has been downloaded and returns the downloaded file path.

```robot
${path}=    VerifyFileDownload    timeout=20s
Log    Downloaded file: ${path}
```

Notes:

- `timeout` controls how long QWeb waits for the download to appear.  
- The keyword expects a single downloaded file; it fails if no file appears or if more than one new file is detected.



## 3. Default Download Folder

QWeb manages a controlled downloads directory instead of using the browser’s default OS download location.

Why this is important:

- No dependency on system-level download settings
- Cleaner test artifacts
- Predictable file location
- Easier cleanup between test runs

Do not verify files from:

- `C:\Users\...`
- `/home/user/Downloads`

Always rely on QWeb-managed downloads.

---

## 4. Best Practices for File Automation

1. Store upload files in a suite-local or project-level `files/` directory.
2. Store reference images in a suite-local or project-level `images/` directory.
3. Set `%{TEST_WORKSPACE_ROOT}` when debugging individual test files in cloud environments.
4. Let QWeb manage downloads.
5. Avoid hardcoded absolute paths — use filenames and default folder resolution instead.
6. Use `ExpectFileDownload` before triggering the download.
7. Always verify downloads explicitly.
8. Clean up downloaded files if needed between test runs.

---

## Related File Keywords

| Keyword | Purpose |
|----------|----------|
| `UploadFile` | Upload file to input type=file |
| `VerifyFile` | Verify a file exists and return its resolved path |
| `UseFile` / `UsePdf` | Set active text or PDF file for file keywords |
| `ExpectFileDownload` | Wait for a download to start and complete |
| `VerifyFileDownload` | Verify file exists in downloads folder |

