from accounts.models import Innovator, Moderator, BaseUser
from core.models import Project


def universal_content(request):
    context = {}
    context['is_innovator'] = Innovator.objects.filter(user__username=request.user.username).exists()
    return context