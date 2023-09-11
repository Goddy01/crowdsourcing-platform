from django.shortcuts import render

# Create your views here.
def home(request):
    
    return render(request, 'index.html')

def add_project(request):
    
    return render(request, 'core/add-project.html')