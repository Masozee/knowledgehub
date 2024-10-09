# File: tools/management/commands/auto_backup_db.py

import os
import subprocess
import sys
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from decouple import config
from app.tools.models import DatabaseBackup


class Command(BaseCommand):
    help = 'Automatically backs up the PostgreSQL database and saves info to DatabaseBackup model'

    def find_pg_dump(self):
        # Common PostgreSQL installation directories on Windows
        common_dirs = [
            r'C:\Program Files\PostgreSQL',
            r'C:\Program Files (x86)\PostgreSQL',
        ]

        for base_dir in common_dirs:
            if os.path.exists(base_dir):
                # List all version directories
                versions = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
                # Sort versions in descending order
                versions.sort(reverse=True)
                for version in versions:
                    pg_dump_path = os.path.join(base_dir, version, 'bin', 'pg_dump.exe')
                    if os.path.exists(pg_dump_path):
                        return pg_dump_path
        return None

    def handle(self, *args, **options):
        # Find pg_dump.exe
        pg_dump_path = self.find_pg_dump()
        if not pg_dump_path:
            self.stderr.write(self.style.ERROR('Could not find pg_dump.exe. Please ensure PostgreSQL is installed.'))
            return

        # Database connection details
        db_name = config('DB_NAME')
        db_user = config('DB_USER')
        db_host = config('DB_HOST', default='localhost')
        db_port = config('DB_PORT', default='5432')
        db_password = config('DB_PASSWORD')

        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Generate backup filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = os.path.join(backup_dir, f'db_backup_{timestamp}.sql')

        # Construct the pg_dump command
        dump_command = [
            pg_dump_path,
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-d', db_name,
            '-f', backup_filename,
        ]

        try:
            # Execute the pg_dump command
            result = subprocess.run(dump_command, check=True, env={**os.environ, 'PGPASSWORD': db_password},
                                    capture_output=True, text=True)

            # Get the size of the backup file
            file_size = os.path.getsize(backup_filename)

            # Save backup information to the DatabaseBackup model
            backup = DatabaseBackup.objects.create(
                file_name=backup_filename,
                file_size=file_size
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully backed up database to {backup_filename}'))
            self.stdout.write(self.style.SUCCESS(f'Backup info saved with ID: {backup.id}'))

        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f'An error occurred while backing up the database:'))
            self.stderr.write(self.style.ERROR(f'Command: {e.cmd}'))
            self.stderr.write(self.style.ERROR(f'Return code: {e.returncode}'))
            self.stderr.write(self.style.ERROR(f'Output: {e.output}'))
            self.stderr.write(self.style.ERROR(f'Stderr: {e.stderr}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {e}'))
            self.stderr.write(self.style.ERROR(f'Error type: {type(e).__name__}'))
            self.stderr.write(self.style.ERROR(f'Error details: {str(e)}'))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            import traceback
            traceback.print_exception(exc_type, exc_value, exc_traceback)