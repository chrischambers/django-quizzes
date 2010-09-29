from django import template
register = template.Library()

@register.filter(name='percentage')
def percentage(part, population):
    try:
        return (float(part) / float(population)) * 100
    except (ValueError, ZeroDivisionError):
        return ''

