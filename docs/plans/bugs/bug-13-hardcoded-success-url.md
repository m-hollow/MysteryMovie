# BUG-13: Hardcoded success_url in EditRoundImagesView

## Severity: Medium

## Location
`movies/views.py` ~line 1948

## Problem
```python
success_url = '/edit_round_images/30/'
```
Hardcodes round 30. After uploading images for any other round, the user is redirected to round 30's page.

## Fix Plan

### Step 1: Use get_success_url() method
```python
def get_success_url(self):
    return reverse('movies:edit_round_images', kwargs={'pk': self.object.pk})
```

### Step 2: Remove the hardcoded success_url class attribute

### Step 3: Also fix the form_valid override
The line `self.success_url = '/edit_round_images/' + form.data['round_number'] + '/'` is a partial fix but uses string concatenation. Replace with `reverse()`.

## Risk
Very low — straightforward URL fix.
