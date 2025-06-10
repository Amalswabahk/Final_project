from django.urls import path
from . import views
from django.urls import path
from .views import (
    DepartmentListView,
    DepartmentDetailView,
    DepartmentCreateView,
    DepartmentDeleteView
)

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/login/', views.admin_login, name='admin-login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),

    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('groups/', views.group_management, name='group_management'),
    path('groups/<int:group_id>/edit/', views.edit_group, name='edit_group'),

    # Facility Management
    path('facilities/', views.facility_management, name='facility_management'),
    path('facilities/<int:facility_id>/edit/', views.edit_facility, name='edit_facility'),
    path('departments/', views.department_management, name='department_management'),
    path('departments/<int:department_id>/edit/', views.edit_department, name='edit_department'),
    path('resources/', views.resource_management, name='resource_management'),
    path('resources/<int:resource_id>/edit/', views.edit_resource, name='edit_resource'),

    # Appointment Management
    path('appointments/', views.admin_appointment_management, name='admin_appointment_management'),
    path('appointments/<int:appointment_id>/edit/', views.edit_appointment, name='edit_appointment'),


    path('healthcare-providers/register/', views.register_healthcare_provider, name='register_healthcare_provider'),
    path('providers/', views.healthcare_provider_list, name='provider-list'),
    path('providers/create/', views.healthcare_provider_create, name='provider-create'),
    path('providers/<int:pk>/', views.healthcare_provider_detail, name='provider-detail'),
    path('providers/<int:pk>/update/', views.healthcare_provider_update, name='provider-update'),
    path('providers/<int:pk>/delete/', views.healthcare_provider_delete, name='provider-delete'),
    path('toggle-sidebar/', views.toggle_sidebar, name='toggle_sidebar'),



    path('department/', DepartmentListView.as_view(), name='department-list'),
    path('department/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
    path('department/create/', DepartmentCreateView.as_view(), name='department-create'),
    path('department/<int:pk>/delete/', DepartmentDeleteView.as_view(), name='department-delete'),

]