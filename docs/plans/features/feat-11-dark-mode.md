# FEAT-11: Dark Mode

## Summary
User-selectable dark/light theme with system preference detection.

## Implementation

### CSS Approach
Use CSS custom properties (variables) for theming:
```css
:root {
    --bg-primary: #ffffff;
    --text-primary: #212529;
    --bg-card: #f8f9fa;
    ...
}

[data-theme="dark"] {
    --bg-primary: #1a1a2e;
    --text-primary: #e0e0e0;
    --bg-card: #16213e;
    ...
}
```

### Theme Toggle
- Toggle button in navbar
- Store preference in localStorage (instant) + UserProfile field (persistent)
- Respect `prefers-color-scheme` media query as default

### Model Change
```python
# Add to UserProfile
theme_preference = models.CharField(
    max_length=10,
    choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
    default='auto'
)
```

### Steps
1. Define CSS variables for all colors in `base.css`
2. Create dark theme variable overrides
3. Add theme toggle JavaScript
4. Add theme preference to UserProfile
5. Set theme on page load from stored preference
6. Update Bootstrap classes that use hardcoded colors

## Effort: Low-Medium (half day)
