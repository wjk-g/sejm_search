
from django.contrib import admin
from django.urls import path, include
from search import views as search


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", search.Search.as_view(), name="home"),
    path("search/", search.Search.as_view(), name="search"),
    path("clear_search_params", search.ClearSearchParams.as_view(), name="clear_search_params"),
    path("full_transcript/<int:pk>/", search.FullTranscript.as_view(), name="full_transcript"),
    path("mp_view/<int:pk>/", search.MPView.as_view(), name="mp_view"),
    path("committee_view/<int:pk>", search.CommitteeView.as_view(), name="committee_view"),
    path("full_statement/<int:statement_id>", search.full_statement, name="full_statement"),
]
