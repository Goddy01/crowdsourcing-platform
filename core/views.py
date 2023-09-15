from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Project
from django_countries import countries
from .forms import CreateProjectForm
from accounts.models import Innovator, Moderator
from django.utils import timezone
from django.http import HttpResponse
# Create your views here.
def home(request):
    print('TIME: ', timezone.now())
    return render(request, 'index.html')

def add_project(request):
    project_creation_request = ''
    if request.method == 'POST':
        create_project_form = CreateProjectForm(request.POST or None, request.FILES or None)
        if create_project_form.is_valid():
            project_obj = create_project_form.save(commit=False)
            project_obj.innovator = Innovator.objects.get(user__username=request.user.username)
            # project_obj.date_created = timezone.now()
            if create_project_form.cleaned_data['innovator_user_agreement']:
                project_obj.innovator_user_agreement = True
            project_obj.save()
            print('TIME: ', project_obj.date_created)
            project_creation_request = 'Thank you for submitting your project details. Your project creation request has been sent to a moderator for review. A moderator will carefully assess your project to ensure that the provided information aligns with our user agreement and complies with legal regulations. Please allow some time for our team to review your project thoroughly. We appreciate your patience. If there are any additional details or documents required, a moderator will reach out to you for clarification. We value your commitment to our platform and look forward to the possibility of bringing your project to our community. Once again, thank you for choosing our platform to showcase your project, and we will be in touch with you soon.'

        else:
            print(create_project_form.errors.as_data())
    else:
        create_project_form = CreateProjectForm()
    return render(request, 'core/add-project.html', {'countries': countries, 'create_project_form': create_project_form, 'project_creation_request': project_creation_request})

def pagination(request, items_list, num_of_pages):
    page_number = request.GET.get('page', 1)
    project_paginator = Paginator(items_list.order_by('-pk'), num_of_pages)
    try:
        projects = project_paginator.page(page_number)
    except PageNotAnInteger:
        projects = project_paginator.page(1)
    except EmptyPage:
        projects = project_paginator.page(project_paginator.num_pages)
    return projects

def projects_list(request):
    projects = Project.objects.all()

    return render(request, 'core/projects.html', {'projects': projects})

def filter_projects(request):
    from_expected_return = request.GET.get('from_expected_return')
    to_expected_return = request.GET.get('to_expected_return')

    if from_expected_return:
        print('FROM: ', from_expected_return)
        if to_expected_return:
            print('TO: ', to_expected_return)
            projects = Project.objects.filter(
                Q(expected_return__range=(int(from_expected_return), int(to_expected_return)))
            )
        else:
            projects = Project.objects.filter(
                Q(expected_return__gte=int(from_expected_return))
            )
    else:
        if to_expected_return:
            return HttpResponse('Please provide a min(from) value')
    return render(request, 'core/projects.html', {'projects': projects})
def project_details(request, project_pk):
    project = Project.objects.get(pk=project_pk)
    return render(request, 'core/project_details.html', {'project': project})