# IMP-10: Upgrade Django Version

## Current State
Django 3.1.2 (released October 2020, EOL April 2022). No security patches available.

## Upgrade Path
Django 3.1 → 3.2 (LTS) → 4.0 → 4.1 → 4.2 (LTS) → 5.0 → 5.1 → 5.2 (LTS, current)

Recommended target: **Django 5.2 LTS** (supported until April 2028).

## Steps

### Phase 1: Django 3.2 LTS
1. Update `requirements.txt`: `Django==3.2.*`
2. Run `python -Wa manage.py test` to see deprecation warnings
3. Fix any deprecation warnings
4. Test all views manually

### Phase 2: Django 4.2 LTS
1. Update to `Django==4.2.*`
2. Key changes:
   - `url()` removed → must use `path()` / `re_path()` (already done)
   - `DEFAULT_AUTO_FIELD` setting required
   - Template `{% load %}` changes
3. Fix deprecation warnings and test

### Phase 3: Django 5.2 LTS
1. Update to `Django==5.2.*`
2. Key changes:
   - Python 3.10+ required
   - Some template tag changes
3. Fix and test

### Per-phase checklist
- [ ] Update Django version in requirements.txt
- [ ] Run migrations
- [ ] Fix deprecation warnings
- [ ] Test all pages manually
- [ ] Run `manage.py check --deploy`
- [ ] Update any incompatible third-party packages

## Dependencies
- `django-bootstrap4` may need updating (check compatibility)
- `django-crispy-forms` may need updating
- `django-environ` should be compatible
- `mysqlclient` should be compatible

## Risk
Medium — each major version can introduce breaking changes. Test thoroughly at each step.

## Effort: Medium-High (1-2 days)
