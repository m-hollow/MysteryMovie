# IMP-09: Add CI/CD Pipeline

## Current State
No automated testing, linting, or deployment. All processes are manual.

## Proposed: GitHub Actions

### `.github/workflows/ci.yml`
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test
          MYSQL_DATABASE: mmg_test
        ports: ['3306:3306']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - run: pip install -r requirements.txt
      - run: python manage.py test --settings=mmg.settings.development
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install flake8
      - run: flake8 movies/ users/ mmg/
```

## Steps
1. Create `.github/workflows/` directory
2. Write CI workflow for tests + linting
3. Add a test settings file (`mmg/settings/test.py`) using SQLite for faster CI
4. Ensure tests pass locally first (see IMP-04)
5. Enable branch protection requiring CI to pass

## Effort: Low (2-3 hours, but depends on IMP-04 for tests)
