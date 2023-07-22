from django.urls import path, include
from . import views

app_name = 'accounts'
urlpatterns = [
    path('sign-in/', views.contributor_sign_in, name='contributor_sign_in'),
    path('sign-up/', views.contributor_sign_up, name='contributor_sign_up'),
    path('sent/', views.activation_sent_view, name='activation_sent'),
    path('activate-account/<slug:uidb64>/<slug:token>/', views.activate_account, name='activate'),
    path('sign-out/', views.sign_out, name='sign_out'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('generate-link/<slug:uidb64>/<slug:token>/', views.generate_moderator_sign_up_link, name='gen_mod_sign_up_link'),
]