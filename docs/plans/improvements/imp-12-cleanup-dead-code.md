# IMP-12: Clean Up Dead/Unused Code

## Current State
- `AllTimeScore` model appears unused in any view or template
- `assign_user_to_movie()` in utility_functions.py may be deprecated
- `calculate_trophy_points()` on UserProfile is never called
- Large commented-out code blocks in views.py and models.py
- Debug print statements throughout

## Steps

### Step 1: Audit unused code
- Search for references to `AllTimeScore` outside of model definition and admin registration
- Search for calls to `assign_user_to_movie` and `calculate_trophy_points`
- Identify all multi-line commented blocks

### Step 2: Verify before removing
- Confirm `AllTimeScore` has no data in production (or is truly unused)
- Confirm utility functions aren't called from Django shell or management commands
- Check git blame on commented code to understand why it was commented out

### Step 3: Remove in stages
1. Remove clearly dead commented code (one commit)
2. Remove unused utility functions (one commit)
3. Remove unused models with migration (separate commit, more risky)

### Step 4: Remove unused model
If `AllTimeScore` is confirmed unused:
```bash
python manage.py makemigrations movies  # Will generate DeleteModel migration
python manage.py migrate
```

## Risk
Low for commented code removal. Medium for model removal (requires migration on production DB).

## Effort: Low (2-3 hours)
