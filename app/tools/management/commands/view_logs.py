from django.core.management.base import BaseCommand
from core.logging import get_logs

class Command(BaseCommand):
    help = 'View recent logs'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10, help='Number of logs to display')
        parser.add_argument('--level', type=str, help='Filter by log level')

    def handle(self, *args, **options):
        limit = options['limit']
        level = options['level']
        logs = get_logs(limit, level)
        for log in logs:
            self.stdout.write(f"{log[3]} - {log[1]}: {log[2]}")