
import json
import os
import time
from pprint import pprint

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from django.conf import settings
from search.utils import get_embeddings_model



class ElasticSearch():
    def __init__(self):
        self.elastic_auth = settings.ELASTICSEARCH_DSL["default"]["hosts"]
        self.es = Elasticsearch(self.elastic_auth)
        self.index_name = 'paragraphs'
        print("Connected to ElasticSearch")
        client_info = self.es.info()
        pprint(client_info.body)
    
    def search(self, **query_args):
        return self.es.search(index=self.index_name, **query_args)
    
    @staticmethod
    def get_total_hits(results):
        return results["hits"]['total']['value']
    
    def search_match(self, query):
        results = self.es.search(
            query={
                'match': {
                    'text': {
                        'query': query
                    }
                }
            }
        )
        return results

    def search_knn(self, query):
        results = self.es.search(
            knn={
                'field': 'dense_vector',
                'query_vector': self.vectorize_query(query),
                'num_candidates': 50,
                'k': 10,
            }
        )
        return results
    
    @staticmethod
    def vectorize_query(query):
        model = get_embeddings_model()
        dense_vector = model.encode(query)
        return dense_vector
    