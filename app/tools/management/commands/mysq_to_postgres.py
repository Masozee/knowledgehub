# File: tools/management/commands/mysql_to_postgres.py

import os
import subprocess
import sys
import re
import tempfile
import pymysql
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from decouple import config


class Command(BaseCommand):
    help = 'Converts and restores a MySQL backup file to PostgreSQL database'

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str, help='Name of the MySQL backup file to restore from')

    def find_psql(self):
        """Find PostgreSQL client executable"""
        if sys.platform == 'win32':
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
        else:
            common_paths = [
                '/usr/bin/psql',
                '/usr/local/bin/psql',
                '/usr/local/pgsql/bin/psql'
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return path
        return None

    def convert_mysql_to_postgres(self, input_file):
        """Convert MySQL dump to PostgreSQL compatible format"""
        try:
            # Create a temporary file for the converted SQL
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.sql', delete=False) as temp_file:
                with open(input_file, 'r', encoding='utf8') as mysql_file:
                    content = mysql_file.read()

                # MySQL to PostgreSQL conversions
                conversions = [
                    # Remove MySQL-specific commands
                    (r'SET @.+?;', ''),
                    (r'SET character_set_client.+?;', ''),
                    (r'SET SQL_MODE.+?;', ''),
                    (r'SET time_zone.+?;', ''),
                    (r'SET FOREIGN_KEY_CHECKS.+?;', ''),
                    (r'LOCK TABLES .+?;', ''),
                    (r'UNLOCK TABLES;', ''),

                    # Convert auto_increment
                    (r'auto_increment', 'SERIAL'),

                    # Convert engine definitions
                    (r'ENGINE=\w+', ''),

                    # Convert data types
                    (r'int\(\d+\)', 'integer'),
                    (r'bigint\(\d+\)', 'bigint'),
                    (r'varchar\((\d+)\)', r'varchar(\1)'),
                    (r'datetime', 'timestamp'),
                    (r'longtext', 'text'),
                    (r'tinyint\(\d+\)', 'smallint'),

                    # Convert true/false values
                    (r"'0000-00-00 00:00:00'", 'NULL'),
                    (r"b'0'", 'false'),
                    (r"b'1'", 'true'),

                    # Convert backticks to double quotes
                    (r'`([^`]+)`', r'"\1"'),

                    # Remove COLLATE and CHARACTER SET specifications
                    (r'COLLATE \w+', ''),
                    (r'CHARACTER SET \w+', ''),

                    # Convert IF NOT EXISTS syntax
                    (r'IF NOT EXISTS', ''),
                ]

                # Apply all conversions
                for pattern, replacement in conversions:
                    content = re.sub(pattern, replacement, content)

                # Write converted content to temp file
                temp_file.write(content)
                return temp_file.name

        except Exception as e:
            raise CommandError(f'Error converting MySQL dump to PostgreSQL format: {str(e)}')

    def handle(self, *args, **options):
        file_name = options['file_name']
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        mysql_backup_file = os.path.join(backup_dir, file_name)

        if not os.path.exists(mysql_backup_file):
            raise CommandError(f'Backup file "{file_name}" does not exist in the backups directory.')

        # PostgreSQL connection details
        db_name = config('DB_NAME')
        db_user = config('DB_USER')
        db_password = config('DB_PASSWORD')
        db_host = config('DB_HOST', default='localhost')
        db_port = config('DB_PORT', default='5432')

        # Find psql executable
        psql_path = self.find_psql()
        if not psql_path:
            raise CommandError('Could not find psql executable. Please ensure PostgreSQL is installed.')

        # Confirm action
        self.stdout.write(self.style.WARNING(
            f'You are about to convert and restore MySQL backup "{file_name}" to PostgreSQL database "{db_name}".'))
        self.stdout.write(self.style.WARNING('This will overwrite the current PostgreSQL database contents.'))
        confirm = input('Are you sure you want to proceed? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.SUCCESS('Database restore cancelled.'))
            return

        try:
            # Convert MySQL dump to PostgreSQL format
            self.stdout.write('Converting MySQL dump to PostgreSQL format...')
            postgres_sql_file = self.convert_mysql_to_postgres(mysql_backup_file)

            # Drop and recreate database
            env = {**os.environ, 'PGPASSWORD': db_password}

            drop_cmd = [psql_path, '-h', db_host, '-p', db_port, '-U', db_user,
                        '-d', 'postgres', '-c', f'DROP DATABASE IF EXISTS {db_name}']
            create_cmd = [psql_path, '-h', db_host, '-p', db_port, '-U', db_user,
                          '-d', 'postgres', '-c', f'CREATE DATABASE {db_name}']
            restore_cmd = [psql_path, '-h', db_host, '-p', db_port, '-U', db_user,
                           '-d', db_name, '-f', postgres_sql_file]

            self.stdout.write('Dropping existing database...')
            subprocess.run(drop_cmd, env=env, check=True)

            self.stdout.write('Creating new database...')
            subprocess.run(create_cmd, env=env, check=True)

            self.stdout.write('Restoring converted backup...')
            subprocess.run(restore_cmd, env=env, check=True)

            # Clean up temporary file
            os.unlink(postgres_sql_file)

            # Run migrations
            self.stdout.write('Running migrations...')
            os.system('python manage.py migrate')

            self.stdout.write(self.style.SUCCESS('MySQL to PostgreSQL conversion and restore completed successfully.'))

        except subprocess.CalledProcessError as e:
            raise CommandError(f'An error occurred during the database restore process: {str(e)}')
        except Exception as e:
            raise CommandError(f'An unexpected error occurred: {str(e)}')