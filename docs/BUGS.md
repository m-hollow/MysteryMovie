# Known Bugs

Bugs discovered through code analysis, organized by severity. Each bug has a detailed plan file in [`plans/bugs/`](plans/bugs/).

---

## Critical

### BUG-01: Unreachable Code in CommitUserRoundView.form_valid()
- **File**: `movies/views.py` ~line 1264
- **Issue**: Early `return self.render_to_response(context)` makes the `return super().form_valid(form)` line unreachable. The form is never saved to the database, and `context` may be undefined.
- **Impact**: Round score finalization is broken — user scores may never persist.
- **Plan**: [docs/plans/bugs/bug-01-commit-user-round-unreachable-code.md](plans/bugs/bug-01-commit-user-round-unreachable-code.md)

### BUG-02: Unsafe File Upload — No Validation in UserProfileView
- **File**: `movies/views.py` ~lines 671–686
- **Issue**: Profile picture upload accepts any file type/size, uses `open()` without context manager, and `int(POST['user_id'])` can raise ValueError.
- **Impact**: Arbitrary file upload, potential server crash, resource leak on exception.
- **Plan**: [docs/plans/bugs/bug-02-unsafe-profile-pic-upload.md](plans/bugs/bug-02-unsafe-profile-pic-upload.md)

### BUG-03: Unsafe File Upload in EditRoundImagesView
- **File**: `movies/views.py` ~lines 1990–2009
- **Issue**: Movie image upload uses regex-extracted ID without validation, no file type checks, no context manager for file handle.
- **Impact**: Same class of vulnerability as BUG-02 — arbitrary file writes.
- **Plan**: [docs/plans/bugs/bug-03-unsafe-movie-image-upload.md](plans/bugs/bug-03-unsafe-movie-image-upload.md)

### BUG-04: Bare except Clauses Hide Real Errors
- **File**: `movies/views.py` ~lines 495, 530
- **Issue**: `except:` catches all exceptions including SystemExit and KeyboardInterrupt. Errors are swallowed with only `print("INSERT uid")`.
- **Impact**: Database errors, crashes, and critical failures are silently ignored.
- **Plan**: [docs/plans/bugs/bug-04-bare-except-clauses.md](plans/bugs/bug-04-bare-except-clauses.md)

---

## High

### BUG-05: ForeignKey Default Value Mismatch on Movie.game_round
- **File**: `movies/models.py` ~line 169
- **Issue**: `game_round = models.ForeignKey(GameRound, default="", ...)` — empty string is invalid for a ForeignKey field.
- **Impact**: Creating a Movie without explicit `game_round` causes a database error.
- **Plan**: [docs/plans/bugs/bug-05-foreignkey-default-mismatch.md](plans/bugs/bug-05-foreignkey-default-mismatch.md)

### BUG-06: Unsafe Username Lookup with __icontains
- **File**: `movies/views.py` ~lines 805, 877, 1327, 1343, 1372
- **Issue**: `User.objects.get(username__icontains=winner_name)` can match multiple users (e.g., "john" matches "johndoe"), raising `MultipleObjectsReturned`.
- **Impact**: Crashes during round conclusion if usernames partially overlap.
- **Plan**: [docs/plans/bugs/bug-06-unsafe-username-icontains.md](plans/bugs/bug-06-unsafe-username-icontains.md)

### BUG-07: Undefined Variable `idx` in PartyState Creation
- **File**: `movies/views.py` ~line 818
- **Issue**: `PartyState(idx=idx, ...)` references variable `idx` that is never defined in scope.
- **Impact**: NameError crash when creating initial PartyState.
- **Plan**: [docs/plans/bugs/bug-07-undefined-idx-partystate.md](plans/bugs/bug-07-undefined-idx-partystate.md)

### BUG-08: KeyError in Results Party When chosen_by_id is None
- **File**: `movies/views.py` ~line 414
- **Issue**: `users_index[round_film.chosen_by_id]` crashes if `chosen_by_id` is None (movie has no assigned chooser).
- **Impact**: Results Party page crashes if any movie lacks a `chosen_by` assignment.
- **Plan**: [docs/plans/bugs/bug-08-keyerror-chosen-by-none.md](plans/bugs/bug-08-keyerror-chosen-by-none.md)

