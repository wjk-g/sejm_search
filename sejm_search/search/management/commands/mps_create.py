
import json
import math

from django.core.management.base import BaseCommand

from search.models import (
    MP,
)

class Command(BaseCommand):
    help = "Add MPs to database"

    def handle(self, *args, **options):
        
        def replace_nan(obj):
            for key, value in obj.items():
                if isinstance(value, float) and math.isnan(value):
                    obj[key] = None
            return obj
        
        with open("data_collection/data/unique_mps.json", "r") as f:
            unique_mps = json.load(f, object_hook=replace_nan)

        for mp in unique_mps:
            MP.objects.get_or_create(
                first_name = mp["firstName"],
                second_name = mp["secondName"],
                family_name = mp["lastName"],
                birth_date = mp["birthDate"],
            )
        
        self.stdout.write(
            self.style.SUCCESS("MPs added to the database!")
        )
