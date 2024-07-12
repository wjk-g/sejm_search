
from django.core.management.base import BaseCommand
from search.models import (
    Term,
    Committee,
    Representative,
    Function,
    Sitting,
)

class Command(BaseCommand):
    help = "Loads data from the API to the database."

    def handle(self, *args, **options):
        # fetch data from the API
        # save data to the database
        pass
