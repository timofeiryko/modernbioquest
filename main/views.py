from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Question, Section

import git

@csrf_exempt
def update(request):
    if request.method == 'POST':
        repo = git.Repo('/home/newbioquest/newbioquest.pythonanywhere.com')
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

    context = {
        'nav': [True, False, False],
        'questions': questions,
        'sections': sections
    }

    return render(request, 'problems.html', context=context)