"""crowdsourcing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', 'accounts')), # For social-auth
    path('chat/', include('chat.urls', 'chat')), # For social-auth
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('', views.home, name='home'),
    path('add-project', views.add_project, name='add_project'),
    path('projects/', views.projects_list, name='projects'),
    path('project-details/<project_pk>', views.project_details, name='project_details'),
    path('add-innovation/', views.add_innovation, name='add_innovation'),
    path('innovations/', views.innovations_list, name='innovations_list'),
    path('innovation-detail/<int:pk>/', views.innovation_detail, name='innovation_details'),
    path('upvote/<int:contribution_pk>/', views.upvote_contribution, name='upvote_contribution'),
    path('downvote/<int:contribution_pk>/', views.downvote_contribution, name='downvote_contribution'),
    path('accept_contribution/<int:contribution_pk>/', views.accept_contribution, name='accept_contribution'),
    path('unaccept_contribution/<int:contribution_pk>/', views.unaccept_contribution, name='unaccept_contribution'),
    path('invest/<investment_pk>/', views.invest, name='invest'),
    path('my-investments/', views.my_investments, name="my-investments"),
    path('deposit/', views.deposit_money, name='deposit'),
    path('get-bank-details/', views.get_bank_details, name='get_bank_details'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('send-money/', views.send_money, name='send_money'),
    path('account-statement/', views.statement, name='statement'),
    path('investment-capital/', views.investment_capital, name='investment_capital'),
    path('withdraw-project-funds/<project_pk>/', views.withdraw_project_funds, name='withdraw_project_funds'),
    path('withdraw-project-funds-page/', views.withdraw_project_funds_page, name='withdraw_project_funds_page'),
    path('withdrawal-requests/', views.withdrawal_requests, name='withdrawal_requests'),
    path('withdrawal-requests/set-withdrawal-request-status/<type>/<pk>', views.set_withdrawal_request_status, name='set_withdrawal_request_status'),
    path('<type>/<pk>/send-withdrawal-request-confirmation-email', views.send_withdrawal_request_confirmation_email, name='send_withdrawal_request_confirmation_email'),
    path('confirm-withdrawal-request/<type>/<withdrawal_pk>/<response>', views.confirm_withdrawal_request, name='confirm_withdrawal_request'),
    path('send-kbq/<type>/<withdrawal_pk>', views.send_kbq, name='send_kbq'),
    path('kbq-confirmation/<type>/<withdrawal_pk>', views.kbq_confirmation, name='kbq_confirmation'),
    path('approve-withdrawal-request/<type>/<withdrawal_pk>', views.approve_withdrawal_request, name='approve_withdrawal_request'),
    path('reject-withdrawal-request/<type>/<withdrawal_pk>', views.reject_withdrawal_request, name='reject_withdrawal_request'),
    path('approve-money-transer/<send_money_pk>/<sender>/<recipient>/<amount_to_send>', views.approve_send_money_request, name='approve_send_money'),
    path('reject-money-transer/<send_money_pk>/<recipient>/<amount_to_send>', views.reject_send_money_request, name='reject_send_money'),
    path('contact-us', views.contact_us, name='contact_us'),
    
    # path('contribution/reply/<innovation_pk>/', views.reply, name='reply'),


    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name="password/password_change_done.html"), name="password_change_done"),

    # path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password/password_change.html'), name='password_change'),

    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="password/password_reset_done.html"), name="password_reset_done"),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'), name="password_reset_complete"),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password/password_reset_form.html', 
        success_url = reverse_lazy('password_reset_complete'),
    ), name="password_reset_confirm"),    

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password/password_reset.html',
        email_template_name='password/password_reset_email.html',
        subject_template_name='password/password_reset_subject.txt',
        success_url = reverse_lazy('password_reset_done'),
    ), name='password_reset'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)