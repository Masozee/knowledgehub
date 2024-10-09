# File: tools/management/commands/reset_db.py

import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings
from decouple import config


class Command(BaseCommand):
    help = 'Resets the PostgreSQL database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input', action='store_true',
            help='Reset the database without asking for confirmation',
        )

    def find_psql(self):
        # Common PostgreSQL installation directories on Windows
        common_dirs = [
            r'C:\Program Files\PostgreSQL',
            r'C:\Program Files (x86)\PostgreSQL',
        ]

        for base_dir in common_dirs:
            if os.path.exists(base_dir):
                versions = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
                versions.sort(reverse=True)
                for version in versions:
                    psql_path = os.path.join(base_dir, version, 'bin', 'psql.exe')
                    if os.path.exists(psql_path):
                        return psql_path
        return None

    def handle(self, *args, **options):
        # Database connection details
        db_name = config('DB_NAME')
        db_user = config('DB_USER')
        db_password = config('DB_PASSWORD')
        db_host = config('DB_HOST', default='localhost')
        db_port = config('DB_PORT', default='5432')

        # Find psql.exe
        psql_path = self.find_psql()
        if not psql_path:
            self.stderr.write(self.style.ERROR('Could not find psql.exe. Please ensure PostgreSQL is installed.'))
            return

        # Confirm action
        if not options['no_input']:
            confirm = input(
                f"You are about to RESET the database '{db_name}'. This will DELETE ALL DATA. Are you sure? (yes/no): ")
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Database reset cancelled.'))
                return

        # SQL commands to reset the database
        sql_commands = f"""
        DROP DATABASE IF EXISTS {db_name};
        CREATE DATABASE {db_name};
        """

        # Execute SQL commands
        try:
            process = subprocess.Popen(
                [psql_path, '-h', db_host, '-p', db_port, '-U', db_user, '-d', 'postgres'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, 'PGPASSWORD': db_password},
                universal_newlines=True
            )
            stdout, stderr = process.communicate(input=sql_commands)

            if process.returncode != 0:
                self.stderr.write(self.style.ERROR(f'An error occurred while resetting the database:'))
                self.stderr.write(self.style.ERROR(stderr))
                return

            self.stdout.write(self.style.SUCCESS(f'Successfully reset database "{db_name}"'))

            # Run migrations
            self.stdout.write(self.style.WARNING('Running migrations...'))
            os.system('python manage.py migrate')

            self.stdout.write(self.style.SUCCESS('Database reset and migrations completed successfully.'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {str(e)}'))