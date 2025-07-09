from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
import difflib
import json
USER_COLORS = [
    "text-red-600",
    "text-blue-600",
    "text-green-600",
    "text-purple-600",
    "text-orange-600",
]

from ..utils import get_user_color


register = template.Library()

@register.simple_tag
def diff_highlight(new_text, old_text='', color_class='text-red-600'):
    """Return HTML diff highlighting additions with the given color.

    The input strings are compared after normalizing JSON formatting. If the
    normalized texts are identical, the original ``new_text`` is returned
    without any highlighting.
    """
    if not old_text:
        return mark_safe(new_text)

    if new_text.strip() == old_text.strip():
        return mark_safe(new_text)

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
        text = escape(part[2:])
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


def _init_tokens_map(data, tokens, path=""):
    """Initialize token map with uncolored words from the first history entry."""
    if isinstance(data, dict):
        for k, v in data.items():
            sub_path = f"{path}.{k}" if path else k
            _init_tokens_map(v, tokens, sub_path)
    elif isinstance(data, list):
        for i, val in enumerate(data):
            sub_path = f"{path}[{i}]"
            _init_tokens_map(val, tokens, sub_path)
    else:
        tokens[path] = [(w, None) for w in str(data).split()]


def _apply_word_diff(old_tokens, new_words, color):
    """Return new tokens after applying a word-level diff."""
    old_words = [w for w, _ in old_tokens]
    diff = difflib.ndiff(old_words, new_words)
    result = []
    idx = 0
    for part in diff:
        code = part[:2]
        word = part[2:]
        if code == "  ":
            result.append(old_tokens[idx])
            idx += 1
        elif code == "- ":
            idx += 1
        elif code == "+ ":
            result.append((word, color))
    return result


def _apply_diff_map(old, new, color, tokens, path=""):
    if isinstance(new, dict):
        for k, v in new.items():
            sub_old = old.get(k, {}) if isinstance(old, dict) else {}
            sub_path = f"{path}.{k}" if path else k
            _apply_diff_map(sub_old, v, color, tokens, sub_path)
    elif isinstance(new, list):
        for i, val in enumerate(new):
            sub_old = old[i] if isinstance(old, list) and i < len(old) else {}
            sub_path = f"{path}[{i}]"
            _apply_diff_map(sub_old, val, color, tokens, sub_path)
    else:
        old_val = old if not isinstance(old, (dict, list)) else None
        if path not in tokens:
            tokens[path] = [(w, None) for w in str(old_val if old_val is not None else "").split()]
        if new != old_val:
            tokens[path] = _apply_word_diff(tokens[path], str(new).split(), color)


def _render_json(obj, tokens, path="", indent=0):
    space = " " * indent
    if isinstance(obj, dict):
        lines = ["{"]
        keys = list(obj.keys())
        for idx, key in enumerate(keys):
            val = obj[key]
            sub_path = f"{path}.{key}" if path else key
            rendered = _render_json(val, tokens, sub_path, indent + 2)
            comma = "," if idx < len(keys) - 1 else ""
            lines.append(f"{space}  \"{escape(key)}\": {rendered}{comma}")
        lines.append(f"{space}}}")
        return "\n".join(lines)
    elif isinstance(obj, list):
        lines = ["["]
        for idx, item in enumerate(obj):
            sub_path = f"{path}[{idx}]"
            rendered = _render_json(item, tokens, sub_path, indent + 2)
            comma = "," if idx < len(obj) - 1 else ""
            lines.append(f"{space}  {rendered}{comma}")
        lines.append(f"{space}]")
        return "\n".join(lines)
    else:
        token_list = tokens.get(path)
        if token_list is None:
            value = json.dumps(obj, ensure_ascii=False)
            return escape(value)
        pieces = []
        for word, color in token_list:
            if color:
                pieces.append(f'<span class="{color} diff-added">{escape(word)}</span>')
            else:
                pieces.append(escape(word))
        value_html = " ".join(pieces)
        if isinstance(obj, str):
            return f'"{value_html}"'
        return value_html


@register.simple_tag
def json_history_diff(result):
    """Render ``parsed_result`` with word-level highlights for each editor."""
    if not result.parsed_result:
        return mark_safe(result.edited_text)

    histories = list(result.history.all())
    if not histories:
        return mark_safe(result.edited_text)

    tokens = {}
    first_data = histories[0].edited_data or {}
    _init_tokens_map(first_data, tokens)
    prev_data = first_data

    for hist in histories[1:]:
        color = get_user_color(hist.editor.username) if hist.editor else ""
        data = hist.edited_data or {}
        _apply_diff_map(prev_data, data, color, tokens)
        prev_data = data

    html = _render_json(result.parsed_result, tokens)
    return mark_safe(html)

