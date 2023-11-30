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
        players.update( mood=Subquery(
            Player.objects.filter(id=OuterRef("id")).annotate(
                newmood=Cast( 
                    Cast(F("mood"), FloatField()) - 40/Cast(  # amount of mood lost depends on 40/comfort, comfort = # of placed furniture + 1
                        Count(
                            F("house__furnitureOwned"), 
                            filter=Q(house__furnitureOwned__placed=True)
                        ) + 1,  # prevent division by zero
                        FloatField() ),  
                    PositiveIntegerField()) # must always be positive
            ).values("newmood")[:1]
        ))
        
        players = Player.objects.filter(Q(mood__gt=0))  # only update live players next

        players.update( hunger=Subquery(
            Player.objects.filter(id=OuterRef("id")).annotate(
                newhunger=F("hunger") - Cast(Cast((100 - F("mood")), FloatField())/4, PositiveIntegerField()) # amount of hunger lost depends on 100-mood
             # don't need +1 since live => mood > 0
            ).values("newhunger")[:1]
        ))

        
        dead_players = Player.objects.filter(Q(mood__lte=0) | Q(hunger__lte=0))
        # Update dead players or smthing

        # Update all currency:
        Player.objects.all().update(daily_money_earned=0)

