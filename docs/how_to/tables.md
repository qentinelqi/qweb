# Working with Tables in QWeb

Testing dynamic tables in standard Selenium usually requires brittle XPath loops like:

```xpath
//table/tbody/tr[i]/td[j]
```

QWeb eliminates this complexity by introducing a **Table Context system**, where tables behave like coordinate grids.

Once a table is activated, all table keywords operate inside that context.

---

## 1. Activating a Table (`UseTable`)

Before interacting with any cells, you must define the active table using `UseTable`.

The table can be identified by:

- A unique visible text (recommended)
- An attribute value
- An XPath locator (if necessary)

```robot
UseTable    Firstname
```

Using XPath:

```robot
UseTable    xpath=//table[@id\="users"]
```

After this, all table keywords operate within this table only.

---

## 2. Row Discovery (`GetTableRow`)

Often you don’t know which row a value appears in.

`GetTableRow` searches the active table and returns the row index.

```robot
${row}=    GetTableRow    Jim
```

Example return value:

```
3
```

### Special Row Searches

#### Last row

```robot
${last}=    GetTableRow    //last
```

#### Skip header row

```robot
${row}=    GetTableRow    Jim    skip_header=True
```

Use `skip_header=True` when header rows are included in row counting.

---

## 3. Coordinate Syntax

Once a table is active, QWeb uses coordinate syntax to locate cells.

There are two coordinate modes.

### A. Index-Based Coordinates

Format:

```
rXcY
```

- `r` = row
- `c` = column
- `<thead>` is excluded from index counting

Example:

```robot
${status}=    GetCellText    r3c2
```

#### Negative Index Support

| Pattern | Meaning |
|----------|----------|
| `r-1` | Last row |
| `r-2` | Second last row |
| `c-1` | Last column |

Example:

```robot
${latest}=    GetCellText    r-1c2
```

---

### B. Text-Based Coordinates

Instead of numeric row indexes, you can search by content.

#### Row by text

```
r?Text
```

Example:

```robot
${value}=    GetCellText    r?Robot/c5
```

Meaning:

- Find row containing "Robot"
- Return value from column 5

#### Column by header text

Use `/` to switch to column selector:

```robot
${value}=    GetCellText    r?Robot/Status
```

Meaning:

- Row containing "Robot"
- Column whose header contains "Status"

Text-based column search includes `<thead>`.  
Index-based search does not include `<thead>`.

---

## 4. Reading Data (`GetCellText`)

```robot
${value}=    GetCellText    r3c2
${value}=    GetCellText    r?Robot/Status
```

---

## 5. Clicking Cells (`ClickCell`)

```robot
ClickCell    r3c2
ClickCell    r?Robot/c3
```

If a cell contains multiple clickable elements:

```robot
ClickCell    r3c2    tag=input    index=2
```

---

## 6. Verifying Tables (`VerifyTable`)

```robot
VerifyTable    r2c3    jane.doe@example.com
```

Used to assert expected content across rows and columns.

---

## 7. Dynamic Lookup Example

Find the row with User X and verify their Status.

```robot
*** Test Cases ***
Verify User Status

    UseTable    Username
    ${status}=  GetCellText    r${row}/c?Status
    Should Be Equal    ${status}    Active
```

---

## 8. Iterating All Rows

```robot
UseTable    Username

${count}=    GetTableRow    //last    skip_header=True

FOR    ${i}    IN RANGE    1    ${count}+1
    ${status}=    GetCellText    r${i}/Status
    Should Be Equal    ${status}    Active
END
```

---

## QWeb Table Keywords

| Keyword | Purpose |
|----------|----------|
| `UseTable` | Activate a table context |
| `GetTableRow` | Find row index by text or special locator |
| `GetCellText` | Read cell value |
| `ClickCell` | Click cell or child element |
| `ClickCheckbox` | Toggle checkbox inside table |
| `VerifyTable` | Verify table structure or content |
