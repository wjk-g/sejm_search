
import json
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Paragraph
from elasticsearch import Elasticsearch
from django.conf import settings
import numpy as np
from elasticsearch_dsl import DenseVector


@registry.register_document
class ParagraphDocument(Document):
    print("Initializing ParagraphDocument...")

    speaker_mp = fields.ObjectField(properties={
        'pk': fields.IntegerField(),
        'name': fields.TextField(),
        'birth_date': fields.DateField(),
    })

    speaker_guest = fields.ObjectField(properties={
        'pk': fields.IntegerField(),
        'name': fields.TextField(),
    })
    
    statement = fields.ObjectField(properties={
        'pk': fields.IntegerField(),
    })

    term = fields.ObjectField(properties={
        'number': fields.IntegerField(),
    })

    committee = fields.ObjectField(properties={
        'pk': fields.IntegerField(),
        'name': fields.TextField(),
        'code': fields.TextField(),
    })

    sitting = fields.ObjectField(properties={
        'pk': fields.IntegerField(),
        'date': fields.DateField(),
        'number': fields.Integer(),
    })

    dense_vector = DenseVector(dims=768)

    class Index:
        name = 'paragraphs'

    class Django:
        model = Paragraph
        fields = [
            'text',
            'place_in_statement',
        ]

    def prepare(self, instance):
        data = super().prepare(instance)
        data['dense_vector'] = self.prepare_custom_dense_vector(instance)
        return data

    def prepare_custom_dense_vector(self, instance):
        print("Preparing dense vector") 
        try:
            vector_data = json.loads(instance.dense_vector)
            if isinstance(vector_data, list) and len(vector_data) == 768:
                return [float(v) for v in vector_data]
            else:
                print(f"Invalid vector format for instance {instance.id}")
                return None
        except json.JSONDecodeError:
            print(f"JSON decode error for instance {instance.id}")
            return None
        except Exception as e:
            print(f"Error processing instance {instance.id}: {str(e)}")
            return None

    def prepare_speaker_mp(self, instance):
        if instance.speaker_mp:
            return {
                'pk': instance.speaker_mp.pk,
                'name': instance.speaker_mp.name,
                'birth_date': instance.speaker_mp.birth_date
            }
        else: 
            return None

    def prepare_speaker_guest(self, instance):
        if instance.speaker_guest:
            return {
                'pk': instance.speaker_guest.pk,
                'name': instance.speaker_guest.name,
            }
        else: 
            return None

    def prepare_statement(self, instance):
        return {
            'pk': instance.statement.pk,
        }

    def prepare_sitting(self, instance):
        return {
            'pk': instance.sitting.pk,
            'date': instance.sitting.date,
            'number': instance.sitting.number,
        }
