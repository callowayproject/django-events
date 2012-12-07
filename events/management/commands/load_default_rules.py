from django.core.management.base import NoArgsCommand
from django.core import management
import os


class Command(NoArgsCommand):
    help = "Load some sample data into the db"

    def handle_noargs(self, **options):
        rel_path = '../../fixtures/default_rules.json'
        full_path = os.path.abspath(
                        os.path.join(
                            os.path.dirname(__file__), rel_path))
        management.call_command('loaddata', full_path, **options)