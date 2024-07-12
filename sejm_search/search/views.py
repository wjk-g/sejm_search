from typing import Any
from pprint import pprint
from datetime import datetime

#from elasticsearch_dsl import Search as ElasticSearch
from sentence_transformers import SentenceTransformer

from django.http import HttpResponse
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.views.generic import View, FormView, DetailView

from search.documents import ParagraphDocument
from search.forms import ParagraphSearchForm

from search.models import (
    Transcript, 
    Sitting, 
    TermMP, 
    CommitteeTermMP, 
    MP,
    Paragraph,
)

from search.elastic_search_setup.elasticsearch import ElasticSearch


es = ElasticSearch()

class Search(FormView):
    template_name = "search.html"
    form_class = ParagraphSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query = None
        search_type = None
        order = None
        total_hits = None

        # Get search and filter parameters
        if self.request.method == "POST":
            form = self.get_form()
            if form.is_valid():
                query = form.cleaned_data['query']
                search_type = form.cleaned_data['search_type']
                order = form.cleaned_data['order']

                # Store in session for filtering and downloading
                self.request.session['query'] = query
                self.request.session['search_type'] = search_type
                self.request.session['order'] = order
        elif self.request.method == "GET": 
            # Load from session for GET requests
            query = self.request.session.get('query')
            search_type = self.request.session.get('search_type')
            order = self.request.session.get('order')
        
        # Perform elasticsearch query
        if query and search_type:
            if search_type == "simple": 
                results = es.search_match(query)
            elif search_type == "smart":
                results = es.search_knn(query)
            
            # Get total number of results
            total_hits = es.get_total_hits(results)
            
            # Format the results
            individual_results = results['hits']['hits']
            paragraphs = [result['_source'] for result in individual_results]

            # Match sittings to transcript
            sitting_ids = [paragraph["sitting"]["pk"] for paragraph in paragraphs]
            transcripts = Transcript.objects.filter(sitting_id__in=sitting_ids).values('sitting_id', 'id')
            sitting_to_transcript_map = {t["sitting_id"]: t["id"] for t in transcripts}
            
            for p in paragraphs:
                p['transcript_id'] = sitting_to_transcript_map.get(p['sitting']['pk'])
                p["sitting"]["date"] = datetime.strptime(p["sitting"]["date"], "%Y-%m-%d").date()

            if order == 'chrono': 
                paragraphs = sorted(paragraphs, key=lambda x: x['sitting']['date'])

            context['paragraphs'] = paragraphs
            context['total_hits'] = total_hits

        return context

    
    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


def full_statement(request, statement_id):
    # Logic to get or generate new text
    paragraphs = Paragraph.objects.filter(statement_id=statement_id).order_by('place_in_statement')
    paragraphs_text = [f'<p>{p.text}</p>' for p in paragraphs]
    full_statement = ''.join(paragraphs_text)

    return HttpResponse(full_statement)


class ClearSearchParams(View):
    def get(self, request):
        search_parameters = ['query', 'search_type', 'order']
        for key in search_parameters:
            request.session.pop(key, None)

        return redirect('search')


class FullTranscript(DetailView):
    template_name = "full_transcript.html"
    model = Transcript


class MPView(DetailView):
    template_name = "mp_view.html"
    model = MP

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        # Returns context dict with a following structure:
        # {'object': <MP: MP object (3330)>, 'mp': <MP: MP object (3330)>, 'view': <search.views.MPView object at 0x119fda9f0>}
        # get_object method gets context['mp']
        context = super().get_context_data(**kwargs)
        mp_object = context["mp"]
        
        ctmps = CommitteeTermMP.objects.filter(mp=mp_object).select_related('term').order_by('term__number')
        
        term_committees = {}
        for ctmp in ctmps:
            term = ctmp.term
            if term not in term_committees:
                term_committees[term] = []
            term_committees[term].append(ctmp)
        
        mp_info_package = {
            'mp_name': mp_object.name,
            'term_committees': term_committees,
        }

        context['mp_info'] = mp_info_package

        return context


class CommitteeView(DetailView):
    template_name = "committee_view.html"
    model = CommitteeTermMP
