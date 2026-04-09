from copy import deepcopy

import markdown
import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_MD_ATTRIBUTES = deepcopy(nh3.ALLOWED_ATTRIBUTES)
for _tag in ("div", "span", "code", "pre", "table", "thead", "tbody", "tr", "th", "td"):
    if _tag not in _MD_ATTRIBUTES:
        _MD_ATTRIBUTES[_tag] = set()
    _MD_ATTRIBUTES[_tag].add("class")

_MD_EXTENSIONS = ["codehilite", "fenced_code", "tables", "nl2br"]


@register.filter(is_safe=True)
def render_markdown(value):
    """Convert markdown text to sanitized HTML.

    Preserves Pygments class attributes for codehilite syntax highlighting.
    Strips scripts, iframes, forms, and event handlers via nh3.
    """
    if not value:
        return ""
    html = markdown.markdown(str(value), extensions=_MD_EXTENSIONS)
    return mark_safe(nh3.clean(html, attributes=_MD_ATTRIBUTES))
