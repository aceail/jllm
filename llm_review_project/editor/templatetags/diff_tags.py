from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
import difflib
import json


register = template.Library()

@register.simple_tag
def diff_highlight(new_text, old_text='', color_class='text-red-600'):
    """Return HTML diff highlighting additions with the given color.

    Leading/trailing or internal whitespace differences can occur when
    converting JSON to strings. To avoid false highlights, compare the two
    strings after removing all whitespace characters. If they match, return
    the new text without any highlighting.

    if not old_text:

    If the texts are equal after stripping whitespace, return the new text
    without highlighting.
    """
    if not old_text or new_text.strip() == old_text.strip():

        return mark_safe(new_text)

    # Try JSON normalization first to avoid false positives caused by
    # formatting differences or key ordering.
    try:
        new_obj = json.loads(new_text)
        old_obj = json.loads(old_text)
        new_normalized = json.dumps(new_obj, ensure_ascii=False, sort_keys=True)
        old_normalized = json.dumps(old_obj, ensure_ascii=False, sort_keys=True)
    except Exception:
        new_normalized = ''.join(new_text.split())
        old_normalized = ''.join(old_text.split())

    if new_normalized == old_normalized:
        return mark_safe(new_text)

    # Try JSON normalization first to avoid false positives caused by
    # formatting differences or key ordering.
    try:
        new_obj = json.loads(new_text)
        old_obj = json.loads(old_text)
        new_normalized = json.dumps(new_obj, ensure_ascii=False, sort_keys=True)
        old_normalized = json.dumps(old_obj, ensure_ascii=False, sort_keys=True)
    except Exception:
        new_normalized = ''.join(new_text.split())
        old_normalized = ''.join(old_text.split())

    if new_normalized == old_normalized:
        return mark_safe(new_text)

    # Try JSON normalization first to avoid false positives caused by
    # formatting differences or key ordering.
    try:
        new_obj = json.loads(new_text)
        old_obj = json.loads(old_text)
        new_normalized = json.dumps(new_obj, ensure_ascii=False, sort_keys=True)
        old_normalized = json.dumps(old_obj, ensure_ascii=False, sort_keys=True)
    except Exception:
        new_normalized = ''.join(new_text.split())
        old_normalized = ''.join(old_text.split())

    if new_normalized == old_normalized:
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


@register.filter
def json_equal(new_text, old_text=''):
    """Return True if two strings are equivalent JSON or whitespace-normalized."""
    if not old_text:
        return False

    try:
        new_obj = json.loads(new_text)
        old_obj = json.loads(old_text)
        new_normalized = json.dumps(new_obj, ensure_ascii=False, sort_keys=True)
        old_normalized = json.dumps(old_obj, ensure_ascii=False, sort_keys=True)
    except Exception:
        new_normalized = ''.join(new_text.split())
        old_normalized = ''.join(old_text.split())

    return new_normalized == old_normalized

