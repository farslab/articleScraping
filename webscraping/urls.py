from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html
from . import views


def searchPage(request):
    
    return HttpResponse("Arama sayfası")
    

urlpatterns = [
    
    path('', views.PublicationListView.as_view(), name='publication_list'),
    path('scrape/', views.scrape, name='scrape'),
    path('publication_details/<int:id>/', views.PublicationDetailView.as_view(), name='publication_details'),

    
]

