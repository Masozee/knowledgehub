# File: tools/management/commands/restore_db.py

import os
import subprocess
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from decouple import config


class Command(BaseCommand):
    help = 'Restores the PostgreSQL database from a backup file'

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str, help='Name of the backup file to restore from')

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
        file_name = options['file_name']
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        backup_file = os.path.join(backup_dir, file_name)

        if not os.path.exists(backup_file):
            raise CommandError(f'Backup file "{file_name}" does not exist in the backups directory.')

        # Database connection details
        db_name = config('DB_NAME')
        db_user = config('DB_USER')
        db_password = config('DB_PASSWORD')
        db_host = config('DB_HOST', default='localhost')
        db_port = config('DB_PORT', default='5432')

        # Find psql.exe
        psql_path = self.find_psql()
        if not psql_path:
            raise CommandError('Could not find psql.exe. Please ensure PostgreSQL is installed.')

        # Confirm action
        self.stdout.write(self.style.WARNING(
            f'You are about to restore the database "{db_name}" from the backup file "{file_name}".'))
        self.stdout.write(self.style.WARNING('This will overwrite the current database contents.'))
        confirm = input('Are you sure you want to proceed? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.SUCCESS('Database restore cancelled.'))
            return

        # Drop and recreate the database
        drop_db_command = f'{psql_path} -h {db_host} -p {db_port} -U {db_user} -d postgres -c "DROP DATABASE {db_name};"'
        create_db_command = f'{psql_path} -h {db_host} -p {db_port} -U {db_user} -d postgres -c "CREATE DATABASE {db_name};"'

        # Restore command
        restore_command = f'{psql_path} -h {db_host} -p {db_port} -U {db_user} -d {db_name} -f "{backup_file}"'

        try:
            # Drop the existing database
            subprocess.run(drop_db_command, shell=True, env={**os.environ, 'PGPASSWORD': db_password}, check=True)
            self.stdout.write(self.style.SUCCESS(f'Dropped existing database "{db_name}"'))

            # Create a new database
            subprocess.run(create_db_command, shell=True, env={**os.environ, 'PGPASSWORD': db_password}, check=True)
            self.stdout.write(self.style.SUCCESS(f'Created new database "{db_name}"'))

            # Restore from backup
            subprocess.run(restore_command, shell=True, env={**os.environ, 'PGPASSWORD': db_password}, check=True)
            self.stdout.write(self.style.SUCCESS(f'Successfully restored database from "{file_name}"'))

            # Run migrations to ensure database schema is up to date
            self.stdout.write(self.style.WARNING('Running migrations...'))
            os.system('python manage.py migrate')

            self.stdout.write(self.style.SUCCESS('Database restore and migrations completed successfully.'))

        except subprocess.CalledProcessError as e:
            raise CommandError(f'An error occurred during the database restore process: {str(e)}')