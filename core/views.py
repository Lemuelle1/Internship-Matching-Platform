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

from .models       import User, Profile, Opportunity, Application, TeamMember
from .serializers  import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ProfileSerializer, OpportunitySerializer,
    ApplicationSerializer, ApplicationStatusSerializer,
    TeamMemberSerializer
)
from .permissions  import IsAdmin, IsStudent, IsAdminOrReadOnly


# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            Profile.objects.create(user=user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Account created successfully.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully.'})


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE
# ══════════════════════════════════════════════════════════════════════════════

class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class   = ProfileSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class CVUploadView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        cv_file = request.FILES.get('cv')

        if not cv_file:
            return Response({'error': 'No file provided.'}, status=400)

        if not cv_file.name.endswith('.pdf'):
            return Response({'error': 'Only PDF files allowed.'}, status=400)

        profile.cv = cv_file
        profile.save()

        return Response({
            'message': 'CV uploaded successfully.',
            'cv_url': request.build_absolute_uri(profile.cv.url)
        })


# ══════════════════════════════════════════════════════════════════════════════
# OPPORTUNITIES
# ══════════════════════════════════════════════════════════════════════════════

class OpportunityListCreateView(generics.ListCreateAPIView):
    serializer_class   = OpportunitySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'company', 'location', 'description']
    ordering           = ['-created_at']

    def get_queryset(self):
        qs = Opportunity.objects.all()

        if self.request.user.role == 'STUDENT':
            qs = qs.filter(status='OPEN')
        else:
            status_filter = self.request.query_params.get('status')
            if status_filter:
                qs = qs.filter(status=status_filter.upper())

        return qs


class OpportunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = Opportunity.objects.all()
    serializer_class   = OpportunitySerializer
    permission_classes = [IsAdminOrReadOnly]


# ══════════════════════════════════════════════════════════════════════════════
# APPLICATIONS (STUDENTS)
# ══════════════════════════════════════════════════════════════════════════════

class ApplyView(generics.CreateAPIView):
    serializer_class   = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsStudent]


class MyApplicationsView(generics.ListAPIView):
    serializer_class   = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user)


class WithdrawApplicationView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def delete(self, request, pk):
        app = get_object_or_404(Application, pk=pk, student=request.user)

        if app.status != 'PENDING':
            return Response({'error': 'Only pending applications can be withdrawn.'}, status=400)

        app.delete()
        return Response({'message': 'Application withdrawn.'}, status=204)


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN — APPLICATIONS (UPDATED + MERGED LOGIC)
# ══════════════════════════════════════════════════════════════════════════════

class AdminApplicationListView(generics.ListAPIView):
    """
    GET /api/admin/applications/
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        qs = Application.objects.all().select_related('student', 'opportunity')

        opp_id = self.request.query_params.get('opportunity')
        if opp_id:
            qs = qs.filter(opportunity_id=opp_id)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter.upper())

        return qs

    def list(self, request, *args, **kwargs):
        apps = self.get_queryset()

        data = []
        for a in apps:
            profile = getattr(a.student, 'profile', None)

            data.append({
                "id": a.id,
                "student_name": a.student.get_full_name() or a.student.username,
                "student_email": a.student.email,
                "opportunity_title": a.opportunity.title,
                "status": a.status,
                "applied_at": a.created_at,
                "admin_notes": getattr(a, "admin_notes", ""),
                "cv": profile.cv.url if profile and profile.cv else None
            })

        return Response(data)


class AdminApplicationDetailView(generics.RetrieveUpdateAPIView):
    """
    PATCH /api/admin/applications/<id>/
    """
    queryset = Application.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        return ApplicationStatusSerializer if self.request.method in ['PATCH', 'PUT'] else ApplicationSerializer


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN — STUDENTS (UPDATED FORMAT MATCHING YOUR FIRST CODE)
# ══════════════════════════════════════════════════════════════════════════════

class AdminStudentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return User.objects.filter(role='STUDENT')

    def list(self, request, *args, **kwargs):
        students = self.get_queryset()

        return Response([
            {
                "full_name": s.get_full_name() or s.username,
                "email": s.email,
                "created_at": s.date_joined
            }
            for s in students
        ])


class AdminStudentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        student = get_object_or_404(User, pk=pk, role='STUDENT')
        profile = getattr(student, 'profile', None)

        return Response({
            "user": UserSerializer(student).data,
            "profile": ProfileSerializer(profile, context={'request': request}).data if profile else None
        })


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD STATS
# ══════════════════════════════════════════════════════════════════════════════

class AdminDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({
            'total_students': User.objects.filter(role='STUDENT').count(),
            'total_opportunities': Opportunity.objects.count(),
            'open_opportunities': Opportunity.objects.filter(status='OPEN').count(),
            'total_applications': Application.objects.count(),
            'pending_applications': Application.objects.filter(status='PENDING').count(),
        })


class StudentDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        apps = Application.objects.filter(student=request.user)
        return Response({
            'total_applications': apps.count(),
            'pending': apps.filter(status='PENDING').count(),
            'accepted': apps.filter(status='ACCEPTED').count(),
            'rejected': apps.filter(status='REJECTED').count(),
        })


# ══════════════════════════════════════════════════════════════════════════════
# TEAM
# ══════════════════════════════════════════════════════════════════════════════

class TeamMemberListCreateView(generics.ListCreateAPIView):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class TeamMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated, IsAdmin]