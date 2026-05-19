# BUG-01: Unreachable Code in CommitUserRoundView.form_valid()

## Severity: Critical

## Location
`movies/views.py` ~line 1264

## Problem
The `form_valid()` method has an early `return self.render_to_response(context)` that makes the subsequent `return super().form_valid(form)` unreachable. This means:
1. The form is never saved via Django's standard `form_valid()` flow
2. The `context` variable referenced may be undefined, causing a NameError
3. User round scores are never persisted to the database

## Root Cause
Likely a debugging artifact — the render call was added to inspect context but the original return was never restored.

## Fix Plan

### Step 1: Understand the intended flow
- Read the full `CommitUserRoundView` class to understand what data needs to be saved
- Check if PointsEarned and UserRoundDetail updates happen before or after `form_valid()`
- Determine if any context data is needed for the success page

### Step 2: Fix the return logic
- Remove the premature `return self.render_to_response(context)` line
- Ensure `super().form_valid(form)` is reached and executes
- If context data is needed for the response, pass it via the session or success URL

### Step 3: Verify the fix
- Test the full round conclusion flow: Conclude → Commit User → Commit Game
- Confirm UserRoundDetail records are saved with correct point values
- Confirm PointsEarned records are created

## Risk
High — this touches the core scoring workflow. Test thoroughly with a complete round cycle.
