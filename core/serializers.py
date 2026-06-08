"""
core/serializers.py
Converts model instances to/from JSON for the API.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Profile, Opportunity, Application


# ─── Auth Serializers ─────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, label='Confirm Password')

    class Meta:
        model  = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('Account is disabled.')
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model  = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role', 'created_at']
        read_only_fields = ['id', 'role', 'created_at']


# ─── Profile Serializer ──────────────────────────────────────────────────────

class ProfileSerializer(serializers.ModelSerializer):
    user     = UserSerializer(read_only=True)
    cv_url   = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model  = Profile
        fields = [
            'id', 'user', 'phone', 'university', 'course', 'level',
            'gpa', 'bio', 'skills', 'linkedin', 'github',
            'cv', 'cv_url', 'avatar', 'avatar_url', 'updated_at'
        ]
        extra_kwargs = {
            'cv':     {'write_only': True, 'required': False},
            'avatar': {'write_only': True, 'required': False},
        }

    def get_cv_url(self, obj):
        if obj.cv:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.cv.url) if request else obj.cv.url
        return None

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return None


# ─── Opportunity Serializer ───────────────────────────────────────────────────

class OpportunitySerializer(serializers.ModelSerializer):
    created_by_name  = serializers.ReadOnlyField(source='created_by.full_name')
    application_count = serializers.SerializerMethodField()
    has_applied      = serializers.SerializerMethodField()

    class Meta:
        model  = Opportunity
        fields = [
            'id', 'title', 'type', 'company', 'location', 'mode',
            'description', 'requirements', 'stipend', 'duration',
            'deadline', 'status', 'created_by', 'created_by_name',
            'application_count', 'has_applied', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_application_count(self, obj):
        return obj.applications.count()

    def get_has_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'STUDENT':
            return obj.applications.filter(student=request.user).exists()
        return False


# ─── Application Serializers ─────────────────────────────────────────────────

class ApplicationSerializer(serializers.ModelSerializer):
    student_name      = serializers.ReadOnlyField(source='student.full_name')
    student_email     = serializers.ReadOnlyField(source='student.email')
    opportunity_title = serializers.ReadOnlyField(source='opportunity.title')
    opportunity_company = serializers.ReadOnlyField(source='opportunity.company')

    class Meta:
        model  = Application
        fields = [
            'id', 'student', 'student_name', 'student_email',
            'opportunity', 'opportunity_title', 'opportunity_company',
            'cover_letter', 'status', 'admin_notes',
            'applied_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student', 'status', 'admin_notes', 'applied_at', 'updated_at']

    def validate(self, data):
        request = self.context['request']
        opp     = data.get('opportunity')
        if Application.objects.filter(student=request.user, opportunity=opp).exists():
            raise serializers.ValidationError('You have already applied for this opportunity.')
        if opp.status == 'CLOSED':
            raise serializers.ValidationError('This opportunity is no longer accepting applications.')
        return data

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationStatusSerializer(serializers.ModelSerializer):
    """Admin-only: update status and notes."""

    class Meta:
        model  = Application
        fields = ['status', 'admin_notes']


from .models import TeamMember

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'
