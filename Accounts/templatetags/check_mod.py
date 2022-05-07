from django import template

from Moderator.models import Mode #this import is fine but pychrame shows error


register = template.Library()


@register.filter('check_mod')
def has_group(user):
    try :
      team_mode=  Mode.objects.get(email=user)
    except Exception:
      team_mode =None

    if team_mode is not None and team_mode.mode_active:
        return True
    else :
        return False
    #groups = user.groups.all().values_list('name', flat=True)
    #return True if group_name in groups else False

register.filter('check_mod',has_group)


