# BUG-12: Improper View Method Declaration — Missing `self`

## Severity: Medium

## Location
`movies/views.py` ~lines 480, 521

## Problem
```python
class ResultsPartyStateIncrement(LoginRequiredMixin):
    def request(request, value):  # Missing 'self'
```
These methods are called directly as view functions via URL conf, so `request` accidentally receives the HTTP request object (which would normally go to `self`). It works by coincidence but is structurally wrong.

## Fix Plan

### Step 1: Convert to standalone functions
```python
@login_required
def results_party_state(request):
    ...

@login_required
def results_party_increment(request, value):
    ...
```

### Step 2: Update URL patterns
```python
path('resultspartystate.json', results_party_state, name='party_state'),
path('resultspartyincrement/<value>', results_party_increment, name='party_increment'),
```

### Step 3: Test Results Party
- Verify state polling returns correct JSON
- Verify increment updates state correctly

## Risk
Low — converting to functions is the simplest correct fix. Combines well with BUG-11 fix.
