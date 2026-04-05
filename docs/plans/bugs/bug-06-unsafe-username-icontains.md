# BUG-06: Unsafe Username Lookup with __icontains

## Severity: High

## Location
`movies/views.py` ~lines 805, 877, 1327, 1343, 1372

## Problem
Multiple places use `User.objects.get(username__icontains=winner_name)` which:
1. Can match multiple users (e.g., "john" matches "john", "johndoe", "john_smith")
2. Raises `MultipleObjectsReturned` if multiple matches exist
3. Case-insensitive matching may pick the wrong user

## Fix Plan

### Step 1: Replace all __icontains with exact match
Find all instances and change to:
```python
User.objects.get(username=winner_name)
```

### Step 2: Wrap in proper error handling
```python
try:
    winner = User.objects.get(username=winner_name)
except User.DoesNotExist:
    # Handle missing user gracefully
    messages.error(request, f"User '{winner_name}' not found")
    return redirect(...)
```

### Step 3: Audit where winner_name comes from
- If it comes from form data, ensure the form uses a ModelChoiceField (select dropdown) instead of free text
- This eliminates the lookup problem entirely

## Risk
Low — straightforward text replacement. Test with round conclusion workflow.
