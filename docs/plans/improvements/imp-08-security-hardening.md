# IMP-08: Add Django Security Middleware Configuration

## Current State
Production settings lack security headers and cookie flags.

## Changes for production.py

```python
# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

## Prerequisites
- Verify PythonAnywhere has HTTPS/SSL configured for clubprotean.com
- Test with `python manage.py check --deploy --settings=mmg.settings.production`

## Steps
1. Verify HTTPS works on clubprotean.com
2. Add security settings to production.py
3. Run `manage.py check --deploy` and fix any remaining warnings
4. Deploy and verify site still works over HTTPS
5. Test that HTTP redirects to HTTPS

## Effort: Low (1-2 hours)
