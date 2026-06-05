"""
core/models.py
All database models for InternLink.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ─── Custom User Manager ─────────────────────────────────────────────────────

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra):
        extra.setdefault('is_staff',     True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('role',         'ADMIN')
        return self.create_user(email, password, **extra)


# ─── User ────────────────────────────────────────────────────────────────────

class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('ADMIN',   'Admin'),
    ]

    email      = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects    = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


# ─── Student Profile ─────────────────────────────────────────────────────────

class Profile(models.Model):

    LEVEL_CHOICES = [
        ('HND',        'HND'),
        ('DEGREE',     'Degree'),
        ('MASTERS',    'Masters'),
        ('PHD',        'PhD'),
        ('OTHER',      'Other'),
    ]

    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone       = models.CharField(max_length=20,  blank=True)
    university  = models.CharField(max_length=200, blank=True)
    course      = models.CharField(max_length=200, blank=True)
    level       = models.CharField(max_length=10,  choices=LEVEL_CHOICES, blank=True)
    gpa         = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    bio         = models.TextField(blank=True)
    skills      = models.TextField(blank=True, help_text='Comma-separated skills')
    linkedin    = models.URLField(blank=True)
    github      = models.URLField(blank=True)
    cv          = models.FileField(upload_to='cvs/', null=True, blank=True)
    avatar      = models.ImageField(upload_to='avatars/', null=True, blank=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Profile of {self.user.full_name}'


# ─── Opportunity ─────────────────────────────────────────────────────────────

class Opportunity(models.Model):

    TYPE_CHOICES = [
        ('INTERNSHIP',   'Internship'),
        ('SCHOLARSHIP',  'Scholarship'),
    ]

    MODE_CHOICES = [
        ('REMOTE',   'Remote'),
        ('ONSITE',   'On-site'),
        ('HYBRID',   'Hybrid'),
    ]

    STATUS_CHOICES = [
        ('OPEN',   'Open'),
        ('CLOSED', 'Closed'),
    ]

    title          = models.CharField(max_length=255)
    type           = models.CharField(max_length=15,  choices=TYPE_CHOICES)
    company        = models.CharField(max_length=200)
    location       = models.CharField(max_length=200, blank=True)
    mode           = models.CharField(max_length=10,  choices=MODE_CHOICES, default='ONSITE')
    description    = models.TextField()
    requirements   = models.TextField(blank=True)
    stipend        = models.CharField(max_length=100, blank=True, help_text='e.g. $500/month or N/A')
    duration       = models.CharField(max_length=100, blank=True, help_text='e.g. 3 months')
    deadline       = models.DateField(null=True, blank=True)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    created_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='opportunities')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Opportunities'

    def __str__(self):
        return f'{self.title} @ {self.company}'


# ─── Application ─────────────────────────────────────────────────────────────

class Application(models.Model):

    STATUS_CHOICES = [
        ('PENDING',   'Pending'),
        ('REVIEWED',  'Reviewed'),
        ('ACCEPTED',  'Accepted'),
        ('REJECTED',  'Rejected'),
    ]

    student        = models.ForeignKey(User,        on_delete=models.CASCADE, related_name='applications')
    opportunity    = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    cover_letter   = models.TextField(blank=True)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    admin_notes    = models.TextField(blank=True)
    applied_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        # One student can only apply once per opportunity
        unique_together = ('student', 'opportunity')
        ordering        = ['-applied_at']

    def __str__(self):
        return f'{self.student.full_name} → {self.opportunity.title}'
