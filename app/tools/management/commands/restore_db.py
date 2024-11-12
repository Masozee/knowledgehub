# File: tools/management/commands/restore_db.py

import os
import subprocess
import sys
import pymysql

pymysql.install_as_MySQLdb()
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from decouple import config


class Command(BaseCommand):
    help = 'Restores the MySQL or PostgreSQL database from a backup file'

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str, help='Name of the backup file to restore from')

    def find_executable(self, db_type, client=False):
        """
        Find database executable based on OS and database type.
        client: If True, find client executable (psql/mysql), else find server executable (pg_restore/mysql)
        """
        if sys.platform == 'win32':
            # Windows paths
            common_dirs = {
                'postgresql': [
                    r'C:\Program Files\PostgreSQL',
                    r'C:\Program Files (x86)\PostgreSQL'
                ],
                'mysql': [
                    r'C:\Program Files\MySQL',
                    r'C:\Program Files (x86)\MySQL',
                    r'C:\xampp\mysql\bin'
                ]
            }

            if db_type == 'postgresql':
                exe_name = 'psql.exe' if client else 'pg_restore.exe'
            else:
                exe_name = 'mysql.exe' if client else 'mysql.exe'

            for base_dir in common_dirs[db_type]:
                if os.path.exists(base_dir):
                    if db_type == 'postgresql':
                        versions = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
                        versions.sort(reverse=True)
                        for version in versions:
                            exe_path = os.path.join(base_dir, version, 'bin', exe_name)
                            if os.path.exists(exe_path):
                                return exe_path
                    else:
                        exe_path = os.path.join(base_dir, 'bin', exe_name)
                        if os.path.exists(exe_path):
                            return exe_path
        else:
            # Linux/Unix/Mac paths
            if db_type == 'postgresql':
                common_paths = [
                    '/usr/bin/psql' if client else '/usr/bin/pg_restore',
                    '/usr/local/bin/psql' if client else '/usr/local/bin/pg_restore',
                    '/usr/local/pgsql/bin/psql' if client else '/usr/local/pgsql/bin/pg_restore'
                ]
            else:
                common_paths = [
                    '/usr/bin/mysql',
                    '/usr/local/bin/mysql',
                    '/usr/local/mysql/bin/mysql',
                    '/usr/local/cpanel/3rdparty/bin/mysql'  # cPanel path
                ]

            for path in common_paths:
                if os.path.exists(path):
                    return path

        return None

    def test_connection(self, db_type, db_name, db_user, db_password, db_host, db_port):
        """Test database connection before attempting restore."""
        try:
            if db_type == 'mysql':
                conn = pymysql.connect(
                    host=db_host,
                    port=int(db_port),
                    user=db_user,
                    password=db_password
                )
                conn.close()
                return True
            else:
                import psycopg2
                conn = psycopg2.connect(
                    dbname='postgres',  # Connect to default database first
                    user=db_user,
                    password=db_password,
                    host=db_host,
                    port=db_port
                )
                conn.close()
                return True
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Database connection test failed: {str(e)}'))
            return False

    def handle(self, *args, **options):
        file_name = options['file_name']
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        backup_file = os.path.join(backup_dir, file_name)

        if not os.path.exists(backup_file):
            raise CommandError(f'Backup file "{file_name}" does not exist in the backups directory.')

        # Database connection details
        db_type = config('DB_TYPE', default='mysql').lower()
        db_name = config('DB_NAME')
        db_user = config('DB_USER')
        db_password = config('DB_PASSWORD')
        db_host = config('DB_HOST', default='localhost')
        db_port = config('DB_PORT', default='3306' if db_type == 'mysql' else '5432')

        # Find database client executable
        client_exe = self.find_executable(db_type, client=True)
        if not client_exe:
            raise CommandError(f'Could not find {db_type} client executable. Please ensure it is installed.')

        # Test connection
        if not self.test_connection(db_type, db_name, db_user, db_password, db_host, db_port):
            raise CommandError('Database connection test failed. Please check your credentials.')

        # Confirm action
        self.stdout.write(self.style.WARNING(
            f'You are about to restore the {db_type} database "{db_name}" from the backup file "{file_name}".'))
        self.stdout.write(self.style.WARNING('This will overwrite the current database contents.'))
        confirm = input('Are you sure you want to proceed? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.SUCCESS('Database restore cancelled.'))
            return

        try:
            if db_type == 'postgresql':
                # PostgreSQL restore process
                env = {**os.environ, 'PGPASSWORD': db_password}

                # Drop and recreate database
                drop_cmd = [client_exe, '-h', db_host, '-p', db_port, '-U', db_user,
                            '-d', 'postgres', '-c', f'DROP DATABASE IF EXISTS {db_name}']
                create_cmd = [client_exe, '-h', db_host, '-p', db_port, '-U', db_user,
                              '-d', 'postgres', '-c', f'CREATE DATABASE {db_name}']
                restore_cmd = [client_exe, '-h', db_host, '-p', db_port, '-U', db_user,
                               '-d', db_name, '-f', backup_file]

                subprocess.run(drop_cmd, env=env, check=True)
                self.stdout.write(self.style.SUCCESS(f'Dropped existing database "{db_name}"'))

                subprocess.run(create_cmd, env=env, check=True)
                self.stdout.write(self.style.SUCCESS(f'Created new database "{db_name}"'))

                subprocess.run(restore_cmd, env=env, check=True)
            else:
                # MySQL restore process
                mysql_cmd = [
                    client_exe,
                    f'-h{db_host}',
                    f'-P{db_port}',
                    f'-u{db_user}',
                    f'-p{db_password}',
                ]

                # Drop and create database
                drop_create_sql = f'DROP DATABASE IF EXISTS {db_name}; CREATE DATABASE {db_name};'
                subprocess.run(mysql_cmd, input=drop_create_sql.encode(), check=True)
                self.stdout.write(self.style.SUCCESS(f'Recreated database "{db_name}"'))

                # Restore from backup
                restore_cmd = [*mysql_cmd, db_name]
                with open(backup_file, 'r', encoding='utf8') as f:
                    subprocess.run(restore_cmd, stdin=f, check=True)

            self.stdout.write(self.style.SUCCESS(f'Successfully restored database from "{file_name}"'))

            # Run migrations
            self.stdout.write(self.style.WARNING('Running migrations...'))
            os.system('python manage.py migrate')

            self.stdout.write(self.style.SUCCESS('Database restore and migrations completed successfully.'))

        except subprocess.CalledProcessError as e:
            raise CommandError(f'An error occurred during the database restore process: {str(e)}')
        except Exception as e:
            raise CommandError(f'An unexpected error occurred: {str(e)}')