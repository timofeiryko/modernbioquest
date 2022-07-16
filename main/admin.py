from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet

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

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    model = Question
    inlines = [RightAnswerIine]

admin.site.register(RightAnswer)