from elasticsearch_dsl import analyzer, tokenizer, analysis
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Question, Section, Topic

index_settings = {
    'analysis': {
        'filter': {
            'russian_stemmer': {
                'type': 'snowball',
                'language': 'russian'
            }
        },
        'analyzer': {
            'standard': {
                'type': 'custom',
                'tokenizer': 'standard',
                'filter': ['lowercase', 'stop', 'russian_stemmer']
            }
        }
    }
}


standard_analyzer = analyzer(
    'standard',
    tokenizer=tokenizer('standard'),
    filter=['lowercase', 'stop', analysis.token_filter('russian_stemmer', type='snowball', language='russian')]
)

@registry.register_document
class QuestionDocument(Document):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._index.settings(
            analysis=index_settings['analysis']
        )

    text = fields.TextField(analyzer=standard_analyzer)
    title = fields.TextField(analyzer=standard_analyzer)
    sections = fields.NestedField(properties={
        'name': fields.TextField(analyzer=standard_analyzer),
    })
    topics = fields.NestedField(properties={
        'name': fields.TextField(analyzer=standard_analyzer),
    })

    class Index:
        name = 'questions'
        settings = index_settings


    class Django:
        model = Question
        fields = ['id', 'listed']
        ignore_signals = True

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Section):
            return related_instance.questions.listed()
        elif isinstance(related_instance, Topic):
            return related_instance.questions.listed()
        return []

    def get_queryset(self):
        return super().get_queryset().filter(listed=True)

    def prepare_sections(self, instance):
        return [{'name': section.name} for section in instance.sections.all()]

    def prepare_topics(self, instance):
        return [{'name': topic.name} for topic in instance.topics.all()]

    def prepare(self, instance):
        prepared_data = super().prepare(instance)

        # Add question text to searchable fields
        prepared_data['text'] = instance.text

        # Add question title to searchable fields
        prepared_data['title'] = instance.title

        # Add related section and topic names to searchable fields
        prepared_data['sections'] = self.prepare_sections(instance)
        prepared_data['topics'] = self.prepare_topics(instance)

        return prepared_data
