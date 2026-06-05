"""
core/urls.py
All API routes for InternLink.
"""

from django.urls import path
from .views import (
    # Auth
    RegisterView, LoginView, LogoutView, MeView,
    # Profile
    MyProfileView, CVUploadView,
    # Opportunities
    OpportunityListCreateView, OpportunityDetailView,
    # Applications
    ApplyView, MyApplicationsView, WithdrawApplicationView,
    # Admin
    AdminApplicationListView, AdminApplicationDetailView,
    AdminStudentListView, AdminStudentDetailView,
    AdminDashboardStatsView, StudentDashboardStatsView,
)

urlpatterns = [

    # ── Authentication ───────────────────────────────────────────────────────
    path('auth/register/', RegisterView.as_view(),  name='register'),
    path('auth/login/',    LoginView.as_view(),     name='login'),
    path('auth/logout/',   LogoutView.as_view(),    name='logout'),
    path('auth/me/',       MeView.as_view(),        name='me'),

    # ── Profile ──────────────────────────────────────────────────────────────
    path('profile/',       MyProfileView.as_view(), name='my-profile'),
    path('profile/cv/',    CVUploadView.as_view(),  name='cv-upload'),

    # ── Opportunities ────────────────────────────────────────────────────────
    path('opportunities/',       OpportunityListCreateView.as_view(), name='opportunities'),
    path('opportunities/<int:pk>/', OpportunityDetailView.as_view(),  name='opportunity-detail'),

    # ── Applications (student) ───────────────────────────────────────────────
    path('applications/',                    ApplyView.as_view(),            name='apply'),
    path('applications/mine/',               MyApplicationsView.as_view(),   name='my-applications'),
    path('applications/<int:pk>/withdraw/',  WithdrawApplicationView.as_view(), name='withdraw'),

    # ── Admin ────────────────────────────────────────────────────────────────
    path('admin/stats/',                        AdminDashboardStatsView.as_view(),    name='admin-stats'),
    path('admin/students/',                     AdminStudentListView.as_view(),        name='admin-students'),
    path('admin/students/<int:pk>/',            AdminStudentDetailView.as_view(),      name='admin-student-detail'),
    path('admin/applications/',                 AdminApplicationListView.as_view(),    name='admin-applications'),
    path('admin/applications/<int:pk>/',        AdminApplicationDetailView.as_view(),  name='admin-application-detail'),

    # ── Student dashboard ────────────────────────────────────────────────────
    path('dashboard/stats/',  StudentDashboardStatsView.as_view(), name='student-stats'),
]
