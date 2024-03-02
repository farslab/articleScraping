from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Publication
from elasticsearch_dsl import connections

# Elasticsearch bağlantısını oluşturun
# connections.create_connection(alias='default', hosts=['http://localhost:9200'], timeout=20)

@registry.register_document
class PublicationDocument(Document):
    class Index:
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}
        name="pub_index"
    class Django:
        model = Publication
        fields = ['title', 'authors', 'abstract', 'publication_type']

