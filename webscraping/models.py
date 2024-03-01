# web_scraping/models.py
from django.db import models


class Publication(models.Model):
    title = models.CharField(max_length=255)
    authors = models.TextField(null=True, default="None")
    publication_type = models.CharField(null=True,max_length=50,default="None")
    publication_date = models.DateField(null=True)
    publisher_name = models.CharField(max_length=100,default="None")
    keywords_searched = models.TextField(default="None")
    keywords_article = models.TextField(null=True,default="None",blank=True)
    abstract = models.TextField(null=True,blank=True)
    references = models.TextField(null=True,default="None",blank=True)
    citation_count = models.CharField(max_length=100,null=True,blank=True)
    doi_number = models.CharField(max_length=50, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)


    def __str__(self):
        return self.title   
