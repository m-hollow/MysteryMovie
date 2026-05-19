# FEAT-16: REST API

## Summary
Django REST Framework API for reading game data, enabling external tools and future mobile app.

## Endpoints

### Read-Only (Public to authenticated users)
- `GET /api/rounds/` — List all rounds
- `GET /api/rounds/<id>/` — Round detail with movies and participants
- `GET /api/movies/` — List all movies (filterable by round, rating)
- `GET /api/movies/<id>/` — Movie detail with ratings
- `GET /api/users/<id>/stats/` — User statistics
- `GET /api/leaderboard/` — Current rankings

### Admin-Only
- `POST /api/rounds/` — Create round
- `POST /api/rounds/<id>/conclude/` — Conclude round

## Implementation

### Dependencies
```
djangorestframework>=3.14
```

### Serializers
```python
class GameRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRound
        fields = ['id', 'round_number', 'active_round', 'round_completed',
                  'date_started', 'date_finished', 'winner']

class MovieSerializer(serializers.ModelSerializer):
    average_rating = serializers.DecimalField(source='avg_rating', ...)
    class Meta:
        model = Movie
        fields = ['id', 'name', 'year', 'game_round', 'chosen_by',
                  'average_rating', 'date_watched']
```

### Authentication
- Session auth (for browser access)
- Token auth (for external tools/bots)

### Steps
1. Install Django REST Framework
2. Create `movies/api/` package with serializers, views, urls
3. Add API URLs under `/api/`
4. Implement read-only viewsets first
5. Add token authentication
6. Add API documentation (DRF browsable API is built-in)

## Effort: Medium (1-2 days)
