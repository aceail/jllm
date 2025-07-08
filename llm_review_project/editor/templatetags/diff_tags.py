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


def _update_color_map(old, new, color, colors, path=""):
    if isinstance(new, dict):
        for k, v in new.items():
            sub_old = old.get(k, {}) if isinstance(old, dict) else {}
            sub_path = f"{path}.{k}" if path else k
            _update_color_map(sub_old, v, color, colors, sub_path)
    elif isinstance(new, list):
        for i, val in enumerate(new):
            sub_old = old[i] if isinstance(old, list) and i < len(old) else {}
            sub_path = f"{path}[{i}]"
            _update_color_map(sub_old, val, color, colors, sub_path)
    else:
        old_val = old if not isinstance(old, (dict, list)) else None
        if new != old_val:
            colors[path] = color


def _render_json(obj, colors, path="", indent=0):
    space = " " * indent
    if isinstance(obj, dict):
        lines = ["{"]
        keys = list(obj.keys())
        for idx, key in enumerate(keys):
            val = obj[key]
            sub_path = f"{path}.{key}" if path else key
            rendered = _render_json(val, colors, sub_path, indent + 2)
            comma = "," if idx < len(keys) - 1 else ""
            lines.append(f"{space}  \"{escape(key)}\": {rendered}{comma}")
        lines.append(f"{space}}}")
        return "\n".join(lines)
    elif isinstance(obj, list):
        lines = ["["]
        for idx, item in enumerate(obj):
            sub_path = f"{path}[{idx}]"
            rendered = _render_json(item, colors, sub_path, indent + 2)
            comma = "," if idx < len(obj) - 1 else ""
            lines.append(f"{space}  {rendered}{comma}")
        lines.append(f"{space}]")
        return "\n".join(lines)
    else:
        color = colors.get(path)
        value = json.dumps(obj, ensure_ascii=False)
        if color:
            return f'<span class="{color} diff-added">{escape(value)}</span>'
        return escape(value)


@register.simple_tag
def json_history_diff(result):
    """Render the parsed_result with values highlighted by the user who last changed each field."""
    if not result.parsed_result:
        return mark_safe(result.edited_text)

    histories = result.history.all()
    colors = {}
    prev_data = {}
    for hist in histories:
        color = get_user_color(hist.editor.username) if hist.editor else ""
        data = hist.edited_data or {}
        _update_color_map(prev_data, data, color, colors)
        prev_data = data

    html = _render_json(result.parsed_result, colors)
    return mark_safe(html)

