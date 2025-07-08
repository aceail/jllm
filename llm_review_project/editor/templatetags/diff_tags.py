from django import template
from django.utils.safestring import mark_safe
import difflib

register = template.Library()

@register.filter
def diff_highlight(new_text, old_text):
    """Return HTML diff showing additions in <span> tags."""
    if not old_text:
        return new_text
    diff = difflib.ndiff(old_text.split(), new_text.split())
    result = []
    for part in diff:
        code = part[:2]
        text = part[2:]
        if code == '+ ':
            result.append(f'<span class="diff-added">{text}</span>')
        elif code == '- ':
            continue
        else:
            result.append(text)
    return mark_safe(' '.join(result))
