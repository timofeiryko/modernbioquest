"""Conventioanal Django ORM models. Domain logic (aka business logic) is not here! It is in `services.py`."""

from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import URLValidator

from polymorphic.models import PolymorphicModel

# from .services import QuestionService

class BaseModel(models.Model):
    """From this model we inherit most of the models associated with different features."""

    created_at = models.DateTimeField('Created', auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField('Modified', auto_now=True)

    class Meta:
        abstract = True

class BasePolymorphic(PolymorphicModel):
    """From this model we inherit some of the models, which are a qukte abstract."""

    created_at = models.DateTimeField('Created', auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField('Modified', auto_now=True)

    class Meta:
        abstract = True

class Profile(BaseModel):
	user = models.OneToOneField(User, on_delete=models.CASCADE)

class ImageAlbum(BaseModel):
    """To have an ability to add multiple images to models"""

    @property
    def model(self):
        """To get the model, which refers to the ImageAlbum instance (among the models having multple images)"""

        fields =  ImageAlbum._meta.get_fields()
        related_models = [field.name for field in fields if field.get_internal_type() == 'OneToOneField']

        for related_model in related_models:
            if hasattr(self, related_model):
                return getattr(self, related_model)


    def __str__(self):
        if self.model is None:
            return 'Набор изображений'
        return f'Изображения для "{self.model}" ({self.model._meta.verbose_name.title()})'
    
    class Meta:
        verbose_name = 'Набор изображений'
        verbose_name_plural = 'Наборы изображений'
        ordering = ['-id']

class Image(BaseModel):
    """To store images for the models"""

    file = models.ImageField('Файл', upload_to='images/')
    album = models.ForeignKey(ImageAlbum, related_name='images', on_delete=models.CASCADE, verbose_name='Набор изображений')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        if self.album.model is None:
            return 'Изображение'
        return f'Изображение для "{self.album.model}" ({self.album.model._meta.verbose_name.title()})'


class Section(BaseModel):
    """To sort questions by quite big areas of knowledge. Every question can be in multiple sections."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('section_url', kwargs={'slug': self.slug})

class Topic(BaseModel):
    """To sort questions by particular topics. Every question can have multiple topics."""
    
    parent_section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, related_name='topics')
    name = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['parent_section', 'name']
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'
    
    def __str__(self):
        return self.name

class Competition(BaseModel):
    """To sort questions by competition, where they were taken from."""

    name = models.CharField('Олимпиада', max_length=300, default='ВсОШ', null=True)
    link = models.CharField('Ссылка', max_length=300, validators=[URLValidator()])

    class Meta:
        ordering = ['name']
        verbose_name = 'Олимпиада'
        verbose_name_plural = 'Олимпиады'

    def __str__(self):
        return self.name

class BaseQuestion(BasePolymorphic):
    """Abstract model to store different questions: both olympiads and just tests."""

    text = models.TextField('Текст вопроса', null=True)

    max_score = models.FloatField('Балл', null=True, default=0.0)    
    @property
    def answers_num(self):
        answers = [ans for ans in self.right_answers.all() if ans.is_full_answer]
        return len(answers)

    images = models.OneToOneField(ImageAlbum, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Иллюстрации к вопросу')

    quauthor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='%(class)s',
        verbose_name='Добавил вопрос'
    )

    sections = models.ManyToManyField(
        Section, blank=True,
        related_name='%(class)s', verbose_name=Section._meta.verbose_name_plural.title()
    )
    topics = models.ManyToManyField(
        Topic, blank=True, 
        related_name='%(class)s', verbose_name=Topic._meta.verbose_name_plural.title()
    )

    class Types(models.TextChoices):
        PART1 = 'P1', ('1 правильный ответ')
        PART2 = 'P2', ('Множественный выбор')
        RELATE = 'REL', ('Соответствие')
        STR = 'STR', ('Текстовые пункты')

    type = models.CharField(
        'Тип',
        max_length=4,
        choices=Types.choices,
        default=Types.STR,
    )

class Question(BaseQuestion):
    """To store questions from olympiads. Main model with a lot of information.
    Related domain-speccific aspects are in `services.py`."""
    
    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, null=True,
        related_name='questions', verbose_name=Competition._meta.verbose_name.title()
    )

    year = models.IntegerField('Год проведения', null=True)
    stage = models.CharField('Этап', max_length=100, null=True)
    grade = models.IntegerField('Класс', null=True)

    part = models.CharField('Часть', max_length=100, null=True)
    number = models.IntegerField('Номер', null=True)

    class Meta:
        verbose_name = 'Вопрос с олимпиады'
        verbose_name_plural = 'Вопросы с олимпиад'
        ordering = ['-id']

    def __str__(self):
        shortened = str(self.text)[:25] + '...'
        return shortened

class SolvedQuestion(BaseModel):
    """To store information about the questions solved by different users."""

    parent_question = models.ForeignKey(BaseQuestion, on_delete=models.CASCADE, related_name='solved')

    user_text = models.TextField('Текст вопроса', null=True)
    
    user_score = models.FloatField('Балл', null=True, default=0.0)

    # TODO: it should be equal to the number of answers, validator
    user_points = models.IntegerField('Количество ответов', null=True)
    
    solved_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='solved_questions',
        verbose_name='Решено пользователем'
    )

class BaseAnswer(BaseModel):
    """To store answers for the questions. It is an abstract class, because there are dufferent types of answers: right and user.
    Right answer has foreign key to polymorphic BaseQuestion, user answer - to SolvedQuestion.
    We need it, because we want to have an ability to add multiple answers for one question (if we have several points in it, for example)."""

    label = models.TextField('Вариант или название пункта', null=True)

    text = models.TextField('Текстовый ответ', null=True, blank=True)
    flag = models.BooleanField('Выбор варианта', null=True, blank=True)

    @property
    def has_flag(self) -> bool:
        return not (self.flag is None)
    
    @property
    def is_full_answer(self) -> bool:
        return self.text or self.has_flag

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return 'Вариант или пункт'
    
class RightAnswer(BaseAnswer):
    """To store answers for the questions.
    We need it, because we want to have an ability to add multiple answers for one question (if we have several points in it, for example)."""
    
    parent_question = models.ForeignKey(BaseQuestion, on_delete=models.CASCADE, null=True, blank=True, related_name='right_answers')

    class Meta:
        ordering = ['parent_question']
        verbose_name = 'Вариант или пункт'
        verbose_name_plural = 'Вариант или пункт'

class UserAnswer(BaseAnswer):
    """To store answers for the questions.
    We need it, because we want to have an ability to add multiple answers for one question (if we have several points in it, for example)."""

    parent_solved = models.ForeignKey(SolvedQuestion, on_delete=models.CASCADE, null=True, blank=True, related_name='user_answers')
    is_right = models.BooleanField('Выбор варианта', null=True, blank=True)

    class Meta:
        ordering = ['parent_solved']
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы пользователей'


class Explanation(BaseModel):
    """To store explanations for the questions."""

    parent_question = models.OneToOneField(BaseQuestion, on_delete=models.CASCADE, null=True, blank=True)

    text = models.TextField('Разбор, комментарии', blank=False)
    images = models.OneToOneField(ImageAlbum, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Иллюстрации к разбору')

    explauthor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='comments',
        verbose_name='Добавил разбор'
    )

    mark = models.BooleanField('Проверено экспертом', default=False)

    class Meta:
        ordering = ['parent_question']
        verbose_name = 'Разбор'
        verbose_name_plural = 'Разборы'