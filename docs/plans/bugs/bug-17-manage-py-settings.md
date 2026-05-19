# BUG-17: manage.py Settings Module Not Configurable

## Severity: Medium

## Location
`manage.py` ~line 9

## Problem
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mmg.settings')
```
Points to `mmg.settings` (the package), not a specific settings file. If `mmg/settings/__init__.py` is empty, Django can't determine which settings to use.

## Fix Plan

### Step 1: Default to development settings
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mmg.settings.development')
```

### Step 2: Allow override via environment
The `setdefault` already supports this — if `DJANGO_SETTINGS_MODULE` is set in `.env` or shell, it takes precedence.

### Step 3: Update documentation
Note in README that production uses:
```bash
DJANGO_SETTINGS_MODULE=mmg.settings.production python3 manage.py ...
```

## Risk
Very low — `setdefault` means existing env vars are respected.
