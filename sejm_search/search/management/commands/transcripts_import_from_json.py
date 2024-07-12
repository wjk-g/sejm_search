
import json
import pandas as pd

from django.core.management.base import BaseCommand

from search.models import (
    Transcript,
)

from data_collection.get_transcripts import get_html_data

class Command(BaseCommand):
    help = "Create transcripts"

    def add_arguments(self, parser):
        parser.add_argument('--json_file', type=str, help='JSON file name')

    def handle(self, *args, **options):

        json_file = options["json_file"]

        transcripts = Transcript.objects.all()

        data = []
        for transcript in transcripts:
            row = {
                "term": transcript.sitting.term.number,
                "committee_code": transcript.sitting.committee.code,
                "sitting_number": transcript.sitting.number,
                "text": transcript.text,
            }
            data.append(row)
        
        df = pd.DataFrame.from_dict(data)
        current_date = date.today()
        df.to_json(f"data_collection/data/transcripts_{current_date}.json", indent=4, orient="records")
        
        self.stdout.write(
            self.style.SUCCESS('Transcripts exported to JSON')
        )
