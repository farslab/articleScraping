from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html

from . import views


def searchPage(request):
    
    return HttpResponse("Arama sayfası")
    

urlpatterns = [
    
    path('', views.PublicationListView.as_view(), name='publication_list'),
    path('scrape/', views.scrape, name='scrape'),
    path('download/', views.download_file, name='download_file'),
    path('publication_details/<int:id>/',views.publicationDetails, name='publication_details'),

    
]

