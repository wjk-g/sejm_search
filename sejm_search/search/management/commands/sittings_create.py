
import json
import requests

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from search.models import (
    Committee,
    Sitting,
)

from data_collection.get_info import get_json_data

class Command(BaseCommand):
    help = "Get sittings"

    def handle(self, *args, **options):

        committees = Committee.objects.all()

        for committee in committees:

            has_sittings_in_db = Sitting.objects.filter(committee=committee).exists()

            if not has_sittings_in_db:
                url = f"https://api.sejm.gov.pl/sejm/term{committee.term.number}/committees/{committee.code}/sittings"
            
                response = requests.get(url)
                sittings = response.json()
                term = committee.term

                for sitting in sittings:
                    Sitting.objects.get_or_create(
                        committee = committee,
                        term = term,
                        number = sitting.get("num"),
                        defaults={
                            "date": sitting.get("date"),
                            "agenda": sitting.get("agenda"),
                            "closed": sitting.get("closed"),
                            "remote": sitting.get("remote"),
                            "jointWith": sitting.get("jointWith"),
                        }
                    )
                print(f"Sittings of committee {committee.code} in term {committee.term.number} added to the db")
                
            if has_sittings_in_db:
                print(f"Sittings of committee {committee.code} in term {committee.term.number} already in the db")

        self.stdout.write('Operation finished!')
