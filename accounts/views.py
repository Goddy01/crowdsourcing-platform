from django.shortcuts import render

# Create your views here.
def sign_in(request):
    
    return render(request, 'accounts/sign_in.html')

def sign_up(request):

    return render(request, 'accounts/sign_up.html')