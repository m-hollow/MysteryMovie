# BUG-02: Unsafe File Upload in UserProfileView

## Severity: Critical

## Location
`movies/views.py` ~lines 671–686

## Problem
Profile picture upload has multiple issues:
1. **No file type validation** — any file can be uploaded (executables, scripts, etc.)
2. **No file size limit** — a multi-GB file could exhaust disk/memory
3. **No context manager** — `open(outfile, "wb")` without `with` means the file handle leaks on exception
4. **Unsafe integer cast** — `int(self.request.POST['user_id'])` raises ValueError on bad input
5. **No extension on saved file** — files saved without extension

## Fix Plan

### Step 1: Add file type validation
```python
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
```
- Check `file.content_type` against allowed types
- Check file extension against allowed list
- Check `file.size` against max limit

### Step 2: Use context manager for file writing
```python
with open(outfile, "wb") as f:
    for chunk in uploaded_file.chunks():
        f.write(chunk)
```

### Step 3: Validate user_id
- Wrap `int(POST['user_id'])` in try/except ValueError
- Verify the user_id matches `request.user.id` (prevent uploading to other users' profiles)

### Step 4: Save with proper extension
- Determine extension from content type
- Save as `{user_id}.jpg` (or appropriate extension)

## Risk
Medium — existing uploaded files may not have extensions. Check existing media/user/ directory for current naming convention before changing.
