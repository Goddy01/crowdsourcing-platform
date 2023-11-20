from accounts.models import Innovator, Moderator, BaseUser
from core.models import Project
from django.utils.safestring import mark_safe
import json


def universal_content(request):
    context = {}

    # context['is_innovator'] = Innovator.objects.filter(user__username=request.user.username).exists()
    try:
        context['to_user_username'] = request.POST.get('to_user')
    except:
        context['to_user'] = ''
    # if not request.user.is_superuser:
    #     context['user'] = BaseUser.objects.get(pk=request.user.pk)
    try:
        Innovator.objects.get(user__pk=request.user.pk)
    except:
        pass
    else:
        context['innovator'] = Innovator.objects.get(user__pk=request.user.pk)
    #     context['innovator'] = ''
    return context