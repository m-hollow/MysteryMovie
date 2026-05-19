# BUG-10: Multiple Active Rounds Possible

## Severity: Medium

## Location
`movies/models.py` ~lines 20–21

## Problem
`active_round = BooleanField(default=False)` has no constraint preventing multiple rounds from being `True`. Code uses `.last()` to find "the" active round, which is non-deterministic if multiple exist.

## Fix Plan

### Step 1: Add application-level enforcement
Override `GameRound.save()` to deactivate other rounds when activating one:
```python
def save(self, *args, **kwargs):
    if self.active_round:
        GameRound.objects.filter(active_round=True).exclude(pk=self.pk).update(active_round=False)
    super().save(*args, **kwargs)
```

### Step 2: Add a database constraint (Django 3.1+)
```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['active_round'],
            condition=models.Q(active_round=True),
            name='unique_active_round'
        )
    ]
```

### Step 3: Verify existing data
Run a check for multiple active rounds:
```python
assert GameRound.objects.filter(active_round=True).count() <= 1
```

### Step 4: Migration and test

## Risk
Medium — the constraint could fail if data already has duplicates. Check and fix data first.
