from django.urls import path, include
from . import views

app_name = 'accounts'
urlpatterns = [
    path('innovator/login', views.innovator_login, name='innovator_login'),
    path('innovator/sign-up', views.innovator_sign_up, name='innovator_sign_up'),
    path('sent', views.activation_sent_view, name='activation_sent'),
    path('activate-account/<slug:uidb64>/<slug:token>', views.activate_account, name='activate'),
    path('sign-out', views.sign_out, name='sign_out'),
    path('social-auth', include('social_django.urls', namespace='social')),
    # path('generate-link/', views.send_moderator_details, name='send_mod_details'),
    path('account-details-sent', views.moderation_account_setup_done, name='moderator_account_setup_sent'),
    path('moderator/sign-up', views.moderator_sign_up, name='moderator_sign_up'),
    path('moderator/login', views.moderator_login, name='moderator_login'),
    path('profile/innovator', views.profile, name='profile'),
    path('profile/moderator', views.mod_profile, name='mod_profile'),
    path('profile/<user_pk>', views.others_profile, name='profile_with_arg'),
    path('innovator/edit-profile', views.edit_profile, name='edit_profile'),
    path('moderator/edit-profile', views.moderator_edit_profile, name='mod_edit_profile'),
    path('resend-email-activation-link', views.resend_email_activation, name='resend_email_activation'),
    path('profile/delete-pfp', views.remove_pfp, name='remove_pfp'),
    path('remove-skill/<skill_id>', views.remove_skill, name='remove_skill'),
    path('remove-service/<pk>', views.remove_service, name='remove_service'),
    # path('password-change', views.change_password, name='change_password'),
]