### BUG-09: Date Fields Use Potentially Stale Defaults
- **File**: `movies/models.py` ~lines 26, 29, 176
- **Issue**: `default=date.today` on DateFields — code comments acknowledge this may produce wrong dates. The `date.today` callable is correct syntax but the design intent seems wrong (finished date shouldn't default to today).
- **Impact**: New rounds/movies get misleading default dates.
- **Plan**: [docs/plans/bugs/bug-09-stale-date-defaults.md](plans/bugs/bug-09-stale-date-defaults.md)

---

## Medium

### BUG-10: Multiple Active Rounds Possible (No Unique Constraint)
- **File**: `movies/models.py` ~lines 20–21
- **Issue**: `active_round` BooleanField has no constraint ensuring only one round is active. Code comment asks "should you add unique=True?" but it was never done.
- **Impact**: Multiple active rounds causes UI to show wrong data (uses `.last()`).
- **Plan**: [docs/plans/bugs/bug-10-multiple-active-rounds.md](plans/bugs/bug-10-multiple-active-rounds.md)

### BUG-11: Missing CSRF Protection on AJAX Endpoints
- **File**: `movies/urls.py` ~lines 42–43
- **Issue**: `ResultsPartyStateView.request` and `ResultsPartyStateIncrement.request` are class methods bound directly in URL patterns, bypassing Django's CBV dispatch and CSRF middleware.
- **Impact**: CSRF vulnerability on party state endpoints; POST requests may fail or be exploitable.
- **Plan**: [docs/plans/bugs/bug-11-missing-csrf-ajax.md](plans/bugs/bug-11-missing-csrf-ajax.md)

### BUG-12: Improper View Method Declaration — Missing `self`
- **File**: `movies/views.py` ~lines 480, 521
- **Issue**: Class methods defined as `def request(request, value):` without `self` parameter, called directly in URL conf instead of via `as_view()`.
- **Impact**: Fragile binding that works by accident — `request` acts as `self`. Will break if anyone tries to use these as proper CBVs.
- **Plan**: [docs/plans/bugs/bug-12-missing-self-parameter.md](plans/bugs/bug-12-missing-self-parameter.md)

### BUG-13: Hardcoded success_url in EditRoundImagesView
- **File**: `movies/views.py` ~line 1948
- **Issue**: `success_url = '/edit_round_images/30/'` hardcodes round ID 30.
- **Impact**: After uploading images for any other round, user is redirected to round 30's edit page.
- **Plan**: [docs/plans/bugs/bug-13-hardcoded-success-url.md](plans/bugs/bug-13-hardcoded-success-url.md)

### BUG-14: N+1 Query in Results Party View
- **File**: `movies/views.py` ~lines 386–422
- **Issue**: Loop fetches `round_user.user.username` for each UserRoundDetail without `select_related('user')`.
- **Impact**: Extra database query per participant — performance degrades with more users.
- **Plan**: [docs/plans/bugs/bug-14-n-plus-1-results-party.md](plans/bugs/bug-14-n-plus-1-results-party.md)

### BUG-15: Production Settings Missing Security Headers
- **File**: `mmg/settings/production.py`
- **Issue**: Missing `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`.
- **Impact**: Cookies sent over plain HTTP, no HSTS, no forced HTTPS redirect.
- **Plan**: [docs/plans/bugs/bug-15-missing-security-headers.md](plans/bugs/bug-15-missing-security-headers.md)

### BUG-16: Index Out of Bounds in Results Party
- **File**: `movies/views.py` ~line 454
- **Issue**: `round_films[PartyState.objects.last().idx-1].id` — no bounds check if `idx` exceeds film count or films list is empty.
- **Impact**: IndexError crash during Results Party.
- **Plan**: [docs/plans/bugs/bug-16-index-out-of-bounds-party.md](plans/bugs/bug-16-index-out-of-bounds-party.md)

### BUG-17: manage.py Settings Module Not Configurable
- **File**: `manage.py` ~line 9
- **Issue**: Hardcoded `DJANGO_SETTINGS_MODULE = 'mmg.settings'` — doesn't point to development or production, relies on `__init__.py` which may be empty.
- **Impact**: Ambiguous settings resolution; may use wrong settings in some contexts.
- **Plan**: [docs/plans/bugs/bug-17-manage-py-settings.md](plans/bugs/bug-17-manage-py-settings.md)

---

## Low

### BUG-18: print() Statements Left in Production Code
- **File**: `movies/views.py` ~lines 39, 150, 155, 412, and others
- **Issue**: Debug `print()` calls throughout views — no proper logging.
- **Impact**: Clutters server logs; no log levels, no structured output.
- **Plan**: [docs/plans/bugs/bug-18-print-statements.md](plans/bugs/bug-18-print-statements.md)

### BUG-19: Python Sorting Instead of Database Ordering
- **File**: `movies/views.py` ~line 133
- **Issue**: `sorted(Movie.objects.all(), key=lambda x: x.average_rating, ...)` loads all movies into memory, then calls the `average_rating` property (a DB query) on each.
- **Impact**: O(n) database queries for sorting; poor performance at scale.
- **Plan**: [docs/plans/bugs/bug-19-python-sorting.md](plans/bugs/bug-19-python-sorting.md)

### BUG-20: Potential MultipleObjectsReturned on UserMovieDetail
- **File**: `movies/views.py` ~line 275
- **Issue**: `.get(movie=movie, is_user_movie=True)` assumes only one user marked as chooser, but model doesn't enforce this with a constraint.
- **Impact**: Crash if multiple users are flagged as choosing the same movie.
- **Plan**: [docs/plans/bugs/bug-20-multiple-movie-choosers.md](plans/bugs/bug-20-multiple-movie-choosers.md)

### BUG-21: Commented-Out Code Throughout Codebase
- **File**: Multiple locations in `views.py` and `models.py`
- **Issue**: Large blocks of dead commented code make maintenance harder.
- **Impact**: Readability and maintenance burden.
- **Plan**: [docs/plans/bugs/bug-21-commented-out-code.md](plans/bugs/bug-21-commented-out-code.md)

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 4 |
| High | 5 |
| Medium | 8 |
| Low | 4 |
| **Total** | **21** |
