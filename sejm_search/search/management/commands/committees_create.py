import json

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from search.models import (
    Committee,
    Term,
)

class Command(BaseCommand):
    help = "Create committees"

    def handle(self, *args, **options):

        with open("data_collection/data/committees.json") as f:
            terms = json.load(f)

        for term in terms:
            for committee in term:
                term_object = Term.objects.get(number=committee.get("term"))
                print(term_object)
                members = committee.get("members")
                member_ids = [member["id"] for member in members]
                try:
                    Committee.objects.get_or_create(
                        code = committee.get("code"),
                        name = committee.get("name"),
                        nameGenitive = committee.get("nameGenitive"),
                        scope = committee.get("scope"),
                        compositionDate = committee.get("compositionDate"),
                        appointmentDate = committee.get("appointmentDate"),
                        phone = committee.get("phone"),
                        _type = committee.get("type"),
                        term = term_object,
                        member_ids = member_ids
                    )
                except IntegrityError as e:
                    print(e)

        self.stdout.write('Committees added!')
