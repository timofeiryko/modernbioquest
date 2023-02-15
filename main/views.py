from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from django_registration.backends.one_step.views import RegistrationView

from .models import Question, Section, Competition, NewStage, Topic
from .configs import QUESTIONS_PER_PAGE
from .services import get_question_by_link, get_questions_by_sections, filter_questions_by_query, advanced_filter_service

import git

LOG_IN_URL = "{% url 'main: %}"
NOT_LOGGED_IN_MESSAGE = f'<br><b><a href="">Войдите</a> или <a href="">зарегистрируйтесь</a></b>, чтобы сохранять вопросы и получить доступ к дополнительным возможностям!'

@csrf_exempt
def update(request):
    if request.method == 'POST':

        try:
            repo = git.Repo('quest.pythonanywhere.com')
            origin = repo.remotes.origin
            origin.pull()
        except Exception as e:
            return HttpResponse(e)

        return HttpResponse('Updated code on PythonAnywhere')
    else:
        return HttpResponse("Couldn't update the code on PythonAnywhere")


def show_selected_questions(request, questions, h1_content: str, p_content: str, **kwargs):

    # get dict of get params withouth page
    get_params = request.GET.copy()
    if 'page' in get_params:
        get_params.pop('page')

    paginator = Paginator(questions, QUESTIONS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    is_paginated = page.has_other_pages()
    prev_url = f'?page={page.previous_page_number()}' if page.has_previous() else ''
    next_url = f'?page={page.next_page_number()}' if page.has_next() else ''
    last_url = f'?page={page.paginator.num_pages}' if page.has_next() else ''

    # generate dict of urls with page numbers uaing page.paginator.page_range and add get params to them
    page_urls = {}
    for page_number in page.paginator.page_range:
        page_urls[page_number] = f'?page={page_number}'
        if get_params:
            page_urls[page_number] += ('&' + get_params.urlencode())
    
    # generate urls for pagination with get params
    if get_params:
        if prev_url:
            prev_url += ('&' + get_params.urlencode())
        if next_url:
            next_url += ('&' + get_params.urlencode())
        if last_url:
            last_url += ('&' + get_params.urlencode())

    sections = Section.objects.order_by('name')

    context = {
        'nav': [False, True, False, False],
        'questions': page,
        'is_paginated': is_paginated,
        'next_url': next_url,
        'prev_url': prev_url,
        'last_url': last_url,
        'h1_content': h1_content,
        'p_content': p_content,
        'sections': sections,
        'page_urls': page_urls
    }

    # add kwargs to context
    context.update(kwargs)

    return render(request, 'problems.html', context=context)

def advanced_filter(questions, request, requested_sections):
    # TODO: TO SERVICES?

    requested_topics = request.GET.getlist('topic')

    requested_competitions = request.GET.getlist('competition')
    requested_stages = request.GET.getlist('stage')

    requested_years = request.GET.getlist('year')
    requested_parts = request.GET.getlist('part')

    questions, p_content = advanced_filter_service(
        questions,
        requested_topics,
        requested_sections,
        requested_competitions,
        requested_stages,
        requested_years,
        requested_parts
    )

    if not questions:
        h1_content = ''
        p_content = 'Ничего не найдено :( <a href="https://vk.me/join/p/R7YSQ1Hda3q0dE5Dn6qOmFVvSveP7WRTE=">Помогите нам с наполнением базы вопросов!</a>'
    else:
        h1_content = 'Ваш персональный набор вопросов'
        p_content += 'Кроме фильтров, на сайте есть поиск!'

    # TODO; automatically add new fields to this filter

    # additional listed filtration as a quick fix (actually there is some bug above)
    questions = questions.filter(listed=True)

    return questions, h1_content, p_content

def problems(request):

    # extract search query from the get request
    requested_query = request.GET.get('query')

    # extract multipe sections from the get request
    requested_sections_slugs = request.GET.getlist('section')
    requested_sections = None
    if requested_sections_slugs:
        requested_sections = Section.objects.filter(slug__in=requested_sections_slugs)
        questions = get_questions_by_sections(requested_sections)
    else:
        questions = Question.objects.order_by('-id').filter(listed=True)

    fitler_type = request.GET.get('filter')
    if fitler_type:
        if fitler_type == 'advanced':
            questions, h1_content, p_content = advanced_filter(questions, request, requested_sections)
        else:
            raise NotImplementedError
    else:

        # extract topic from the get request
        requested_topic = request.GET.get('topic')

        if requested_sections_slugs:

            h1_content = ''
            if questions:
                p_content = f'Вопросы по разделам: <b>{", ".join([section.name for section in requested_sections])}</b>'
            else:
                p_content = f'По запрошенным разделам <b>{", ".join([section.name for section in requested_sections])}</b> ничего не найдено :( <a href="https://vk.me/join/p/R7YSQ1Hda3q0dE5Dn6qOmFVvSveP7WRTE=">Помогите нам с наполнением базы вопросов!</a>'

        elif requested_topic:
                # TODO: DRY - this code is the same in filter by query service
                questions = Question.objects.order_by('-id').filter(listed = True, topics__name__icontains=requested_topic)
        
                h1_content = ''
                if questions:
                    p_content = f'Вопросы по теме <b>{requested_topic}</b>'
                else:
                    p_content = f'По запрошенной теме <b>{requested_topic}</b> ничего не найдено :( <a href="https://vk.me/join/p/R7YSQ1Hda3q0dE5Dn6qOmFVvSveP7WRTE=">Помогите нам с наполнением базы вопросов!</a>'

        else:

            questions = Question.objects.order_by('-id').filter(listed = True)

            h1_content = 'Коллекция вопросов с ответами'
            p_content = 'Вы можете выбрать вопросы по разделам или темам в меню справа (с мобильного устройства — снизу)'

    if requested_query:

        questions = filter_questions_by_query(requested_query, questions)

        h1_content = ''
        if questions:
            p_content = f'Всё, что мы нашли по запросу <b>{requested_query}</b>'
        else:
            p_content = f'По запросу <b>{requested_query}</b> ничего не найдено :( <a href="https://vk.me/join/p/R7YSQ1Hda3q0dE5Dn6qOmFVvSveP7WRTE=">Помогите нам с наполнением базы вопросов!</a>'

    if not request.user.is_authenticated:
        p_content += NOT_LOGGED_IN_MESSAGE

    if fitler_type:
        return show_selected_questions(request, questions, h1_content, p_content)
    else:
        return show_selected_questions(
            request, questions, h1_content, p_content,
            requested_sections_slugs=requested_sections_slugs, requested_topic=requested_topic
        )

def problems_by_section(request, slug):

    # Check if there are any get parameters in the request
    params = request.GET
    if params:
        return redirect(reverse('main:problems') + f'?{params.urlencode()}')

    section = Section.objects.get(slug=slug)
    questions = get_questions_by_sections([section])

    h1_content = ''
    p_content = f'Раздел <b>{section.name}</b>'

    if not request.user.is_authenticated:
        p_content += NOT_LOGGED_IN_MESSAGE

    return show_selected_questions(request, questions, h1_content, p_content)

def question_page(request, slug):

    query = request.GET.get('query')
    if query:
        return redirect(reverse('main:problems') + f'?query={query}')

    question = get_question_by_link(slug)
    context = {
        'nav': [False, True, False, False],
        'questions': question
    }
    return render(request, 'question_page.html', context=context)

def about(request):

    requested_query = request.GET.get('query')
    if requested_query:
        return redirect(reverse('main:problems') + f'?query={requested_query}')

    sections = Section.objects.order_by('name')

    context = {
        'nav': [False, False, True, False],
        'sections': sections
        
    }
    return render(request, 'about.html', context=context)

def index(request):

    requested_query = request.GET.get('query')
    if requested_query:
        return redirect(reverse('main:problems') + f'?query={requested_query}')

    sections = Section.objects.order_by('name')
    competitions = Competition.objects.order_by('-id')

    # add cashing of this page, since here we query all the questions
    quesions = Question.objects.filter(listed = True).order_by()
    years = quesions.values_list('year', flat=True).distinct()
    parts = quesions.values_list('part', flat=True).distinct()

    p_content = 'На этом сайте собраны вопросы биологических олимпиад, размеченные по разделам и темам, доступны другие фильтры'
    if not request.user.is_authenticated:
        p_content += NOT_LOGGED_IN_MESSAGE

    context = {
        'nav': [True, False, False, False],
        'sections': sections,
        'competitions': competitions,
        'years': years,
        'parts': parts,
        'p_content': p_content
    }

    return render(request, 'index.html', context=context)

def personal(request):

    context = {
        'nav': [False, False, False, True]
    }

    return render(request, 'personal.html', context=context)

def django_registration_complete(request):
    return redirect(reverse('main:personal'))