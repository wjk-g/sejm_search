
import json 

from sentence_transformers import SentenceTransformer
from django.core.management.base import BaseCommand

from search.models import (
    Term,
    Committee,
    Sitting,
    Paragraph,
    Statement,
    Transcript,
)


class Command(BaseCommand):
    help = "Vectorize paragraphs"

    def handle(self, *args, **options):

        print("Loading model...")
        model = SentenceTransformer('sdadas/st-polish-paraphrase-from-distilroberta')
        print("Model loaded.")

        #all_committees = Committee.objects.all()
        #for committee in all_committees:
        #    vectorize_paragraphs_for_committee(committee)
        
        #def get_paragraphs_for_committee(term_number, committee_code):
        #    term = Term.objects.get(number=term_number)
        #    committee = Committee.objects.get(code=committee_code, term=term_number)
        #    sittings = Sitting.objects.filter(committee=committee)
        #    transcripts = Transcript.objects.filter(sitting__in=sittings)
        #    statements = Statement.objects.filter(transcript__in=transcripts)
        #    paragraphs = Paragraph.objects.filter(statement__in=statements)
        #    return paragraphs

        def vectorize_paragraph(paragraph, model):
            dense_vector = model.encode(paragraph)
            print("Paragraph vectorized.")         
            return dense_vector

        #paragraphs = get_paragraphs_for_committee(9, "EPS")

        def serialize_ndarray(ndarray):
            return json.dumps(ndarray.tolist())
        
        paragraphs = Paragraph.objects.filter(dense_vector__isnull=True)

        for paragraph in paragraphs:
            dense_vector = vectorize_paragraph(paragraph.text, model)
            paragraph.dense_vector = serialize_ndarray(dense_vector)
            paragraph.save()

        self.stdout.write(
            self.style.SUCCESS('Paragraphs vectorized!')
        )
