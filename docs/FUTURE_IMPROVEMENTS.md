# Future Improvements

Technical improvements and refactoring opportunities that aren't bugs but would improve code quality, performance, maintainability, and developer experience. Each item has a detailed plan in [`docs/plans/improvements/`](docs/plans/improvements/).

---

## Architecture & Code Organization

### IMP-01: Split Monolithic views.py Into Modules
- **File**: `movies/views.py` (2000+ lines)
- **Issue**: Single file contains 20+ view classes/functions covering game logic, admin workflows, Results Party, user profiles, and AJAX endpoints.
- **Benefit**: Easier navigation, smaller diffs, clearer ownership of code sections.
- **Plan**: [docs/plans/improvements/imp-01-split-views.md](docs/plans/improvements/imp-01-split-views.md)

### IMP-02: Extract Point Calculation Into Service Layer
- **Issue**: Point calculation logic is embedded in view methods (`calculate_guess_points()`, `calculate_movie_points()`, `get_ranked_results()`). This makes it untestable in isolation and tightly coupled to the HTTP request cycle.
- **Benefit**: Testable scoring logic, reusable across views, cleaner views.
- **Plan**: [docs/plans/improvements/imp-02-extract-point-calculation.md](docs/plans/improvements/imp-02-extract-point-calculation.md)

### IMP-03: Replace Session-Based State Passing with Database Transactions
- **Issue**: Round conclusion stores point data in the session (`request.session['point_queue']`, `request.session['ranked_results']`), which is fragile — session expiry or browser closure loses data mid-workflow.
- **Benefit**: Atomic, reliable round conclusion that can't lose data.
- **Plan**: [docs/plans/improvements/imp-03-replace-session-state.md](docs/plans/improvements/imp-03-replace-session-state.md)

## Testing

### IMP-04: Add Test Suite
- **Issue**: Both `movies/tests.py` and `users/tests.py` are empty. Zero test coverage for the entire application.
- **Benefit**: Confidence in changes, regression prevention, documentation of expected behavior.
- **Plan**: [docs/plans/improvements/imp-04-add-test-suite.md](docs/plans/improvements/imp-04-add-test-suite.md)

## Performance

### IMP-05: Add select_related/prefetch_related to All Views
- **Issue**: Multiple views iterate over querysets and access related objects without optimization, causing N+1 query problems.
- **Benefit**: Dramatically fewer database queries, faster page loads.
- **Plan**: [docs/plans/improvements/imp-05-optimize-queries.md](docs/plans/improvements/imp-05-optimize-queries.md)

### IMP-06: Replace Property-Based Aggregation with Database Annotations
- **Issue**: `Movie.average_rating` property runs a DB query each time it's accessed. When sorting or displaying lists of movies, this creates O(n) queries.
- **Benefit**: Single query for aggregated data instead of one per movie.
- **Plan**: [docs/plans/improvements/imp-06-database-annotations.md](docs/plans/improvements/imp-06-database-annotations.md)

## Logging & Observability

### IMP-07: Implement Proper Django Logging
- **Issue**: All debug output uses `print()`. No log levels, no structured output, no way to control verbosity.
- **Benefit**: Proper log levels (DEBUG/INFO/WARNING/ERROR), configurable output, production-safe logging.
- **Plan**: [docs/plans/improvements/imp-07-implement-logging.md](docs/plans/improvements/imp-07-implement-logging.md)

## Security Hardening

### IMP-08: Add Django Security Middleware Configuration
- **Issue**: Production settings lack security headers, HTTPS enforcement, and cookie security flags.
- **Benefit**: Protection against common web attacks, compliance with security best practices.
- **Plan**: [docs/plans/improvements/imp-08-security-hardening.md](docs/plans/improvements/imp-08-security-hardening.md)

## Developer Experience

### IMP-13: Dockerized Development Environment
- **Issue**: Setting up the dev environment requires manually installing Python 3, MySQL, libmysqlclient, creating a database/user, configuring `.env`, running migrations, and seeding data. Devs have reported this friction as a barrier to contribution — system library mismatches and misconfigured environments cause setup failures.
- **Benefit**: `docker compose up` gives a fully working environment mirroring the PythonAnywhere production stack (Python 3, MySQL 8.0) with no global installs beyond Docker. Scoped to development only — production remains on PythonAnywhere which does not support containers.
- **Plan**: [docs/plans/improvements/imp-13-dockerize-dev-environment.md](docs/plans/improvements/imp-13-dockerize-dev-environment.md)

### IMP-09: Add CI/CD Pipeline
- **Issue**: No automated testing, linting, or deployment. All manual processes.
- **Benefit**: Automated quality checks on PRs, faster feedback, safer deployments.
- **Plan**: [docs/plans/improvements/imp-09-add-ci-cd.md](docs/plans/improvements/imp-09-add-ci-cd.md)

### IMP-10: Upgrade Django Version
- **Issue**: Running Django 3.1.2 (released October 2020). This version reached end-of-life in April 2022 and no longer receives security patches.
- **Benefit**: Security patches, new features, better performance, modern ORM features.
- **Plan**: [docs/plans/improvements/imp-10-upgrade-django.md](docs/plans/improvements/imp-10-upgrade-django.md)

## Data Integrity

### IMP-14: Migrate from MySQL to PostgreSQL
- **Issue**: MySQL requires installing `libmysqlclient` — a system-level C library that is a frequent source of setup failures, especially on macOS. The project uses no raw SQL or MySQL-specific features; all queries go through the Django ORM.
- **Benefit**: `psycopg2-binary` installs with no system dependencies. PostgreSQL is Django's best-supported backend with exclusive features (ArrayField, full-text search, ExclusionConstraint). PythonAnywhere supports PostgreSQL on paid plans. Also simplifies IMP-13 (Docker dev) since the dev Dockerfile no longer needs `libmysqlclient-dev`.
- **Dependencies**: Best done after IMP-10 (Django upgrade) and IMP-04 (test suite) for safer migration.
- **Plan**: [docs/plans/improvements/imp-14-migrate-to-postgresql.md](docs/plans/improvements/imp-14-migrate-to-postgresql.md)

### IMP-11: Add Database Constraints for Business Rules
- **Issue**: Business rules (one active round, one chooser per movie, valid point ranges) are only enforced in application code, not at the database level.
- **Benefit**: Data integrity guaranteed regardless of how data is modified (admin, shell, migrations).
- **Plan**: [docs/plans/improvements/imp-11-database-constraints.md](docs/plans/improvements/imp-11-database-constraints.md)

### IMP-12: Clean Up Dead/Unused Code
- **Issue**: `AllTimeScore` model appears unused, `assign_user_to_movie` in utility_functions is deprecated, large commented-out blocks throughout views.py.
- **Benefit**: Smaller codebase, less confusion, cleaner maintenance.
- **Plan**: [docs/plans/improvements/imp-12-cleanup-dead-code.md](docs/plans/improvements/imp-12-cleanup-dead-code.md)

---

## Priority Matrix

| Priority | Items | Rationale |
|----------|-------|-----------|
| **High** | IMP-13 (Docker dev), IMP-04 (tests), IMP-10 (Django upgrade), IMP-08 (security) | Dev onboarding friction, safety, and security fundamentals |
| **Medium** | IMP-14 (PostgreSQL), IMP-01 (split views), IMP-02 (service layer), IMP-05 (queries), IMP-07 (logging) | Dev friction, maintainability, and performance |
| **Lower** | IMP-03 (session state), IMP-06 (annotations), IMP-09 (CI/CD), IMP-11 (constraints), IMP-12 (cleanup) | Quality of life improvements |
