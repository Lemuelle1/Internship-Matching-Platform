"""
core/urls.py
Page routes + API routes for InternLink.
"""

from django.urls import path
from django.shortcuts import render
from .views import (
    RegisterView, LoginView, LogoutView, MeView,
    MyProfileView, CVUploadView,
    OpportunityListCreateView, OpportunityDetailView,
    ApplyView, MyApplicationsView, WithdrawApplicationView,
    AdminApplicationListView, AdminApplicationDetailView,
    AdminStudentListView, AdminStudentDetailView,
    AdminDashboardStatsView, StudentDashboardStatsView,
    TeamMemberListCreateView, TeamMemberDetailView,
)

# ── Simple page views (render HTML templates) ────────────────
def index(request):         return render(request, 'core/index.html')
def login_page(request):    return render(request, 'core/login.html')
def register_page(request): return render(request, 'core/register.html')
def dashboard(request):     return render(request, 'core/dashboard.html')
def opportunities(request): return render(request, 'core/opportunities.html')
def about(request):         return render(request, 'core/about.html')
def admin_panel(request):   return render(request, 'core/admin_panel.html')
def about_admin(request):   return render(request, 'core/about_admin.html')

urlpatterns = [

    # ═══════════════════════════════════════════════════
    # HTML PAGES
    # ═══════════════════════════════════════════════════
    path('',                index,          name='index'),
    path('login/',          login_page,     name='login'),
    path('register/',       register_page,  name='register'),
    path('dashboard/',      dashboard,      name='dashboard'),
    path('opportunities/',  opportunities,  name='opportunities'),
    path('about/',          about,          name='about'),
    path('admin-panel/',    admin_panel,    name='admin_panel'),
    path('about-admin/',    about_admin,    name='about_admin'),

    # ═══════════════════════════════════════════════════
    # AUTH
    # ═══════════════════════════════════════════════════
    path('api/auth/register/', RegisterView.as_view(),  name='register-api'),
    path('api/auth/login/',    LoginView.as_view(),     name='login-api'),
    path('api/auth/logout/',   LogoutView.as_view(),    name='logout'),
    path('api/auth/me/',       MeView.as_view(),        name='me'),

    # ═══════════════════════════════════════════════════
    # PROFILE
    # ═══════════════════════════════════════════════════
    path('api/profile/',     MyProfileView.as_view(), name='my-profile'),
    path('api/profile/cv/',  CVUploadView.as_view(),  name='cv-upload'),

    # ═══════════════════════════════════════════════════
    # OPPORTUNITIES
    # ═══════════════════════════════════════════════════
    path('api/opportunities/',         OpportunityListCreateView.as_view(), name='opportunities-api'),
    path('api/opportunities/<int:pk>/', OpportunityDetailView.as_view(),    name='opportunity-detail'),

    # ═══════════════════════════════════════════════════
    # APPLICATIONS (STUDENT)
    # ═══════════════════════════════════════════════════
    path('api/applications/',                    ApplyView.as_view(),            name='apply'),
    path('api/applications/mine/',               MyApplicationsView.as_view(),   name='my-applications'),
    path('api/applications/<int:pk>/withdraw/',  WithdrawApplicationView.as_view(), name='withdraw'),

    # ═══════════════════════════════════════════════════
    # ADMIN
    # ═══════════════════════════════════════════════════
    path('api/admin/stats/',                      AdminDashboardStatsView.as_view(),   name='admin-stats'),
    path('api/dashboard/stats/',                  StudentDashboardStatsView.as_view(), name='student-stats'),
    path('api/admin/students/',                   AdminStudentListView.as_view(),      name='admin-students'),
    path('api/admin/students/<int:pk>/',          AdminStudentDetailView.as_view(),    name='admin-student-detail'),
    path('api/admin/applications/',               AdminApplicationListView.as_view(),  name='admin-applications'),
    path('api/admin/applications/<int:pk>/',      AdminApplicationDetailView.as_view(),name='admin-application-detail'),

    # ═══════════════════════════════════════════════════
    # TEAM
    # ═══════════════════════════════════════════════════
    path('api/admin/team/',          TeamMemberListCreateView.as_view(), name='team'),
    path('api/admin/team/<int:pk>/', TeamMemberDetailView.as_view(),     name='team-detail'),
]