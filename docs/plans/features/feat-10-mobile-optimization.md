# FEAT-10: Mobile-Optimized Interface

## Summary
Responsive redesign for mobile devices with simplified forms and touch-friendly interactions.

## Current Issues
- Bootstrap 4 provides basic responsiveness but tables don't collapse well on mobile
- Forms have small touch targets
- Navigation doesn't collapse to hamburger menu cleanly
- Movie lists are text-heavy with no visual distinction

## Proposed Changes

### Navigation
- Proper Bootstrap navbar collapse with hamburger menu
- Bottom tab bar for key actions (Home, Results, Members, Profile)

### Forms
- Larger touch targets (min 44px)
- RadioSelect buttons as large tappable cards instead of tiny circles
- Star rating as tappable stars instead of dropdown
- Full-width inputs on mobile

### Tables
- Convert tables to card layout on small screens
- Or use responsive table with horizontal scroll
- Priority: Results table, Members ranking, Overview

### Movie Listings
- Card grid on mobile (poster + title + rating)
- Swipeable cards for movie browsing

### Steps
1. Audit current mobile rendering (browser dev tools)
2. Fix navbar collapse behavior
3. Add responsive CSS for tables → cards
4. Resize form inputs and touch targets
5. Add viewport-specific layouts where needed
6. Test on actual mobile devices

## Effort: Medium (1-2 days)
