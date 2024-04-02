from django.urls import path, include
from django_registration.backends.one_step.views import RegistrationView
from . import views

app_name = 'main'   


urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('accounts/profile/', views.personal, name='personal'),
    path('problems/', views.problems, name='problems'),
    path('problems/<str:slug>', views.question_page, name='question_page'),
    path('sections/<str:slug>', views.problems_by_section, name='section_url'),
    path('competitions/<str:slug>', views.problems_by_competition, name='competition_url'),
    path('update_server/', views.update, name='update'),
    # auth
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', RegistrationView.as_view(success_url='/accounts/profile/'), name='django_registration_register'),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    # ajax: save and unsave question
    path('save_question/<int:question_id>/', views.save_question, name='save_question'),
    path('unsave_question/<int:question_id>/', views.unsave_question, name='unsave_question'),
    # solve questions page
    path('solve/<str:slug>', views.solve_question, name='solve_question'),
    # ajax: send user answer and question id to server
    path('send_answer/<int:question_id>/', views.send_answer, name='send_answer'),
    # roadmap
    path('roadmap/', views.roadmap, name='roadmap')
]