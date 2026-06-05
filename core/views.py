"""
core/views.py
All API endpoint logic for InternLink.
"""

from rest_framework                 import generics, status, filters
from rest_framework.views           import APIView
from rest_framework.response        import Response
from rest_framework.permissions     import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.parsers         import MultiPartParser, FormParser, JSONParser
from django.shortcuts               import get_object_or_404
from django_filters.rest_framework  import DjangoFilterBackend

from .models       import User, Profile, Opportunity, Application
from .serializers  import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ProfileSerializer, OpportunitySerializer,
    ApplicationSerializer, ApplicationStatusSerializer
)
from .permissions  import IsAdmin, IsStudent, IsAdminOrReadOnly, IsOwnerOrAdmin


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════════════════

class RegisterView(APIView):
    """POST /api/auth/register/ — create a new student account."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user  = serializer.save()
            Profile.objects.create(user=user)          # auto-create empty profile
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user':  UserSerializer(user).data,
                'message': 'Account created successfully.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """POST /api/auth/login/ — authenticate and return token."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user  = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user':  UserSerializer(user).data,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """POST /api/auth/logout/ — invalidate token."""

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully.'})


class MeView(APIView):
    """GET /api/auth/me/ — return current user info."""

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ══════════════════════════════════════════════════════════════════════════════
#  PROFILE
# ══════════════════════════════════════════════════════════════════════════════

class MyProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/profile/      — view my profile
    PUT  /api/profile/      — update my profile
    PATCH /api/profile/     — partial update
    """
    serializer_class   = ProfileSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class CVUploadView(APIView):
    """
    POST /api/profile/cv/ — upload or replace CV (PDF).
    """
    permission_classes = [IsAuthenticated, IsStudent]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        cv_file    = request.FILES.get('cv')
        if not cv_file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        if not cv_file.name.endswith('.pdf'):
            return Response({'error': 'Only PDF files are accepted.'}, status=status.HTTP_400_BAD_REQUEST)
        profile.cv = cv_file
        profile.save()
        return Response({
            'message': 'CV uploaded successfully.',
            'cv_url':  request.build_absolute_uri(profile.cv.url)
        })


# ══════════════════════════════════════════════════════════════════════════════
#  OPPORTUNITIES
# ══════════════════════════════════════════════════════════════════════════════

class OpportunityListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/opportunities/        — list all open opportunities (students) or all (admin)
    POST /api/opportunities/        — create new opportunity (admin only)
    """
    serializer_class   = OpportunitySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'company', 'location', 'description']
    ordering_fields    = ['created_at', 'deadline', 'title']
    ordering           = ['-created_at']

    def get_queryset(self):
        qs = Opportunity.objects.all()

        # Filter by type
        opp_type = self.request.query_params.get('type')
        if opp_type:
            qs = qs.filter(type=opp_type.upper())

        # Filter by status — students only see OPEN
        if self.request.user.role == 'STUDENT':
            qs = qs.filter(status='OPEN')
        else:
            status_filter = self.request.query_params.get('status')
            if status_filter:
                qs = qs.filter(status=status_filter.upper())

        # Filter by mode
        mode = self.request.query_params.get('mode')
        if mode:
            qs = qs.filter(mode=mode.upper())

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class OpportunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/opportunities/<id>/   — view single opportunity
    PUT    /api/opportunities/<id>/   — edit  (admin only)
    PATCH  /api/opportunities/<id>/   — partial edit (admin only)
    DELETE /api/opportunities/<id>/   — delete (admin only)
    """
    queryset           = Opportunity.objects.all()
    serializer_class   = OpportunitySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


# ══════════════════════════════════════════════════════════════════════════════
#  APPLICATIONS
# ══════════════════════════════════════════════════════════════════════════════

class ApplyView(generics.CreateAPIView):
    """
    POST /api/applications/   — student submits an application.
    """
    serializer_class   = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class MyApplicationsView(generics.ListAPIView):
    """
    GET /api/applications/mine/   — student views their own applications.
    """
    serializer_class   = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user).select_related('opportunity')


class AdminApplicationListView(generics.ListAPIView):
    """
    GET /api/admin/applications/                      — all applications
    GET /api/admin/applications/?opportunity=<id>     — filter by opportunity
    GET /api/admin/applications/?status=PENDING       — filter by status
    """
    serializer_class   = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['student__first_name', 'student__last_name', 'student__email',
                          'opportunity__title', 'opportunity__company']
    ordering_fields    = ['applied_at', 'status']

    def get_queryset(self):
        qs = Application.objects.all().select_related('student', 'opportunity')
        opp_id = self.request.query_params.get('opportunity')
        if opp_id:
            qs = qs.filter(opportunity_id=opp_id)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter.upper())
        return qs


class AdminApplicationDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/admin/applications/<id>/   — view single application
    PATCH /api/admin/applications/<id>/   — update status / add notes
    """
    queryset           = Application.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ApplicationStatusSerializer
        return ApplicationSerializer


class WithdrawApplicationView(APIView):
    """
    DELETE /api/applications/<id>/withdraw/   — student withdraws their application.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def delete(self, request, pk):
        app = get_object_or_404(Application, pk=pk, student=request.user)
        if app.status != 'PENDING':
            return Response(
                {'error': 'You can only withdraw pending applications.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        app.delete()
        return Response({'message': 'Application withdrawn.'}, status=status.HTTP_204_NO_CONTENT)


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN — STUDENT MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

class AdminStudentListView(generics.ListAPIView):
    """
    GET /api/admin/students/   — admin views all registered students.
    """
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends    = [filters.SearchFilter]
    search_fields      = ['first_name', 'last_name', 'email']

    def get_queryset(self):
        return User.objects.filter(role='STUDENT').order_by('-created_at')


class AdminStudentDetailView(generics.RetrieveAPIView):
    """
    GET /api/admin/students/<id>/   — view a single student + profile.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        student = get_object_or_404(User, pk=pk, role='STUDENT')
        profile = getattr(student, 'profile', None)
        return Response({
            'user':    UserSerializer(student).data,
            'profile': ProfileSerializer(profile, context={'request': request}).data if profile else None,
        })


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD STATS
# ══════════════════════════════════════════════════════════════════════════════

class AdminDashboardStatsView(APIView):
    """
    GET /api/admin/stats/   — counts for admin dashboard cards.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({
            'total_students':     User.objects.filter(role='STUDENT').count(),
            'total_opportunities': Opportunity.objects.count(),
            'open_opportunities':  Opportunity.objects.filter(status='OPEN').count(),
            'total_applications':  Application.objects.count(),
            'pending_applications': Application.objects.filter(status='PENDING').count(),
            'internships':         Opportunity.objects.filter(type='INTERNSHIP').count(),
            'scholarships':        Opportunity.objects.filter(type='SCHOLARSHIP').count(),
        })


class StudentDashboardStatsView(APIView):
    """
    GET /api/dashboard/stats/   — counts for student dashboard cards.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        apps = Application.objects.filter(student=request.user)
        return Response({
            'total_applications': apps.count(),
            'pending':   apps.filter(status='PENDING').count(),
            'accepted':  apps.filter(status='ACCEPTED').count(),
            'rejected':  apps.filter(status='REJECTED').count(),
            'open_opportunities': Opportunity.objects.filter(status='OPEN').count(),
        })
