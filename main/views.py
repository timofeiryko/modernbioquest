from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import Question, Section
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

def about(request):
    pass

def show_selected_questions(request, questions, h1_content: str, p_content: str, **kwargs):

    paginator = Paginator(questions, QUESTIONS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    is_paginated = page.has_other_pages()
    prev_url = f'?page={page.previous_page_number()}' if page.has_previous() else ''
    next_url = f'?page={page.next_page_number()}' if page.has_next() else ''

    if page.has_previous():
        prev_url = f'?page={page.previous_page_number()}'
    else:
        prev_url = ''

    if page.has_next():
        next_url = f'?page={page.next_page_number()}'
    else:
        next_url = ''

    sections = Section.objects.order_by('name')

    context = {
        'nav': [True, False, False],
        'questions': page,
        'is_paginated': is_paginated,
        'next_url': next_url,
        'prev_url': prev_url,
        'h1_content': h1_content,
        'p_content': p_content,
        'sections': sections
    }

    # add kwargs to context
    context.update(kwargs)

    return render(request, 'problems.html', context=context)

def problems(request):

    # extract multipe sections from the get request
    requested_sections = request.GET.getlist('section')

    # extract topic from the get request
    requested_topic = request.GET.get('topic')

    # extract search query from the get request
    requested_query = request.GET.get('query')

    if requested_sections:

        sections = Section.objects.filter(slug__in=requested_sections)
        questions = get_questions_by_sections(sections)

        h1_content = ''
        if questions:
            p_content = f'Вопросы по разделам: <b>{", ".join([section.name for section in sections])}</b>'
        else:
            p_content = f'По запрошенным разделам <b>{", ".join([section.name for section in sections])}</b> вопросов не найдено :( Помогите нам с наполнением базы вопросов: <a href="mailto:timofei.ryko@gmail.com">timofei.ryko@gmail.com</a>'

    elif requested_topic:
            
            questions = Question.objects.order_by('-id').filter(listed = True, topics__name__icontains=requested_topic)
    
            h1_content = ''
            if questions:
                p_content = f'Вопросы по теме: <b>{requested_topic}</b>'
            else:
                p_content = f'По запрошенной теме <b>{requested_topic}</b> вопросов не найдено :( Помогите нам с наполнением базы вопросов: <a href="mailto:timofei.ryko@gmail.com">timofei.ryko@gmail.com</a>'

    else:

        questions = Question.objects.order_by('-id').filter(listed = True)

        h1_content = 'Коллекция вопросов с ответами'
        p_content = 'Вы можете выбрать вопросы по разделам или темам в меню справа (с мобильного устройства — снизу)'

    if requested_query:

        questions = filter_questions_by_query(requested_query, questions)

        h1_content = ''
        if questions:
            p_content = f'Вопросы по запросу: <b>{requested_query}</b>'
        else:
            p_content = f'По запросу <b>{requested_query}</b> ничего не найдено :( Помогите нам с наполнением базы вопросов: <a href="mailto:timofei.ryko@gmail.com">timofei.ryko@gmail.com</a>'

    return show_selected_questions(
        request, questions, h1_content, p_content,
        requested_sections=requested_sections, requested_topic=requested_topic
    )

def problems_by_section(request, slug):

    section = Section.objects.get(slug=slug)
    questions = get_questions_by_sections([section])

    h1_content = ''
    p_content = f'Вопросы по разделу <b>{section.name}</b>'

    return show_selected_questions(request, questions, h1_content, p_content)

def question_page(request, slug):
    question = get_question_by_link(slug)
    context = {
        'nav': [True, False, False],
        'questions': question
    }
    return render(request, 'question_page.html', context=context)