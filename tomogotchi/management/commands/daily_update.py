from django.core.management.base import BaseCommand
from tomogotchi.models import Player
from django.db.models import F
from django.db.models import Count, Q
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Cast
from django.db.models import FloatField, PositiveIntegerField

class Command(BaseCommand):
    help = "Decrease Hunger & Mood by the daily cost amount"

    def handle(self, *args, **options):
        players = Player.objects.all()
        # Mood update:
        mood_updates = {}
        players = Player.objects.annotate(
            comfort=Count('house__furnitureOwned', filter=Q(house__furnitureOwned__placed=True)) + 1
        )
        for player in players:
            new_mood = max(0, player.mood - 40 / player.comfort)  # Ensure mood doesn't go below 0
            mood_updates[player.id] = new_mood

        # Update players' mood in the database
        for player_id, new_mood in mood_updates.items():
            Player.objects.filter(id=player_id).update(mood=new_mood)

        # set to a minimum of zero:
        Player.objects.filter(mood__lt=0).update(mood=0)
        
        players = Player.objects.filter(Q(mood__gt=0))  # only update live players next
        
        # Decrease hunger for all players, ensuring it doesn't go below 0
        Player.objects.all().update(
            hunger=F('hunger') - (100 - F("mood"))/4
        )
        Player.objects.filter(hunger__lt=0).update(hunger=0)

        dead_players = Player.objects.filter(Q(mood__lte=0) | Q(hunger__lte=0))
        # Update dead players or smthing

        # Update all currency:
        Player.objects.all().update(daily_money_earned=0)

