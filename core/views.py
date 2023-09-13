from django.shortcuts import render
from .models import Project
from django_countries import countries
from .forms import CreateProjectForm
# Create your views here.
def home(request):
    
    return render(request, 'index.html')

def add_project(request):
    if request.method == 'POST':
        create_project_form = CreateProjectForm(request.POST, request.FILES)
        # if create_project_form.is_valid():

    return render(request, 'core/add-project.html', {'countries': countries})