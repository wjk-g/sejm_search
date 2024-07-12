import json
import random

from django.db.models import OuterRef, Exists
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from requests.exceptions import MissingSchema

from search.models import (
    Sitting,
    Transcript,
    Term,
)

from data_collection.get_transcripts import get_html_data

class Command(BaseCommand):
    help = "Create transcripts"

    def handle(self, *args, **options):

        # Get all sittings from the database
        # It seems that sittings < term 7 have not been transcribed
        

        terms_with_transcripts = Term.objects.filter(number__gte=7)
        #random_transcripts = [random.randint(0, 17174) for _ in range(25)]
        #sittings = Sitting.objects.filter(term__in=terms_with_transcripts)
        #sittings = [sittings[i] for i in random_transcripts]
        #print(len(sittings)) # 17 174

        sittings_without_transcript = Sitting.objects.filter(
            term__in=terms_with_transcripts
        ).filter(
            ~Exists(Transcript.objects.filter(sitting=OuterRef('pk')))
        )


        for sitting in sittings_without_transcript[:500]:
            # Check if the sitting already has a transcript assigned
            transcript_exists = Transcript.objects.filter(sitting=sitting).exists()
            if not transcript_exists:
                term_number = sitting.term.number
                sitting_number = sitting.number
                committee_code = sitting.committee.code
                sitting_transcript_url = f"https://api.sejm.gov.pl/sejm/term{term_number}/committees/{committee_code}/sittings/{sitting_number}/html"
                
                try:
                    transcript_text = get_html_data(sitting_transcript_url)
                    if len(transcript_text) > 0:
                        Transcript.objects.create(
                            sitting = sitting,
                            text = transcript_text,
                        )
                        print(f"Added transcript for committee {committee_code}, sitting: {sitting_number}, term: {term_number}.")
                    else:
                        print(f"Transcript text is emtpy, transcript is probably not available ({committee_code}, {sitting_number}, {term_number}).")

                except MissingSchema as e:
                    print(e)
        
        self.stdout.write('Transcript added!')
