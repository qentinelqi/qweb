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

### Using Default Folders (Recommended)

If you provide only a filename:

```robot
UploadFile    Upload Document    invoice.pdf
```

QWeb automatically searches default folders such as:

- `users/downloads`
- `project_dir/files`
- `${EXECDIR}/**/files`

This allows you to avoid hardcoded absolute paths.

### Why Default Folders Matter

1. Tests remain portable across machines  
2. CI/CD pipelines work without path changes  
3. No dependency on user profile directories  
4. Cleaner repository structure  
5. Easier team collaboration  

Avoid this:

```robot
UploadFile    Upload Document    C:\Users\John\Desktop\invoice.pdf
```

Absolute paths break in CI and on other developer machines.

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

1. Store upload files in a project `files/` directory.
2. Let QWeb manage downloads.
3. Never hardcode absolute paths.
4. Use `ExpectFileDownload` before triggering the download.
5. Always verify downloads explicitly.
6. Clean up downloaded files if needed between test runs.

---

## Related File Keywords

| Keyword | Purpose |
|----------|----------|
| `UploadFile` | Upload file to input type=file |
| `ExpectFileDownload` | Wait for a download to start and complete |
| `VerifyFileDownload` | Verify file exists in downloads folder |

