# FEAT-09: Comments & Discussion

## Summary
Post-round discussion threads on movies and rounds, with reactions.

## Design

### Model
```python
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, null=True, on_delete=models.CASCADE)
    game_round = models.ForeignKey(GameRound, null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)  # Threaded
    text = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)  # thumbsup, laugh, etc.
```

### Visibility Rules
- Movie comments visible only after the round is concluded (prevents spoiling guesses)
- Round-level comments visible immediately
- Comments on active round movies: hidden until round concludes

### Display
- Add comment section below movie detail (`old_movie.html`)
- Add comment section on round results (`old_round_results.html`)
- Simple form: textarea + submit button
- Show threaded replies with indent

### Steps
1. Create models and migration
2. Create comment form and partial template
3. Add comment display to movie and results templates
4. Add AJAX submit for comments (avoid full page reload)
5. Add reaction buttons with AJAX
6. Implement visibility rules based on round status

## Effort: Medium (1 day)
