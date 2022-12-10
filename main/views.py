from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import Question, Section, Competition, NewStage, Topic
from .configs import QUESTIONS_PER_PAGE
from .services import get_question_by_link, get_questions_by_sections, filter_questions_by_query

import git

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

    print('ADVANCED FILTER')

    p_content = ''

    if requested_sections is not None:

        requested_topics = request.GET.getlist('topic')
        if requested_topics:
            sections_without_topics = requested_sections.exclude(topics__name__in=requested_topics)
            sections_with_topics = requested_sections.filter(topics__name__in=requested_topics).distinct()
        else:
            sections_without_topics = requested_sections
            sections_with_topics = Section.objects.none()

        if sections_without_topics:
            p_content += f'Разделы целиком: <b>{", ".join([section.name for section in sections_without_topics])}</b><br>'
            questions_without_topics = questions.filter(sections__in=sections_without_topics)

        if requested_topics:

            questions  = questions.filter(topics__name__in=requested_topics)
            topics = Topic.objects.filter(name__in=requested_topics)

            # divide questions and topics into batches by section
            questions = [Question.objects.filter(sections__in=[section]) for section in sections_with_topics]
            topics = [topics.filter(parent_section=section) for section in sections_with_topics]
            new_questions = []

            for section, topic_batch, question_batch in zip(sections_with_topics, topics, questions):
                new_questions.append(question_batch.filter(topics__in=topic_batch))
                p_content += f'<b>{section.name}</b>: {", ".join([topic.name for topic in topic_batch])}<br>'

            # merge batches into one queryset
            questions = Question.objects.none()
            for question_batch in new_questions:
                questions = questions | question_batch

            if sections_without_topics:
                questions = questions | questions_without_topics

        
    # TODO abstraction for similar filtering (competition + stage, section + topic)
    requested_competitions = request.GET.getlist('competition')
    if requested_competitions:
        requested_competitions = Competition.objects.filter(slug__in=requested_competitions)

        requested_stages = request.GET.getlist('stage')
        if requested_stages:
            competitions_without_stages = requested_competitions.exclude(stages__slug__in=requested_stages)
            competitions_with_stages = requested_competitions.filter(stages__slug__in=requested_stages).distinct()
        else:
            competitions_without_stages = requested_competitions
            competitions_with_stages = Competition.objects.none()

        if competitions_without_stages:
            p_content += f'Олимпиады: <b>{", ".join([competition.name for competition in competitions_without_stages])}</b><br>'
            questions_without_stages = questions.filter(competition__slug__in=competitions_without_stages)
        
        if requested_stages:

            questions = questions.filter(new_stage__slug__in=requested_stages)
            stages = NewStage.objects.filter(slug__in=requested_stages)

            # divide questions and stages into batches by competition
            questions = [Question.objects.filter(competition=competition) for competition in competitions_with_stages]
            stages = [stages.filter(competition=competition) for competition in competitions_with_stages]
            new_questions = []

            for competition, stage_batch, question_batch in zip(competitions_with_stages, stages, questions):
                new_questions.append(question_batch.filter(new_stage__in=stage_batch))
                p_content += f'<b>{competition.name}</b>: {", ".join([stage.name for stage in stage_batch])}<br>'

            # merge batches into one queryset
            questions = Question.objects.none()
            for question_batch in new_questions:
                questions = questions | question_batch
            
            if competitions_without_stages:
                questions = questions | questions_without_stages

    requested_years = request.GET.getlist('year')
    if requested_years:
        questions = questions.filter(year__in=requested_years)

        p_content += f'Годы проведения: <b>{", ".join(requested_years)}</b><br>'
    
    requested_parts = request.GET.getlist('part')
    if requested_parts:
        questions = questions.filter(part__in=requested_parts)

        p_content += f'Части: <b>{", ".join(requested_parts)}</b><br>'

    if not questions:
        h1_content = ''
        p_content = 'Ничего не найдено :( <a href="https://vk.me/join/p/R7YSQ1Hda3q0dE5Dn6qOmFVvSveP7WRTE=">Помогите нам с наполнением базы вопросов!</a>'
    else:
        h1_content = 'Ваш персональный набор вопросов'
        p_content += 'Кроме фильтров, на сайте есть поиск!'

    # TODO; automatically add new fields to this filter

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
        questions = Question.objects.order_by('-id').filter(listed = True)

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
        return show_selected_questions(request, questions, h1_content, p_content)
    else:
        return show_selected_questions(
            request, questions, h1_content, p_content,
            requested_sections_slugs=requested_sections_slugs, requested_topic=requested_topic
        )

def problems_by_section(request, slug):

    section = Section.objects.get(slug=slug)
    questions = get_questions_by_sections([section])

    h1_content = ''
    p_content = f'Раздел <b>{section.name}</b>'

    return show_selected_questions(request, questions, h1_content, p_content)

def question_page(request, slug):
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

    context = {
        'nav': [True, False, False, False],
        'sections': sections,
        'competitions': competitions,
        'years': years,
        'parts': parts
        
    }
    return render(request, 'index.html', context=context)

def personal(request):

    context = {
        'nav': [False, False, False, True]
    }

    return render(request, 'personal.html', context=context)