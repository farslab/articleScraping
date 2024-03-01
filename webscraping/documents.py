from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Publication


@registry.register_document
class PublicationDocument(Document):
    class Index:
        title = 'publications_index'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Publication
        fields = ['title', 'authors', 'abstract', 'publication_type']

        
print(PublicationDocument.Index.title)
