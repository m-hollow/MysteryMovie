# FEAT-15: Slack/Discord Bot

## Summary
Bot that announces game events and allows quick interactions from chat.

## Commands

### Notifications (Automated)
- New round started: "Round 31 has begun! Submit your movie at clubprotean.com"
- Reminder: "3 people haven't submitted all their ratings for Round 31"
- Results: "Round 31 is complete! Winner: PlayerX with 14 points"

### Interactive Commands
- `/mmg status` — Current round status (how many submissions complete)
- `/mmg scores` — Current standings
- `/mmg movie <name>` — Look up a movie's stats
- `/mmg profile <player>` — Quick player stats

## Implementation

### Webhook-Based (Simplest)
- Use incoming webhooks for notifications (no bot server needed)
- Django management command sends webhook on events
- Hook into CommitGameRoundView post-save

### Full Bot (More Complex)
- Slash commands require a bot server
- Could use Django view endpoints as bot backend
- Requires FEAT-16 (REST API) for data retrieval

### Steps (Webhook Approach)
1. Create Slack/Discord incoming webhook
2. Store webhook URL in `.env`
3. Create `movies/services/notifications.py` with webhook sender
4. Hook into key views: CreateRoundView, CommitGameRoundView
5. Add management command for manual notifications

## Effort: Low for webhooks (half day), High for full bot (2-3 days)
