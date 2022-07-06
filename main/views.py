from django.shortcuts import render

from .models import Question, Section

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