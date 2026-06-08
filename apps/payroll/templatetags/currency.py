from django import template

from apps.utils import format_vnd_amount


register = template.Library()


@register.filter
def vnd_amount(value):
    return format_vnd_amount(value)
