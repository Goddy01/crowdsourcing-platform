from django.shortcuts import render
from .models import Project
from django_countries import countries
from .forms import CreateProjectForm
from accounts.models import Innovator, Moderator
from datetime import datetime
# Create your views here.
def home(request):
    
    return render(request, 'index.html')

def add_project(request):
    if request.method == 'POST':
        create_project_form = CreateProjectForm(request.POST, request.FILES)
        if create_project_form.is_valid():
            project_obj = create_project_form.save(commit=False)
            project_obj.innovator = Innovator.objects.get(user__username=request.user.username)
            project_obj.date_created = datetime.now()
            if create_project_form.cleaned_data['innovator_user_agreement']:
                project_obj.innovator_user_agreement = True
            project_obj.save()
        else:
            print(create_project_form.errors.as_data())
    else:
        create_project_form = CreateProjectForm()
    return render(request, 'core/add-project.html', {'countries': countries, 'create_project_form': create_project_form})