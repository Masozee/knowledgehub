from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.timezone import make_aware
from allauth.socialaccount.models import SocialAccount, SocialToken
import os
import requests
import logging
from .models import *



logger = logging.getLogger(__name__)
User = get_user_model()


def is_admin(user):
    return user.is_staff or user.is_superuser


def save_photo(backup, item, photo_url):
    """Helper function to save individual photo"""
    try:
        response = requests.get(photo_url)
        if response.status_code == 200:
            filename = item.get('filename', f"{item['id']}.jpg")

            # Create the directory structure if it doesn't exist
            upload_path = f'photo_backups/{backup.user.id}/{backup.id}'
            full_path = os.path.join(settings.MEDIA_ROOT, upload_path)
            os.makedirs(full_path, exist_ok=True)

            # Save the photo file
            file_path = os.path.join(full_path, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)

            # Handle datetime with milliseconds
            created_time = item.get('mediaMetadata', {}).get('creationTime')
            if created_time:
                try:
                    # First try with milliseconds format
                    created_time = make_aware(datetime.strptime(created_time.split('.')[0], '%Y-%m-%dT%H:%M:%S'))
                except ValueError:
                    try:
                        # If that fails, try without milliseconds
                        created_time = make_aware(datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%SZ'))
                    except ValueError:
                        # If both fail, log it and set to None
                        logger.warning(f"Could not parse creation time for photo {item['id']}: {created_time}")
                        created_time = None

            relative_path = os.path.join(upload_path, filename)

            Photo.objects.create(
                backup=backup,
                google_photo_id=item['id'],
                filename=filename,
                original_url=item['baseUrl'],
                mime_type=item['mimeType'],
                created_time=created_time,
                photo_file=relative_path,
                metadata=item.get('mediaMetadata', {})
            )
            return True
    except Exception as e:
        logger.error(f"Failed to save photo {item['id']}: {str(e)}")
        return False
    return False


def process_user_backup(user, admin_user=None):
    """Helper function to process backup for a single user"""
    backup = None
    try:
        # Check for Google account connection
        try:
            social_account = SocialAccount.objects.get(
                user=user,
                provider='google'
            )
        except SocialAccount.DoesNotExist:
            logger.error(f"No Google account connected for user {user.email}")
            return False, f"No Google account connected for user {user.email}"

        # Check for valid token
        try:
            social_token = SocialToken.objects.get(
                account__user=user,
                account__provider='google'
            )
        except SocialToken.DoesNotExist:
            logger.error(f"No valid token found for user {user.email}")
            return False, f"No valid token found for user {user.email}"

        # Create backup record - temporarily remove initiated_by
        backup = PhotoBackup.objects.create(
            user=user,
            status='pending'
        )

        # Create credentials
        credentials = Credentials(
            token=social_token.token,
            refresh_token=social_token.token_secret,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],
            client_secret=settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret'],
            scopes=[
                'https://www.googleapis.com/auth/photoslibrary.readonly',
                'https://www.googleapis.com/auth/photoslibrary'
            ]
        )

        backup.status = 'processing'
        backup.save()

        # Build the Photos API service
        service = build('photoslibrary', 'v1', credentials=credentials, static_discovery=False)

        next_page_token = None
        photo_count = 0
        photos_limit = backup.photos_limit

        while True:
            try:
                results = service.mediaItems().list(
                    pageSize=100,
                    pageToken=next_page_token
                ).execute()

                items = results.get('mediaItems', [])

                for item in items:
                    if photos_limit > 0 and photo_count >= photos_limit:
                        break

                    if item['mimeType'].startswith('image/'):
                        photo_url = f"{item['baseUrl']}=d"
                        if save_photo(backup, item, photo_url):
                            photo_count += 1
                            backup.total_photos = photo_count
                            backup.save()

                if photos_limit > 0 and photo_count >= photos_limit:
                    break

                next_page_token = results.get('nextPageToken')
                if not next_page_token:
                    break

            except HttpError as e:
                error_message = f"Google API error for user {user.email}: {str(e)}"
                logger.error(error_message)
                backup.status = 'failed'
                backup.error_message = error_message
                backup.save()
                return False, error_message

        if photo_count > 0:
            backup.status = 'completed'
            backup.save()
            return True, f'Successfully backed up {photo_count} photos for user {user.email}'
        else:
            backup.status = 'failed'
            backup.error_message = 'No photos found to backup'
            backup.save()
            return False, f'No photos found to backup for user {user.email}'

    except Exception as e:
        error_message = f"Backup failed for user {user.email}: {str(e)}"
        logger.error(error_message)

        if backup:
            backup.status = 'failed'
            backup.error_message = error_message
            backup.save()

        return False, error_message


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_backup_photos(request):
    """View for superusers to backup photos for multiple users"""
    if request.method == 'POST':
        user_ids = request.POST.getlist('users')

        if not user_ids:
            messages.error(request, 'Please select at least one user')
            return redirect('/admin/people/photobackup/')

        success_count = 0
        error_messages = []

        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                success, message = process_user_backup(user, admin_user=request.user)

                if success:
                    success_count += 1
                else:
                    error_messages.append(message)

            except User.DoesNotExist:
                error_messages.append(f"User with ID {user_id} not found")

        if success_count > 0:
            messages.success(request, f'Successfully initiated backup for {success_count} users')

        if error_messages:
            messages.warning(request, 'Errors occurred during backup:\n' + '\n'.join(error_messages))

        return redirect('/admin/people/photobackup/')

    # GET request - show user selection form
    users = User.objects.filter(socialaccount__provider='google').distinct()
    return render(request, 'admin/photo_backup_form.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def backup_photos(request):
    """Original view for individual user backup"""
    success, message = process_user_backup(request.user)

    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect('/admin/people/photobackup/')