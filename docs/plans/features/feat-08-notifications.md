# FEAT-08: Notification System

## Summary
Email alerts for key game events: new rounds, submission reminders, results published.

## Notification Events
1. **New round created** — "Round X has started! Submit your movie."
2. **Submission reminder** — "You haven't submitted details for 2 movies in Round X."
3. **Round concluded** — "Round X results are in! Check your score."
4. **Results Party starting** — "The Results Party for Round X is starting now!"
5. **Trophy earned** — "You earned the 'Deepest Hurting' trophy!"

## Implementation

### Django Email
Use Django's built-in email framework:
```python
from django.core.mail import send_mail

send_mail(
    'Round 31 Results Are In!',
    'Check your score at www.clubprotean.com/results/',
    'noreply@clubprotean.com',
    [user.email],
)
```

### User Preferences
```python
class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_new_round = models.BooleanField(default=True)
    email_reminders = models.BooleanField(default=True)
    email_results = models.BooleanField(default=True)
```

### Email Backend
- Development: Django console backend (prints to terminal)
- Production: SMTP via Gmail, SendGrid, or PythonAnywhere's email

### Steps
1. Configure email backend in settings
2. Create NotificationPreference model
3. Add notification preferences to user profile page
4. Create email templates in `templates/emails/`
5. Hook notifications into CreateRoundView, CommitGameRoundView
6. (Optional) Add management command for reminder emails via cron

## Effort: Medium (1 day)
