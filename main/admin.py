from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

import nested_admin

from django.db.models import QuerySet, Model
from django.http import HttpRequest

from typing import Any, Tuple

from .services import filter_questions_by_query

from .models import Competition, NewStage, Explanation, Section, Topic, Image, ImageAlbum, Question, RightAnswer, TestQuestion, Test, Profile
admin.site.register([Competition, NewStage, Explanation, Section, Image, Test, Profile])

@admin.register(Topic)
class TopicAdmin(nested_admin.NestedModelAdmin):
    list_display = ['name', 'parent_section']
    list_filter = ['parent_section']

class ImageLine(nested_admin.NestedStackedInline):
    model = Image

@admin.register(ImageAlbum)
class ImageAlbumAdmin(nested_admin.NestedModelAdmin):
    model = ImageAlbum
    inlines = [ImageLine]


class RightAnswerIine(admin.TabularInline):
    model = RightAnswer
    extra = 4

    def get_form(self, request, obj=None, **kwargs):
        return super().get_form(request, obj, **kwargs)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    model = Question
    inlines = [RightAnswerIine]
    exclude = ['quauthor']
    search_fields = ['title', 'text']

    def save_model(self, request, obj, form, change): 
        obj.user = request.user
        obj.save()

    def save_formset(self, request, form, formset, change): 
        if formset.model == Question:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.quauthor = request.user
                instance.save()
        else:
            formset.save()

    list_display = ['verbose_title', 'part', 'number']
    list_filter = ['listed', 'competition', 'year', 'new_stage']


    def get_search_results(self, request: HttpRequest, queryset: QuerySet[Any], search_term: str) -> Tuple[QuerySet[Any], bool]:
        use_distinct = True
        if search_term:
            queryset = filter_questions_by_query(query=search_term, questions=queryset)

        return queryset, use_distinct

@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):

    model = TestQuestion
    inlines = [RightAnswerIine]
    exclude = ['quauthor']

    def save_model(self, request, obj, form, change): 
        obj.user = request.user
        obj.save()

    def save_formset(self, request, form, formset, change): 
        if formset.model == Question:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.quauthor = request.user
                instance.save()
        else:
            formset.save()

    list_display = ['parent_test', 'shortened']
    list_filter = ['parent_test']


    

admin.site.register(RightAnswer)