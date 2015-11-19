import os
import shutil

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from django.test.client import Client


def get_pages():
    for name in os.listdir(settings.SITE_PAGES_DIRECTORY):
        if name.endswith('.html'):
            yield name[:-5]


class Command(BaseCommand):
    help = 'Build static site output.'
    leave_locale_alone = True

    def handle(self, *args, **options):
        """Request pages and build output"""
        # Checks whether the output directory exists
        # If so, remove it to create a clean version
        if os.path.exists(settings.SITE_OUTPUT_DIRECTORY):
            shutil.rmtree(settings.SITE_OUTPUT_DIRECTORY)
        os.mkdir(settings.SITE_OUTPUT_DIRECTORY)
        os.makedirs(settings.STATIC_ROOT, exist_ok=True)
        # Run collectstatic to copy all static resources
        # into the STATIC_ROOT, which is configured to be
        # inside the SITE_OUTPUT_DIRECTORY
        call_command('collectstatic', interactive=False, clear=True, verbosity=0)
        client = Client()
        for page in get_pages():
            url = reverse('page', kwargs={'slug': page})
            response = client.get(url)
            if page == 'index':
                output_dir = settings.SITE_OUTPUT_DIRECTORY
            else:
                output_dir = os.path.join(settings.SITE_OUTPUT_DIRECTORY, page)
                os.makedirs(output_dir)
            # Templates are rendered as static content
            # Using the Django test client to mimic crawling
            # the site pages and writing the rendered content
            # into the SITE_OUTPUT_DIRECTORY
            with open(os.path.join(output_dir, 'index.html'), 'wb') as f:
                f.write(response.content)
