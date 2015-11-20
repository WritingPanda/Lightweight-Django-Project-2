import json
import os

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.template import Template, Context
from django.template.loader_tags import BlockNode
from django.utils._os import safe_join


def get_page_or_404(name):
    """Return page content as a Django template or raise a 404 error"""
    try:
        file_path = safe_join(settings.SITE_PAGES_DIRECTORY, name)
    except ValueError:
        raise Http404('Page Not Found')
    else:
        if not os.path.exists(file_path):
            raise Http404('Page Does Not Exist')
    with open(file_path, 'r') as f:
        page = Template(f.read())
    """
    This code loops through the page's raw nodelist and checks for a BlockNode
    with the name context. BlockNode is a class definition for creating {% block %}
    elements in Django templates. If the context BlockNode is found, it defines a
    metavariable for us that contains the context (57).
    """
    meta = None
    for i, node in enumerate(list(page.nodelist)):
        if isinstance(node, BlockNode) and node.name == 'context':
            meta = page.nodelist.pop(i)
            break
    page._meta = meta
    return page


def page(request, slug='index'):
    """Render the requested page if found."""
    file_name = '{}.html'.format(slug)
    page = get_page_or_404(file_name)
    context = {
        'slug': slug,
        'page': page,
    }
    """
    The metacontext is rendered using Python's json module to convert
    {% block context %} into digestible Python (57).
    """
    if page._meta is not None:
        meta = page._meta.render(Context())
        extra_context = json.loads(meta)
        context.update(extra_context)
    return render(request, 'page.html', context)
