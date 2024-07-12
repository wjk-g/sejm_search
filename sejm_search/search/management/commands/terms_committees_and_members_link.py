
import json

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from search.models import (
    MP, 
    Committee,
    TermMP,
    CommitteeTermMP,
    Term,
)

class Command(BaseCommand):
    help = "Create committees"

    def handle(self, *args, **options):

        # Fetch all committees and terms
        committees = Committee.objects.all()
        
        for committee in committees:
            term = Term.objects.get(number=committee.term.number) # committee's term
    
            if committee.member_ids:
                member_ids = committee.member_ids
                
                for member_id in member_ids:
                    print(member_id)
                    try:
                        term_mp = TermMP.objects.get(term=term, mp_term_id=member_id)
                    except TermMP.DoesNotExist:
                        print(f"TermMP with term {term.number} and mp_term_id {member_id} does not exist.")
                        continue

                    # Check if the CommitteeTermMP object already exists
                    if not CommitteeTermMP.objects.filter(committee=committee, term=term, mp=term_mp.mp).exists():
                        # Create the CommitteeTermMP object
                        CommitteeTermMP.objects.create(committee=committee, term=term, mp=term_mp.mp)
                        print(f"Created CommitteeTermMP for committee {committee.name}, term {committee.term}, mp {term_mp.mp.name}")

        self.stdout.write(
            self.style.SUCCESS('MPs linked to committees!')
        )
