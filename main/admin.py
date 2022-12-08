from django.contrib import admin

import nested_admin

from .models import Competition, Stage, Explanation, Section, Topic, Image, ImageAlbum, Question, RightAnswer, TestQuestion, Test
admin.site.register([Competition, Stage, Explanation, Section, Image, Test])

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
    list_filter = ['listed', 'competition', 'year', 'stage']

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