import atexit
import django
from django.db import connection


def table_exists(table_name):
    """Check if a table exists in the DB before querying it."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            )
        """, [table_name])
        return cursor.fetchone()[0]


def shutdown_function():
    # Ensure Django is fully loaded and table exists before querying
    if not django.apps.apps.ready:
        return

    from horilla_backup.models import GoogleDriveBackup, LocalBackup

    if table_exists('horilla_backup_googledrivebackup'):
        if GoogleDriveBackup.objects.exists():
            google_drive_backup = GoogleDriveBackup.objects.first()
            google_drive_backup.active = False
            google_drive_backup.save()

    if table_exists('horilla_backup_localbackup'):
        if LocalBackup.objects.exists():
            local_backup = LocalBackup.objects.first()
            local_backup.active = False
            local_backup.save()


try:
    atexit.register(shutdown_function)
except Exception:
    pass
