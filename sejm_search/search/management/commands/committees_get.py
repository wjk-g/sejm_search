import json
import requests

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from search.models import (
    Term,
)

class Command(BaseCommand):
    help = "Get committees from API and save to file"

    @staticmethod
    def get_committees_in_term(term):
        committees_url = f"https://api.sejm.gov.pl/sejm/term{term}/committees"
        response = requests.get(committees_url)
        committees = response.json()
        for committee in committees:
            committee["term"] = term
        return committees

    def handle(self, *args, **options):

        terms = Term.objects.all()

        all_committees = []
        for term in terms:
            committees = self.get_committees_in_term(term.number)
            all_committees.append(committees)

        with open("data_collection/data/committees.json", "w") as f:
            json.dump(all_committees, f, indent=4)

        self.stdout.write('Committees saved to file!')
