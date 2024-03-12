from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Publication
from elasticsearch_dsl import connections


@registry.register_document
class PublicationDocument(Document):
    class Index:
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}
        name="pub_index"
    class Django:
        model = Publication
        fields = ['title', 'authors', 'abstract', 'publication_type']

