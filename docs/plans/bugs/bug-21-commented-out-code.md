# BUG-21: Commented-Out Code Throughout Codebase

## Severity: Low

## Location
Multiple locations in `movies/views.py` and `movies/models.py`

## Problem
Large blocks of commented-out code that:
- Reduce readability
- Create confusion about what's active vs. deprecated
- Make diffs noisier
- Are already preserved in git history

## Fix Plan

### Step 1: Identify all commented blocks
Search for multi-line comment blocks (3+ consecutive commented lines) in:
- `movies/views.py`
- `movies/models.py`
- `movies/forms.py`

### Step 2: Review each block
For each block, determine:
- Is this dead code? → Remove it
- Is this a TODO/future feature? → Convert to a proper TODO comment or add to FEATURE_IDEAS.md
- Is this documentation? → Convert to a docstring

### Step 3: Remove dead code in one commit
Make a single cleanup commit removing all clearly dead commented code.

## Risk
Very low — code is in git history if ever needed. Review carefully to avoid removing actual documentation comments.
