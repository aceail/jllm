from django import template
from django.utils.safestring import mark_safe
import difflib

register = template.Library()


@register.simple_tag
def diff_highlight(new_text, old_text='', color_class='text-red-600'):
    """Return HTML diff highlighting additions with the given color."""
    if not old_text:
        return mark_safe(new_text)

    diff = difflib.ndiff(old_text.split(), new_text.split())
    pieces = []

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

            pieces.append(f'<span class="{color_class} diff-added">{text}</span>')
        elif code == '  ':
            pieces.append(text)
        # removed words are skipped

    return mark_safe(' '.join(pieces))

            pieces.append(f'<span class="{color_class} diff-added">{text}</span>')
        elif code == '- ':
            continue
        else:
            pieces.append(text)

    return mark_safe(' '.join(pieces))

            result.append(f'<span class="diff-added">{text}</span>')
        elif code == '- ':
            continue
        else:
            result.append(text)
    return mark_safe(' '.join(result))

