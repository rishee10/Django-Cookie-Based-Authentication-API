# Django Cookie-Based Authentication API

A secure authentication system built with **Django**, **Django REST Framework (DRF)**, and **Swagger (drf-yasg)**. It uses **cookie-based token authentication** with CSRF protection, OTP email verification, and fully documented REST APIs.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Environment Configuration](#environment-configuration)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [How It Works — Full Flow](#how-it-works--full-flow)
- [Testing the API](#testing-the-api)
- [Security Details](#security-details)
- [Bonus Frontend](#bonus-frontend)
- [Common Errors & Fixes](#common-errors--fixes)

---

## Features

- User Registration with OTP email verification
- Secure login using HTTP-only cookie-based token auth
- Protected endpoints (accessible only after login)
- Auto CSRF token generation via Swagger UI
- Logout with server-side token invalidation
- Swagger UI for interactive API testing
- Bonus HTML + JS frontend for testing auth flow

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Django 4.2+ | Web framework |
| Django REST Framework | API development |
| drf-yasg | Swagger / OpenAPI documentation |
| django-cors-headers | CORS handling |
| rest_framework.authtoken | Token generation & management |
| Django Email Backend | OTP delivery (console in dev) |

---

## Project Structure

```
myproject/
├── myproject/
│   ├── __init__.py
│   ├── settings.py          ← configured with DRF, auth, CORS, cookies
│   ├── urls.py              ← includes API routes + Swagger + frontend
│   └── wsgi.py
│
├── authentication/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py            ← Custom User model + OTP model
│   ├── serializers.py       ← Input validation for all endpoints
│   ├── views.py             ← API logic (register, verify, login, me, logout)
│   ├── urls.py              ← URL routing for authentication app
│   ├── authentication.py    ← Custom cookie-based token authentication
│   └── utils.py             ← OTP generation and email sending
│
├── templates/
│   └── index.html           ← Bonus: simple HTML/JS frontend
│
├── requirements.txt
└── README.md
```

---

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Create and Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser (optional, for Django admin)

```bash
python manage.py createsuperuser
```

---

## Environment Configuration

In `myproject/settings.py`, the following are pre-configured:

```python
# Cookie settings
AUTH_COOKIE_NAME     = 'auth_token'
AUTH_COOKIE_HTTPONLY = True    # JS cannot read this cookie
AUTH_COOKIE_SECURE   = False   # Set True in production (requires HTTPS)
AUTH_COOKIE_SAMESITE = 'Lax'

# Email — prints to console in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production email (Gmail example):
# EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST         = 'smtp.gmail.com'
# EMAIL_PORT         = 587
# EMAIL_USE_TLS      = True
# EMAIL_HOST_USER    = 'your@gmail.com'
# EMAIL_HOST_PASSWORD = 'your_app_password'
```

---

## Running the Server

```bash
python manage.py runserver
```

Server starts at: `http://127.0.0.1:8000/`

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/` | Bonus frontend (HTML) |
| `http://127.0.0.1:8000/swagger/` | Swagger UI (API docs + testing) |
| `http://127.0.0.1:8000/admin/` | Django admin panel |

---

## API Endpoints

### `POST /api/register/`
Registers a new user and sends an OTP to the provided email.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Success Response (201):**
```json
{
  "message": "OTP sent to your email. Please verify to complete registration."
}
```

---

### `POST /api/register/verify`
Verifies the OTP and activates the user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "706586"
}
```

**Success Response (200):**
```json
{
  "message": "Email verified. You can now log in."
}
```

**Error Responses:**
```json
{ "error": "Invalid OTP." }
{ "error": "OTP has expired. Please register again." }
{ "error": "No pending registration found for this email." }
```

---

### `POST /api/login/`
Authenticates the user and sets an HTTP-only `auth_token` cookie.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Success Response (200):**
```json
{
  "message": "Login successful."
}
```
> The response also sets a `Set-Cookie: auth_token=...` header (HttpOnly).

**Error Responses:**
```json
{ "error": "Invalid credentials." }
{ "error": "Account not verified. Please verify your email." }
```

---

### `GET /api/me/`
Returns the authenticated user's details. Requires valid `auth_token` cookie.

**Success Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2026-05-26T07:41:39Z"
}
```

**Error Response (401 — not logged in):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### `POST /api/logout/`
Deletes the server-side token and clears the `auth_token` cookie.

**Success Response (200):**
```json
{
  "message": "Logged out successfully."
}
```

---

## How It Works — Full Flow

```
1. REGISTER  →  User created (inactive) + OTP saved in DB + email sent
                         ↓
2. VERIFY OTP  →  OTP matched + User activated (is_active=True) + OTP deleted
                         ↓
3. LOGIN  →  Password verified + Token created in DB + auth_token cookie set in browser
                         ↓
4. /api/me/  →  Browser sends cookie automatically → Django reads cookie
                → Finds token in DB → Identifies user → Returns user data
                         ↓
5. LOGOUT  →  Token deleted from DB + auth_token cookie cleared from browser
                         ↓
6. Any request after logout → 401 Unauthorized (no cookie, no token)
```

### OTP Expiry
OTPs are valid for **10 minutes**. After expiry, the user must register again. Previous incomplete registrations are automatically cleaned up on re-registration.

### Token Authentication Flow
Every protected request goes through `CookieTokenAuthentication`:
1. Reads `auth_token` from cookies (not Authorization header)
2. Looks up the token in the `authtoken_token` DB table
3. If found and user is active → allows access
4. If missing or invalid → returns 401

---

## Testing the API

### Option 1: Swagger UI (Recommended)

1. Open `http://127.0.0.1:8000/swagger/`
2. The CSRF token is **automatically set** as a cookie when Swagger loads
3. Click on any endpoint → **Try it out** → fill in the body → **Execute**
4. Test in order: Register → Verify OTP → Login → Me → Logout

> Note: Check the terminal/console for the OTP code when using the dev email backend.

### Option 2: Bonus HTML Frontend

1. Open `http://127.0.0.1:8000/`
2. Use the form to register, verify OTP, login, get details, and logout
3. Responses appear in the output box at the bottom

### Option 3: curl

```bash
# Register
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'

# Verify OTP (replace 123456 with OTP from console)
curl -X POST http://127.0.0.1:8000/api/register/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "otp": "123456"}'

# Login (saves cookie to cookie.txt)
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <your-csrf-token>" \
  -c cookie.txt \
  -d '{"email": "test@example.com", "password": "test123"}'

# Get user details (sends saved cookie)
curl -X GET http://127.0.0.1:8000/api/me/ \
  -b cookie.txt

# Logout
curl -X POST http://127.0.0.1:8000/api/logout/ \
  -b cookie.txt \
  -H "X-CSRFToken: <your-csrf-token>"
```

---

## Security Details

| Security Feature | Implementation |
|---|---|
| Password hashing | Django's built-in PBKDF2 hasher |
| HTTP-only cookie | `auth_token` cookie not accessible via JavaScript |
| CSRF protection | All mutating requests require `X-CSRFToken` header |
| Auto CSRF on Swagger | Opening `/swagger/` sets `csrftoken` cookie automatically |
| OTP expiry | OTPs expire after 10 minutes |
| Token invalidation | Logout deletes token from DB (not just from browser) |
| Inactive user block | Unverified users cannot log in |

---

## Bonus Frontend

A simple HTML + JavaScript page is available at `http://127.0.0.1:8000/` that lets you:
- Register a new user
- Enter and verify OTP
- Login
- View your user details
- Logout

It automatically reads the `csrftoken` cookie and includes it in every request header, mirroring how a real frontend would work.

---

## Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| `Token has no attribute 'objects'` | `rest_framework.authtoken` missing from `INSTALLED_APPS` | Add it and run `python manage.py migrate` |
| `CSRF token missing or incorrect` | Request sent without CSRF token | Open `/swagger/` first to get the cookie, then test |
| `401 Unauthorized` on `/api/me/` | Not logged in or cookie missing | Call `/api/login/` first |
| `OTP has expired` | More than 10 minutes passed | Register again with the same email |
| `Email already registered` | Active account exists for that email | Use login instead, or a different email |
| `Invalid credentials` | Wrong email or password | Check email and password |

---

## Requirements

```
Django>=4.2
djangorestframework
drf-yasg
django-cors-headers
```

Install with:
```bash
pip install -r requirements.txt
```

---

## Repository Checklist

- [x] `README.md` with full setup and usage instructions
- [x] `requirements.txt` with all dependencies
- [x] Clean commit history tracking feature-by-feature progress
- [x] All API endpoints implemented and tested
- [x] Swagger UI with automatic CSRF token generation
- [x] Cookie-based authentication (no Authorization headers)
- [x] OTP email verification flow
- [x] Bonus HTML frontend

---

*Built as part of a Django API Implementation Assignment evaluating authentication, API documentation, and security best practices.*