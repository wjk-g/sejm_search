from django.core.management.base import BaseCommand
from django.conf import settings
from elasticsearch import Elasticsearch
#from search._documents import ParagraphDocument

#class Command(BaseCommand):
#    help = 'Rebuild the Elasticsearch index'
#
#    def handle(self, *args, **options):
#        es = Elasticsearch(
#            hosts=[settings.ELASTICSEARCH_DSL['default']['hosts']],
#            ignore=[400, 404], 
#            ignore_unavailable=True
#        )
#        #index_name = ParagraphDocument._index._name
#        es.indices.delete(index='paragraphs')
#        
#        self.stdout.write(self.style.SUCCESS("Deleted the search index"))