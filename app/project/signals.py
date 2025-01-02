from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from .models import Project, Task, ActivityLog, ProjectMember, ResearchData
from model_utils import FieldTracker


@receiver(post_save, sender=Project)
def log_project_changes(sender, instance, created, **kwargs):
    if created:
        ActivityLog.log_activity(
            actor=instance.created_by,
            action_type='create',
            content_object=instance,
            project=instance,
            description=f"Created new project: {instance.title}"
        )
    else:
        # Log only if specific fields have changed
        changed_fields = []
        if instance.tracker.has_changed('status'):
            changed_fields.append(('status', instance.tracker.previous('status'), instance.status))
        if instance.tracker.has_changed('title'):
            changed_fields.append(('title', instance.tracker.previous('title'), instance.title))

        if changed_fields:
            ActivityLog.log_activity(
                actor=instance._current_user if hasattr(instance, '_current_user') else None,
                action_type='update',
                content_object=instance,
                project=instance,
                description=f"Updated project: {instance.title}",
                changes={
                    'changed_fields': [
                        {
                            'field': field,
                            'from': old_value,
                            'to': new_value
                        } for field, old_value, new_value in changed_fields
                    ]
                }
            )


@receiver(post_save, sender=Task)
def log_task_changes(sender, instance, created, **kwargs):
    if created:
        ActivityLog.log_activity(
            actor=getattr(instance, '_current_user', instance.project.created_by),
            action_type='create',
            content_object=instance,
            project=instance.project,
            description=f"Created new task: {instance.title}"
        )
    else:
        # Log status changes
        if instance.tracker.has_changed('status'):
            ActivityLog.log_activity(
                actor=instance._current_user if hasattr(instance, '_current_user') else None,
                action_type='status_change',
                content_object=instance,
                project=instance.project,
                description=f"Task status changed from {instance.tracker.previous('status')} to {instance.status}",
                changes={
                    'from_status': instance.tracker.previous('status'),
                    'to_status': instance.status
                }
            )


@receiver(m2m_changed, sender=Project.team_members.through)
def log_team_member_changes(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for user_id in pk_set:
            user = settings.AUTH_USER_MODEL.objects.get(id=user_id)
            ActivityLog.log_activity(
                actor=instance._current_user if hasattr(instance, '_current_user') else None,
                action_type='member_add',
                content_object=instance,
                project=instance,
                description=f"Added team member: {user.get_full_name()}"
            )
    elif action == "post_remove":
        for user_id in pk_set:
            user = settings.AUTH_USER_MODEL.objects.get(id=user_id)
            ActivityLog.log_activity(
                actor=instance._current_user if hasattr(instance, '_current_user') else None,
                action_type='member_remove',
                content_object=instance,
                project=instance,
                description=f"Removed team member: {user.get_full_name()}"
            )

'''
@receiver(post_save, sender=Publication)
def log_publication_changes(sender, instance, created, **kwargs):
    if created:
        ActivityLog.log_activity(
            actor=instance._current_user if hasattr(instance, '_current_user') else None,
            action_type='create',
            content_object=instance,
            project=instance.project,
            description=f"Added new publication: {instance.title}"
        )
        
@receiver(post_save, sender=Event)
def log_event_changes(sender, instance, created, **kwargs):
    if created:
        ActivityLog.log_activity(
            actor=instance._current_user if hasattr(instance, '_current_user') else None,
            action_type='create',
            content_object=instance,
            project=instance.project,
            description=f"Created new event: {instance.title}"
        )

'''
@receiver(post_save, sender=ResearchData)
def log_research_data_changes(sender, instance, created, **kwargs):
    if created:
        ActivityLog.log_activity(
            actor=instance.responsible_person,
            action_type='create',
            content_object=instance,
            project=instance.project,
            description=f"Added new research data: {instance.title}"
        )


