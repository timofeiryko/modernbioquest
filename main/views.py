from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import Question, Section
from .configs import QUESTIONS_PER_PAGE

import git

# COMMENT TO TEST WEBHOOKS 3

@csrf_exempt
def update(request):
    if request.method == 'POST':
        repo = git.Repo('/home/quest/quest.pythonanywhere.com')
        origin = repo.remotes.origin
        origin.pull()

        return HttpResponse('Updated code on PythonAnywhere')
    else:
        return HttpResponse("Couldn't update the code on PythonAnywhere")

def about(request):
    pass

def problems(request):

    questions = Question.objects.order_by('-id')
    sections = Section.objects.order_by('name')

    paginator = Paginator(questions, QUESTIONS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    is_paginated = page.has_other_pages()
    prev_url = f'?page={page.previous_page_number()}' if page.has_previous() else ''
    next_url = f'?page={page.next_page_number()}' if page.has_next() else ''

    if page.has_previous():
        prev_url = '?page={}'.format(page.previous_page_number())
    else:
        prev_url = ''

    if page.has_next():
        next_url = '?page={}'.format(page.next_page_number())
    else:
        next_url = ''

    context = {
        'nav': [True, False, False],
        'questions': page,
        'is_paginated': is_paginated,
        'next_url': next_url,
        'prev_url': prev_url,
        'sections': sections
    }

    return render(request, 'problems.html', context=context)