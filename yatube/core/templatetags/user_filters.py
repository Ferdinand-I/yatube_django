from django import template
from django.forms.forms import BoundField


register = template.Library()


@register.filter
def addclass(field: BoundField, css: str) -> str:
    """Do a widget-view of a certain form's field
    with a chosen css.
    """
    return field.as_widget(attrs={'class': css})
