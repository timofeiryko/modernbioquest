from django.contrib import admin

import nested_admin

from .models import Competition, Explanation, Section, Topic, Image, ImageAlbum, Question, RightAnswer
admin.site.register([Competition, Explanation, Section, Topic, Image])

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
        print('RIGHT ANSWER ARGS:')
        print(locals())
        print('---')
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
    

admin.site.register(RightAnswer)