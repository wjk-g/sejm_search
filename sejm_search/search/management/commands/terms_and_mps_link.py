import json

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from search.models import (
    MP,
    TermMP,
    Term,
)

class Command(BaseCommand):
    help = "Link terms and MPs."

    def handle(self, *args, **options):

        with open("data_collection/data/mps_flat.json") as f:
            mps_flat = json.load(f)

        for mp in mps_flat:
            
            try:
                mp_in_db = MP.objects.filter(
                    first_name = mp["firstName"],
                    second_name = mp.get("secondName", None),
                    family_name = mp["lastName"],
                    birth_date = mp["birthDate"],
                ).first()

                term_in_db = Term.objects.filter(
                    number = mp.get("term"),
                ).first()

                TermMP.objects.get_or_create(
                        term = term_in_db,
                        mp_term_id = mp.get("id"),
                        mp = mp_in_db,
                    )
            except IntegrityError as e:
                print(e)

        self.stdout.write(
            self.style.SUCCESS('MPs and terms linked!')
        )
