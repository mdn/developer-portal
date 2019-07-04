from django.contrib.auth.models import Group

def user_as_editor(user=None, *args, **kwargs):
    user.groups.add(Group.objects.get(pk=1))
    user.save()

