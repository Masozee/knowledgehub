# urls.py
from django.urls import path
from . import views

app_name = 'project'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<uuid:uuid>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<uuid:uuid>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
    path('complete/<uuid:uuid>/', views.mark_project_complete, name='complete'),

    #Task
    path('<uuid:project_uuid>/progress/', views.TaskKanbanView.as_view(), name='task_kanban'),
    path('<uuid:project_uuid>/outreach/', views.ProjectOutreachView.as_view(), name='outreach'),
    path('<uuid:project_uuid>/data/', views.ResearchDataListView.as_view(), name='data-research'),

    # Task List View
    path('<uuid:project_uuid>/tasks/', views.TaskListView.as_view(), name='task_list'),

    # Task CRUD operations
    path('<uuid:project_uuid>/tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('<uuid:project_uuid>/tasks/<str:code>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('<uuid:project_uuid>/tasks/<str:code>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    path('<uuid:project_uuid>/tasks/<str:code>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),

    #Fund
    path('<uuid:project_uuid>/funding/', views.ProjectFundUsageView.as_view(), name='funding'),

    path('<uuid:project_uuid>/settings/', views.ProjectConfigView.as_view(), name='settings'),
    path('<uuid:project_uuid>/settings/update/', views.ProjectSettingsUpdateView.as_view(), name='update_settings'),
    path('<uuid:project_uuid>/funding/add/', views.ProjectFundingCreateView.as_view(), name='add_funding'),
    path('<uuid:project_uuid>/logs/', views.ProjectLogsView.as_view(), name='project_logs'),

    #team
    path('<uuid:project_uuid>/team/', views.ProjectTeamView.as_view(), name='team'),
    path('<uuid:project_uuid>/team/invite/', views.InviteMemberView.as_view(), name='invite_member'),
    path('<uuid:project_uuid>/team/<int:member_id>/update-role/', views.UpdateMemberRoleView.as_view(), name='update_member_role'),
    path('<uuid:project_uuid>/team/<int:member_id>/remove/', views.RemoveMemberView.as_view(), name='remove_member'),

    # Task Status Update API
    path('<uuid:project_uuid>/tasks/<str:code>/update-status/',
         views.TaskUpdateStatusView.as_view(),
         name='task_update_status'),
]
