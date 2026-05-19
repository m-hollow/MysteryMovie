# BUG-03: Unsafe File Upload in EditRoundImagesView

## Severity: Critical

## Location
`movies/views.py` ~lines 1990–2009

## Problem
Movie poster image upload via admin:
1. Regex-extracted ID used without validation
2. No file type validation
3. `open()` without context manager
4. No file size limits
5. Destructive regex unpacking `[id] = get_id.groups(0)` can fail

## Fix Plan

### Step 1: Validate the extracted movie ID
- Verify `id` is a valid integer
- Verify a Movie with that ID exists in the database
- Return 400 if validation fails

### Step 2: Add file validation (same as BUG-02)
- Check content type is an image
- Check file size ≤ 5MB
- Check file extension

### Step 3: Use context manager
```python
with open(outfile, "wb") as f:
    for chunk in uploaded_file.chunks():
        f.write(chunk)
```

### Step 4: Handle regex failure gracefully
- Check that `get_id` is not None before unpacking groups
- Log a warning if the field name doesn't match expected pattern

## Risk
Low — admin-only view, but still important to fix for defense in depth.
