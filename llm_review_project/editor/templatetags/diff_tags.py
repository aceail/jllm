from django import template
from django.utils.safestring import mark_safe
import difflib

register = template.Library()

@register.simple_tag
def diff_highlight(new_text, old_text='', color_class='text-red-600'):
    """Return HTML diff highlighting additions with the given color.

    Leading/trailing or internal whitespace differences can occur when
    converting JSON to strings. To avoid false highlights, compare the two
    strings after removing all whitespace characters. If they match, return
    the new text without any highlighting.
    """

    if not old_text:
        return mark_safe(new_text)

    new_compact = ''.join(new_text.split())
    old_compact = ''.join(old_text.split())

    if new_compact == old_compact:
        return mark_safe(new_text)

    diff = difflib.ndiff(old_text.split(), new_text.split())
    pieces = []
    for part in diff:
        code = part[:2]
        text = part[2:]
        if code == '+ ':
            pieces.append(f'<span class="{color_class} diff-added">{text}</span>')
        elif code == '  ':
            pieces.append(text)
        # removed words are skipped

    return mark_safe(' '.join(pieces))
