from django.urls import path, include
from . import views

app_name = 'accounts'
urlpatterns = [
    path('sign-in/', views.innovator_sign_in, name='innovator_sign_in'),
    path('sign-up/', views.innovator_sign_up, name='innovator_sign_up'),
    path('sent/', views.activation_sent_view, name='activation_sent'),
    path('activate-account/<slug:uidb64>/<slug:token>/', views.activate_account, name='activate'),
    path('sign-out/', views.sign_out, name='sign_out'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    # path('generate-link/', views.send_moderator_details, name='send_mod_details'),
    path('account-details-sent/', views.moderation_account_setup_done, name='moderator_account_setup_sent'),
    path('moderator-sign-up/', views.moderator_sign_up, name='moderator_sign_up'),
    path('moderator-sign-in/', views.moderator_sign_in, name='moderator_sign_in'),
    path('profile/', views.profile, name='profile'),
]