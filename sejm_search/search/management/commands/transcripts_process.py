import json

from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef

from search.models import (
    TermMP,
    Transcript,
    Statement,
    Paragraph,
    GuestSpeaker,
)

class Command(BaseCommand):
    help = "Process transcript"

    def handle(self, *args, **options):

        # Get all sittings from the database
        #transcripts = Transcript.objects.filter(dense_vector__isnull=False)
        unprocessed_transcripts = Transcript.objects.filter(
            ~Exists(
                Paragraph.objects.filter(
                    statement__transcript=OuterRef('pk')
                )
            )
        )

        for transcript in unprocessed_transcripts:
            
            statements_exist = Statement.objects.filter(transcript=transcript).exists()
            
            transcript_term = transcript.sitting.term
            # From that point onwards we're only dealing with unprocessed transcripts 
            if not statements_exist:
                parsed = transcript.get_structured_data_from_transcript()
                #print(f"Printing parsed transcript: {parsed}")
                
                # Parsed is a list of dicts containing statements from mps
                # It has a following structure:
                #{ 
                # speaker: "Poseł Jan Łopata (PSL-Kukiz15)"
                # utterances: ['Zachowanie pani poseł było niegodne.', '...' ]
                # }

                # Committee members
                mps_in_committee = [
                    TermMP.objects.get(mp_term_id=member_id, term=transcript_term).mp
                    for member_id in transcript.sitting.committee.member_ids
                ]

                # Speakers listed in the "Speakers" ("Mówcy") section of the transcript
                speakers_listed = transcript.get_speaker_list()
                mps_in_term = TermMP.objects.filter(term=transcript_term)

                for i, statement in enumerate(parsed):
                    speaker = statement.get("speaker")
                    #print(statement)
                    #print(transcript.sitting.pk)
                    #print(f"Printing speaker: {speaker}")
                    
                    # On some occassions non-member MPs speak during sittings
                    # They should be included in the "Speakers" ("Mówcy") section of the transcript
                    def is_mp(speaker):
                        # Check if the speaker is a committee member
                        for mp in mps_in_committee:
                            if mp.name.lower() in speaker.lower():
                                return mp
                            # Check the scenario when a full name is included in the transcript
                            # Pay attention to the extra whitespace
                            second_name = f"{mp.second_name} " if mp.second_name else ""
                            full_name = f"{mp.first_name} {second_name}{mp.family_name}".strip()
                            print(full_name)
                            if full_name.lower() in speaker.lower():
                                return mp

                        # Some MPs have their full name (first middle and last) in the field first_last_name
                        # Np. Dariusz Cezar Dziadzio :)
                        # If previous check fails, check if the speaker is in the list of mps for a given term
                        for termmp in mps_in_term:
                            if termmp.mp.name.lower() in speaker.lower():
                                return termmp.mp
                        # If the speaker is not mp
                        return None
                    
                    mp = is_mp(speaker)

                    if mp:
                        statement_obj = Statement.objects.create(
                            speaker = mp,
                            transcript = transcript,
                            place_in_transcript = i,
                        )
                        guest_speaker = None
                    
                    if not mp:
                        guest_speaker, created = GuestSpeaker.objects.get_or_create(
                            name = speaker
                        )

                        statement_obj = Statement.objects.create(
                            guest_speaker = guest_speaker,
                            transcript = transcript,
                            place_in_transcript = i,
                        )
                        mp = None
                    
                    for i, paragraph in enumerate(statement.get("utterances")):

                        Paragraph.objects.create(
                            statement = statement_obj,
                            place_in_statement = i,
                            text = paragraph,
                            speaker_mp = statement_obj.speaker, 
                            speaker_guest = statement_obj.guest_speaker,
                            sitting = statement_obj.transcript.sitting,
                            committee = statement_obj.transcript.sitting.committee,
                            term = transcript_term,
                        )

        # Parse transcripts into a desired format (speaker - statement - paragraph)
            # Assign positions to statements and paragraphs  
            # Get MPs who are members of a given committee during a given term (Extract all speakers first)
            # Compare speakers with the list of MPs
            # If there's a match - link statement with mp
            # If there's no match add guest to the db
        
        self.stdout.write('Transcripts processed!')
