# BUG-15: Production Settings Missing Security Headers

## Severity: Medium

## Location
`mmg/settings/production.py`

## Problem
Production settings lack several Django security best practices:
- `SECURE_SSL_REDIRECT` not set (no forced HTTPS)
- `SESSION_COOKIE_SECURE` not set (cookies sent over HTTP)
- `CSRF_COOKIE_SECURE` not set
- `SECURE_HSTS_SECONDS` not set (no HSTS header)

## Fix Plan

### Step 1: Add security settings to production.py
```python
# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# HSTS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### Step 2: Verify PythonAnywhere supports HTTPS
- Check if the domain has an SSL certificate
- PythonAnywhere provides free HTTPS for custom domains
- If no HTTPS yet, set up certificate before enabling SECURE_SSL_REDIRECT

### Step 3: Test in production
- Verify site loads over HTTPS
- Verify cookies are not sent over HTTP
- Run `python manage.py check --deploy` to catch remaining issues

## Risk
Medium — enabling `SECURE_SSL_REDIRECT` without HTTPS configured will make the site inaccessible. Verify HTTPS works first.
