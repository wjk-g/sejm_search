import json
import requests

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from search.models import (
    Term,
)

class Command(BaseCommand):
    help = "Get terms from API and save to JSON"

    def handle(self, *args, **options):

        current_term = 10
        for term in range(2, current_term + 1): # there's no data on the first term
            url = f"https://api.sejm.gov.pl/sejm/term{term}"
            response = requests.get(url)
            data = response.json()
            print(data)

            try:
                Term.objects.create(
                    number = data["num"],
                    start_date = data.get("from"),
                    end_date = data.get("to", None),
                    prints_count = data.get("prints").get("count"),
                    prints_count_last_changed = data.get("prints").get("lastChanged")
                )
            except IntegrityError:
                print(f"Term {data['num']} already exists in the database.")

        self.stdout.write('Terms added!')
