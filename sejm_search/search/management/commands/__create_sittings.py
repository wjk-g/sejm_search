
import json

from django.core.management.base import BaseCommand
from search.models import (
    Sitting,
    Term,
    Committee,
)

class Command(BaseCommand):
    help = "Add sittings info to the database"

    def handle(self, *args, **options):

        with open("data_collection/data/sittings_info.json") as f:
            sittings_data = json.load(f)

        for term in sittings_data: # term is a dictionary of dictionaries
            term_obj = Term.objects.get(number=int(term))
            for committee in sittings_data[term]:
                committee_obj = Committee.objects.get(term=term, code=committee)
                for sitting in sittings_data[term][committee]:
                    # Careful: there's a jointWith field in each sitting
                    # Create a sitting unless it already exists

                    sitting_input_unique = {
                        "committee": committee_obj,
                        "term": term_obj,
                        "number": sitting.get("num")
                    }

                    sitting_input_other_fields = {
                        "date": sitting.get("date"),
                        "agenda": sitting.get("agenda"),
                        "closed": sitting.get("closed"),
                        "remote": sitting.get("remote"),
                        "jointWith": sitting.get("jointWith"),
                    }

                    sitting_obj, created = Sitting.objects.get_or_create(**sitting_input_unique, defaults=sitting_input_other_fields)
                    # This method is atomic assuming that the database enforces uniqueness of the keyword arguments (see unique or unique_together). If the fields used in the keyword arguments do not have a uniqueness constraint, concurrent calls to this method may result in multiple rows with the same parameters being inserted.

                    if not created:
                        print(f"Sitting {sitting_input_unique.get("committee")}, num: {sitting_input_unique.get("number")} in term {sitting_input_unique.get("term")} already exists!")

        self.stdout.write('Sittings added!')
