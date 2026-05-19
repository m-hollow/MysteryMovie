# BUG-11: Missing CSRF Protection on AJAX Endpoints

## Severity: Medium

## Location
`movies/urls.py` ~lines 42–43

## Problem
The Results Party AJAX endpoints are bound as class method references (`ResultsPartyStateView.request`) instead of proper CBV `as_view()` calls. This bypasses Django's standard middleware chain including CSRF protection.

## Fix Plan

### Step 1: Convert to proper CBV or FBV
Either make them proper class-based views:
```python
path('resultspartystate.json', ResultsPartyStateView.as_view(), name='party_state'),
path('resultspartyincrement/<value>', ResultsPartyStateIncrement.as_view(), name='party_increment'),
```
Or extract as standalone functions with `@login_required` and `@csrf_exempt` (if CSRF exemption is intentional for AJAX).

### Step 2: Add CSRF token to AJAX requests
In `resultsparty.html` JavaScript, include CSRF token in POST headers:
```javascript
headers: {'X-CSRFToken': getCookie('csrftoken')}
```

### Step 3: Test
- Verify AJAX polling still works
- Verify increment POST succeeds with CSRF token

## Risk
Medium — changing URL binding affects how requests are dispatched. Test the Results Party flow end-to-end.
