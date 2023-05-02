from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from django.core.cache import cache
from django.core.paginator import Paginator

from django_registration.backends.one_step.views import RegistrationView

from .models import Question, Section, Competition, Profile
from .configs import QUESTIONS_PER_PAGE
from .services import get_question_by_link, get_questions_by_sections, filter_questions_by_query, advanced_filter_service
from .services import check_user_answers

import git
import json

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

@login_required
@require_POST
def save_question(request, question_id):

    question = get_object_or_404(Question, id=question_id)

    profile = request.user.profile
    question.saved_by.add(profile)

    return JsonResponse({'success': True})

@login_required
@require_POST
def unsave_question(request, question_id):

    question = get_object_or_404(Question, id=question_id)

    profile = request.user.profile
    question.saved_by.remove(profile)

    return JsonResponse({'success': True})

def show_selected_questions(request, questions, h1_content: str, p_content: str, **kwargs):

    # get dict of get params without page
    get_params = request.GET.copy()
    if 'page' in get_params:
        get_params.pop('page')

    paginator = Paginator(questions.distinct(), QUESTIONS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    is_paginated = page.has_other_pages()
    prev_url = f'?page={page.previous_page_number()}' if page.has_previous() else ''
    next_url = f'?page={page.next_page_number()}' if page.has_next() else ''
    last_url = f'?page={page.paginator.num_pages}' if page.has_next() else ''

    # generate dict of urls with page numbers using page.paginator.page_range and add get params to them
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
    competitions = Competition.objects.order_by('name')

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
        'competitions': competitions,
        'page_urls': page_urls
    }

    # add kwargs to context
    context.update(kwargs)

    return context

def advanced_filter(questions, request, requested_sections):
    # TODO: TO SERVICES?

    requested_topics = request.GET.getlist('topic')

    requested_competitions = request.GET.getlist('competition')
    requested_stages = request.GET.getlist('stage')

    requested_years = request.GET.getlist('year')
    requested_parts = request.GET.getlist('part')
    requested_grades = request.GET.getlist('grade')

    questions, p_content = advanced_filter_service(
        questions,
        requested_topics,
        requested_sections,
        requested_competitions,
        requested_stages,
        requested_years,
        requested_parts,
        requested_grades
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

    # check if there is no get params
    if not request.GET and not request.user.is_authenticated:
        # check if page is in cache
        if cache.has_key('problems'):
            return cache.get('problems')

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


    if fitler_type:
        context =  show_selected_questions(request, questions, h1_content, p_content)
    else:
        context = show_selected_questions(
            request, questions, h1_content, p_content,
            requested_sections_slugs=requested_sections_slugs, requested_topic=requested_topic
        )

    response = render(request, 'problems.html', context=context)

    if not request.GET and not request.user.is_authenticated:
        cache.set('problems', response, 60 * 10)
    
    return response

    

def problems_by_section(request, slug):

    # Check if there are any get parameters in the request except page
    params = request.GET.copy()
    params.pop('page', None)
    if params:
        return redirect(reverse('main:problems') + f'?{params.urlencode()}')

    section = Section.objects.get(slug=slug)
    questions = get_questions_by_sections([section])

    h1_content = ''
    p_content = f'Раздел <b>{section.name}</b>'

    context = show_selected_questions(request, questions, h1_content, p_content)

    return render(request, 'problems.html', context=context)

# TODO: DRY
def problems_by_competition(request, slug):

    # Check if there are any get parameters in the request except page
    params = request.GET.copy()
    params.pop('page', None)
    if params:
        return redirect(reverse('main:problems') + f'?{params.urlencode()}')

    competition = Competition.objects.get(slug=slug)
    questions = Question.objects.order_by('-id').filter(competition=competition, listed=True)

    h1_content = ''
    p_content = f'Вопросы <b>{competition.name}</b>'

    context = show_selected_questions(request, questions, h1_content, p_content)

    return render(request, 'problems.html', context=context)

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

@cache_page(60 * 10)
def index(request):

    requested_query = request.GET.get('query')
    if requested_query:
        return redirect(reverse('main:problems') + f'?query={requested_query}')

    sections = Section.objects.order_by('name')
    competitions = Competition.objects.order_by('-id')

    quesions = Question.objects.filter(listed = True).order_by()
    years = quesions.values_list('year', flat=True).distinct().order_by('-year')
    parts = quesions.values_list('part', flat=True).distinct().order_by('part')
    grades = ['9', '10', '11']

    p_content = 'На этом сайте собраны вопросы биологических олимпиад, размеченные по разделам и темам, доступны другие фильтры'

    context = {
        'nav': [True, False, False, False],
        'sections': sections,
        'competitions': competitions,
        'years': years,
        'parts': parts,
        'p_content': p_content,
        'grades': grades
    }

    return render(request, 'index.html', context=context)

@login_required
def personal(request):

    if not hasattr(request.user, 'profile'):
        profile = Profile.objects.create(user=request.user)
        profile.save()
    
    saved_questions = request.user.profile.saved_questions.all().order_by('-basequestionsave__updated_at')

    requested_query = request.GET.get('query')
    if requested_query:
        saved_questions = filter_questions_by_query(requested_query, saved_questions)

    context = show_selected_questions(
        request, saved_questions,
        'Ваши сохранённые вопросы',
        'Вы можете добавить вопросы в избранное, нажав на кнопку в правом верхнем углу вопроса'
    )
    # TODO h and p content out of show_selected_questions (and probably nav)???

    context['nav'] = [False, False, False, True]

    return render(request, 'personal.html', context=context)

def django_registration_complete(request):
    return redirect(reverse('main:personal'))

def _answer_result(request, is_right):
    user_message = 'Верно!' if is_right else 'Неверно'
    return HttpResponse(user_message)

@login_required
@require_POST
def send_answer(request, question_id):

    # Retrieve the question from the database
    question = get_object_or_404(Question, id=question_id)

    user_answer = json.loads(request.body.decode('utf-8'))['user_answer']

    # Check if the user has already answered this question
    user_answers, solved_question = check_user_answers(question, request.user, [user_answer])

    response_data = {
        'user_score': solved_question.user_score,
        'success': True,
    }

    return JsonResponse(response_data)


def solve_question(request, slug):

    question = get_question_by_link(slug)
    context = {
        'nav': [False, False, False, True],
        'questions': question
    }
    return render(request, 'solve_question.html', context=context)