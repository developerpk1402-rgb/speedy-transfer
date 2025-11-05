from django import template

register = template.Library()

@register.filter
def to_int(value):
    """
    Converts a string value to an integer.
    Useful for comparing string-based GET parameters with integer IDs.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
