from django import template


register = template.Library()


@register.filter('splitId')
def has_group(ytid):
    try :
        id= ytid.split('watch?v=')[1]
        if len(id)==11:
            return id
        else :
            return -999
    except :
        return None



register.filter('splitId',has_group)


