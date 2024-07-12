from django.core.cache import cache
from sentence_transformers import SentenceTransformer

def get_embeddings_model():
    
    model = cache.get('embeddings_model')

    if model is None:
        model = SentenceTransformer('sdadas/st-polish-paraphrase-from-distilroberta')
        cache.set('embeddings_model', model, timeout=None)
    
    return model