
import pandas as pd

from django.core.management.base import BaseCommand

from search.models import (
    Statement,
)

class Command(BaseCommand):
    help = "Export all statements from db"

    def handle(self, *args, **options):

        statements = Statement.objects.all()
        
        data = []
        
        for statement in statements:

            if statement.guest_speaker:
                guest_speaker = statement.guest_speaker.name
            else:
                guest_speaker = ""

            if statement.speaker:
                speaker = statement.speaker.first_last_name
            else:
                speaker = ""
            
            row = {
                "id": statement.pk,
                "place_in_transcript": statement.place_in_transcript,
                "guest_speaker": guest_speaker,
                "speaker": speaker,
                "transcript": statement.transcript.pk,
                "sitting_info": str(statement.transcript.sitting.term.number) + " " + statement.transcript.sitting.committee.code + " " + str(statement.transcript.sitting.number) 
            }

            data.append(row)

        df = pd.DataFrame.from_dict(data)
        df.to_csv("data_collection/data/statements_output.csv")

        self.stdout.write('Statements exported!')
