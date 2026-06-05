# InternLink – Backend API

Django REST Framework backend for the InternLink internship & scholarship platform.

---

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create admin account
python manage.py createsuperuser

# 5. Start server
python manage.py runserver
```

Server runs at: **http://127.0.0.1:8000**

---

## Authentication

All protected routes require this header:
```
Authorization: Token <your_token_here>
```

You get the token from login or register.

---

## API Endpoints

### AUTH

| Method | URL | Description | Auth Required |
|--------|-----|-------------|---------------|
| POST | `/api/auth/register/` | Register new student | No |
| POST | `/api/auth/login/` | Login (returns token) | No |
| POST | `/api/auth/logout/` | Logout (deletes token) | Yes |
| GET  | `/api/auth/me/` | Get current user info | Yes |

**Register body:**
```json
{
  "email": "student@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepass123",
  "password2": "securepass123"
}
```

**Login body:**
```json
{
  "email": "student@example.com",
  "password": "securepass123"
}
```

**Login response:**
```json
{
  "token": "abc123xyz...",
  "user": {
    "id": 1,
    "email": "student@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "STUDENT"
  }
}
```

---

### PROFILE (Student only)

| Method | URL | Description |
|--------|-----|-------------|
| GET    | `/api/profile/` | View my profile |
| PUT    | `/api/profile/` | Update full profile |
| PATCH  | `/api/profile/` | Update partial profile |
| POST   | `/api/profile/cv/` | Upload CV (PDF only) |

**Profile update body (form-data or JSON):**
```json
{
  "phone": "0712345678",
  "university": "University of Ghana",
  "course": "Computer Science",
  "level": "DEGREE",
  "gpa": "3.75",
  "bio": "Passionate software developer...",
  "skills": "Python, JavaScript, React",
  "linkedin": "https://linkedin.com/in/johndoe",
  "github": "https://github.com/johndoe"
}
```

**CV Upload (multipart/form-data):**
```
cv: <pdf_file>
```

---

### OPPORTUNITIES

| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| GET    | `/api/opportunities/` | Browse opportunities | Student/Admin |
| POST   | `/api/opportunities/` | Create opportunity | Admin only |
| GET    | `/api/opportunities/<id>/` | View single opportunity | Student/Admin |
| PUT    | `/api/opportunities/<id>/` | Edit opportunity | Admin only |
| PATCH  | `/api/opportunities/<id>/` | Partial edit | Admin only |
| DELETE | `/api/opportunities/<id>/` | Delete opportunity | Admin only |

**Query params for browsing:**
```
/api/opportunities/?type=INTERNSHIP
/api/opportunities/?type=SCHOLARSHIP
/api/opportunities/?mode=REMOTE
/api/opportunities/?search=software
/api/opportunities/?ordering=-deadline
```

**Create opportunity body (Admin):**
```json
{
  "title": "Software Engineering Intern",
  "type": "INTERNSHIP",
  "company": "Tech Corp Ghana",
  "location": "Accra, Ghana",
  "mode": "HYBRID",
  "description": "Join our engineering team...",
  "requirements": "Python, Django, 3.0+ GPA",
  "stipend": "GHS 800/month",
  "duration": "3 months",
  "deadline": "2025-08-31"
}
```

---

### APPLICATIONS

| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| POST   | `/api/applications/` | Apply for opportunity | Student |
| GET    | `/api/applications/mine/` | My applications | Student |
| DELETE | `/api/applications/<id>/withdraw/` | Withdraw application | Student |

**Apply body:**
```json
{
  "opportunity": 3,
  "cover_letter": "I am very interested in this role because..."
}
```

---

### ADMIN ENDPOINTS

| Method | URL | Description |
|--------|-----|-------------|
| GET    | `/api/admin/stats/` | Dashboard summary counts |
| GET    | `/api/admin/students/` | All registered students |
| GET    | `/api/admin/students/<id>/` | Single student + profile |
| GET    | `/api/admin/applications/` | All applications |
| GET    | `/api/admin/applications/?opportunity=<id>` | Filter by opportunity |
| GET    | `/api/admin/applications/?status=PENDING` | Filter by status |
| PATCH  | `/api/admin/applications/<id>/` | Update application status |

**Update application status (Admin):**
```json
{
  "status": "ACCEPTED",
  "admin_notes": "Great candidate, proceeding to interview."
}
```

**Status values:** `PENDING` · `REVIEWED` · `ACCEPTED` · `REJECTED`

---

### STUDENT DASHBOARD

| Method | URL | Description |
|--------|-----|-------------|
| GET    | `/api/dashboard/stats/` | Application counts summary |

**Response:**
```json
{
  "total_applications": 5,
  "pending": 3,
  "accepted": 1,
  "rejected": 1,
  "open_opportunities": 12
}
```

---

## Project Structure

```
InternLink/
├── manage.py
├── requirements.txt
├── README.md
├── internlink/              ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                    ← Main app
│   ├── models.py            ← User, Profile, Opportunity, Application
│   ├── serializers.py       ← JSON conversion
│   ├── views.py             ← API logic
│   ├── urls.py              ← Route definitions
│   ├── permissions.py       ← IsAdmin, IsStudent, IsOwnerOrAdmin
│   ├── admin.py             ← Django admin panel config
│   └── migrations/
└── media/                   ← Uploaded CVs and avatars
    ├── cvs/
    └── avatars/
```

---

## Database Models

```
User          email, first_name, last_name, role (STUDENT/ADMIN)
Profile       phone, university, course, level, gpa, bio, skills, cv, avatar
Opportunity   title, type, company, location, mode, description, deadline, status
Application   student → opportunity, cover_letter, status, admin_notes
```

---

## Connecting Your Frontend

Store the token after login:
```javascript
localStorage.setItem('token', response.data.token);
```

Send it with every request:
```javascript
axios.defaults.headers.common['Authorization'] = `Token ${localStorage.getItem('token')}`;
```

Check user role to show correct dashboard:
```javascript
if (user.role === 'ADMIN') {
    window.location.href = '/admin-dashboard.html';
} else {
    window.location.href = '/student-dashboard.html';
}
```
