# views.py
import os
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from allauth.socialaccount.models import SocialToken, SocialAccount
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .models import PhotoBackup, Photo
import requests
import logging
from datetime import datetime
from django.utils.timezone import make_aware
import json

logger = logging.getLogger(__name__)


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


@login_required
@user_passes_test(is_admin)
def backup_photos(request):
    backup = None

    try:
        # Check for Google account connection
        try:
            social_account = SocialAccount.objects.get(
                user=request.user,
                provider='google'
            )
        except SocialAccount.DoesNotExist:
            messages.error(request, 'Please connect your Google account first')
            return redirect(reverse('socialaccount_connections'))

        # Check for valid token
        try:
            social_token = SocialToken.objects.get(
                account__user=request.user,
                account__provider='google'
            )
        except SocialToken.DoesNotExist:
            messages.error(request, 'Google authentication token not found. Please reconnect your Google account.')
            return redirect(reverse('socialaccount_connections'))

        # Create backup record
        backup = PhotoBackup.objects.create(
            user=request.user,
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
                error_message = f"Google API error: {str(e)}"
                logger.error(error_message)
                backup.status = 'failed'
                backup.error_message = error_message
                backup.save()
                messages.error(request, error_message)
                return redirect('/admin/people/photobackup/')

        if photo_count > 0:
            backup.status = 'completed'
            backup.save()
            messages.success(request, f'Successfully backed up {photo_count} photos!')
        else:
            backup.status = 'failed'
            backup.error_message = 'No photos found to backup'
            backup.save()
            messages.warning(request, 'No photos found to backup')

        return redirect('/admin/people/photobackup/')

    except Exception as e:
        error_message = f"Backup failed: {str(e)}"
        logger.error(f"Backup failed for user {request.user.email}: {str(e)}")

        if backup:
            backup.status = 'failed'
            backup.error_message = error_message
            backup.save()

        messages.error(request, error_message)
        return redirect('/admin/people/photobackup/')