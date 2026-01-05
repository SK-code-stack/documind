# DocuMind - AI-Powered PDF Chat Application

A Django REST API application that allows users to upload PDF documents and chat with them using AI. Users can ask questions about their documents and receive intelligent answers based on the document content.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Development Status](#development-status)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### Completed Features ✅

**User Authentication & Management:**
- ✅ Email-based user registration with OTP verification
- ✅ Secure JWT authentication (access + refresh tokens)
- ✅ Login with email and password
- ✅ Password change (with current password)
- ✅ Password reset (with OTP verification)
- ✅ User logout with token blacklisting
- ✅ Account deletion

**Document Management:**
- ✅ Upload PDF documents (max 10MB)
- ✅ List all user's documents
- ✅ View document details
- ✅ Delete documents
- ✅ Check document processing status
- ✅ File validation (PDF only)

**Security:**
- ✅ Password strength validation (min 8 chars, uppercase, lowercase, number, special char)
- ✅ OTP email verification (10-minute expiry, one-time use)
- ✅ JWT token authentication with refresh mechanism
- ✅ User can only access their own documents
- ✅ Secure file storage

### In Progress 🚧

**PDF Processing:**
- 🚧 Text extraction from PDFs
- 🚧 Text chunking and preprocessing
- 🚧 Vector embeddings generation
- 🚧 Storage in vector database

**AI Chat:**
- 🚧 Semantic search for relevant content
- 🚧 AI-powered question answering
- 🚧 Conversation history
- 🚧 Source citations

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.12
- Django 5.x
- Django REST Framework
- Django REST Framework SimpleJWT

**Database:**
- PostgreSQL (Production)
- SQLite (Development)

**AI/ML (Planned):**
- Google Gemini API (LLM)
- Sentence Transformers (Embeddings)
- ChromaDB (Vector Database)
- LangChain (Text Processing)

**File Processing:**
- PyPDF2 / pdfplumber

**Email:**
- SMTP (Gmail)

**Authentication:**
- JWT (JSON Web Tokens)

---

## 📁 Project Structure

```
documind/
├── accounts/                   # User authentication app
│   ├── models.py              # Custom User model with email login
│   ├── serializers.py         # User & OTP serializers
│   ├── views.py               # Auth endpoints (signup, login, logout, etc.)
│   ├── services.py            # Email & OTP services
│   ├── validators.py          # Password strength validation
│   └── urls.py                # Account routes
│
├── api/                        # Document & chat app
│   ├── models.py              # Document, DocumentChunk, ChatMessage models
│   ├── serializers.py         # Document & chat serializers
│   ├── views.py               # Document management endpoints
│   ├── services/              # Business logic (coming soon)
│   │   ├── pdf_service.py
│   │   ├── embedding_service.py
│   │   └── chat_service.py
│   └── urls.py                # API routes
│
├── media/                      # Uploaded files
│   └── documents/
│
├── documind/                   # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── .env                        # Environment variables (not in git)
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- Python 3.12+
- pip
- Virtual environment (recommended)
- PostgreSQL (optional, for production)

### Setup Steps

**1. Clone the repository:**

```bash
git clone https://github.com/yourusername/documind.git
cd documind
```

**2. Create virtual environment:**

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Create `.env` file:**

```bash
touch .env
```

Add the following variables:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (optional - uses SQLite by default)
DB_NAME=documind
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password

# JWT Settings
ACCESS_TOKEN_LIFETIME=60  # minutes
REFRESH_TOKEN_LIFETIME=30  # days

# AI API Keys (for future use)
GEMINI_API_KEY=your-gemini-api-key

# File Upload
MAX_FILE_SIZE=10485760  # 10MB in bytes
```

**5. Run migrations:**

```bash
python manage.py makemigrations
python manage.py migrate
```

**6. Create superuser:**

```bash
python manage.py createsuperuser
```

**7. Create media directory:**

```bash
mkdir -p media/documents
```

**8. Run development server:**

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

---

## ⚙️ Configuration

### Email Setup (Gmail)

1. Go to your Google Account settings
2. Enable 2-Step Verification
3. Generate App Password:
   - Visit: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other"
   - Name it "Django"
   - Copy the 16-character password
4. Add to `.env`:
   ```
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=abcdefghijklmnop
   ```

### Gemini API Setup (For AI features)

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Get API Key"
4. Copy your key to `.env`:
   ```
   GEMINI_API_KEY=your-key-here
   ```

---

## 📚 API Documentation

### Base URL
```
http://127.0.0.1:8000
```

### Authentication Endpoints

#### 1. Signup (Send OTP)
```http
POST /account/users/signup/
Content-Type: application/json

{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
}
```

**Response:**
```json
{
    "message": "OTP sent to your email. Please verify to complete signup.",
    "email": "user@example.com"
}
```

#### 2. Confirm Signup (Verify OTP)
```http
POST /account/users/confirm_signup/
Content-Type: application/json

{
    "email": "user@example.com",
    "otp": "123456",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
}
```

**Response:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1Q...",
    "access": "eyJ0eXAiOiJKV1Q...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

#### 3. Login
```http
POST /account/users/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePass123!"
}
```

**Response:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1Q...",
    "access": "eyJ0eXAiOiJKV1Q...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

#### 4. Logout
```http
POST /account/users/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1Q..."
}
```

#### 5. Change Password
```http
POST /account/users/change_password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "current_password": "OldPass123!",
    "new_password": "NewPass123!",
    "confirm_password": "NewPass123!"
}
```

#### 6. Change Password with OTP (Step 1: Send OTP)
```http
POST /account/users/change_password_otp/
Authorization: Bearer <access_token>
```

#### 7. Change Password with OTP (Step 2: Verify & Update)
```http
POST /account/users/confirm_pass_otp/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "otp_code": "123456",
    "new_password": "NewPass123!",
    "confirm_password": "NewPass123!"
}
```

#### 8. Delete Account
```http
POST /account/users/delete_account/
Authorization: Bearer <access_token>
```

#### 9. Refresh Token
```http
POST /token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1Q..."
}
```

---

### Document Endpoints

#### 1. Upload Document
```http
POST /api/documents/upload/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <PDF file>
```

**Response:**
```json
{
    "id": 1,
    "title": "my-document",
    "status": "pending",
    "message": "Document uploaded successfully"
}
```

#### 2. List Documents
```http
GET /api/documents/
Authorization: Bearer <access_token>
```

**Response:**
```json
[
    {
        "id": 1,
        "title": "document-1",
        "status": "completed",
        "page_count": 10,
        "chunk_count": 25,
        "is_ready": true,
        "uploaded_at": "2025-12-30T10:00:00Z"
    },
    {
        "id": 2,
        "title": "document-2",
        "status": "processing",
        "page_count": 5,
        "chunk_count": 0,
        "is_ready": false,
        "uploaded_at": "2025-12-30T11:00:00Z"
    }
]
```

#### 3. Get Document Details
```http
GET /api/documents/{id}/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "id": 1,
    "title": "my-document",
    "file": "/media/documents/2025/12/30/my-document.pdf",
    "file_size": 1024000,
    "page_count": 10,
    "status": "completed",
    "uploaded_at": "2025-12-30T10:00:00Z",
    "processed_at": "2025-12-30T10:05:00Z",
    "error_message": null,
    "chunk_count": 25,
    "is_ready": true,
    "user_email": "user@example.com"
}
```

#### 4. Get Document Status
```http
GET /api/documents/{id}/status/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "id": 1,
    "status": "completed",
    "error_message": null,
    "page_count": 10,
    "chunk_count": 25,
    "is_ready": true
}
```

#### 5. Delete Document
```http
DELETE /api/documents/{id}/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "message": "Document deleted successfully"
}
```

---

## 💡 Usage Examples

### Using cURL

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/account/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Upload Document:**
```bash
curl -X POST http://127.0.0.1:8000/api/documents/upload/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/document.pdf"
```

**List Documents:**
```bash
curl -X GET http://127.0.0.1:8000/api/documents/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Python Requests

```python
import requests

# Login
response = requests.post(
    'http://127.0.0.1:8000/account/users/login/',
    json={
        'email': 'user@example.com',
        'password': 'SecurePass123!'
    }
)
tokens = response.json()
access_token = tokens['access']

# Upload Document
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://127.0.0.1:8000/api/documents/upload/',
        headers={'Authorization': f'Bearer {access_token}'},
        files={'file': f}
    )
    print(response.json())

# List Documents
response = requests.get(
    'http://127.0.0.1:8000/api/documents/',
    headers={'Authorization': f'Bearer {access_token}'}
)
documents = response.json()
print(documents)
```

---

## 📊 Development Status

### Phase 1: User Authentication ✅ COMPLETED
- [x] User registration with OTP
- [x] Email verification
- [x] Login/Logout
- [x] Password management
- [x] JWT authentication
- [x] Token refresh & blacklisting

### Phase 2: Document Management ✅ COMPLETED
- [x] File upload
- [x] Document listing
- [x] Document deletion
- [x] Status tracking
- [x] File validation

### Phase 3: PDF Processing 🚧 IN PROGRESS
- [ ] Text extraction
- [ ] Text cleaning & preprocessing
- [ ] Text chunking
- [ ] Embedding generation
- [ ] Vector storage (ChromaDB)

### Phase 4: AI Chat 📅 PLANNED
- [ ] Semantic search
- [ ] Gemini API integration
- [ ] Question answering
- [ ] Conversation history
- [ ] Source citations

### Phase 5: Advanced Features 📅 PLANNED
- [ ] Background task processing (Celery)
- [ ] Real-time status updates (WebSocket)
- [ ] Multiple file formats (DOCX, TXT)
- [ ] Batch uploads
- [ ] Document sharing
- [ ] Export conversations

---

## 🧪 Testing

### Run Tests (Coming Soon)
```bash
pytest
```

### Manual Testing with Postman

1. Import the Postman collection (coming soon)
2. Set environment variables:
   - `base_url`: `http://127.0.0.1:8000`
   - `access_token`: (obtained after login)
3. Run requests in order:
   - Signup → Verify → Login → Upload → List → Delete

---

## 🔒 Security Features

- ✅ Password hashing (Django's PBKDF2)
- ✅ JWT authentication with expiry
- ✅ Token blacklisting on logout
- ✅ OTP-based email verification
- ✅ Password strength validation
- ✅ CORS protection
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection (Django templates)
- ✅ File type validation
- ✅ File size limits
- ✅ User-document access control

---

## 📝 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Django secret key | - | Yes |
| `DEBUG` | Debug mode | False | No |
| `EMAIL_USER` | Gmail address | - | Yes |
| `EMAIL_PASSWORD` | Gmail app password | - | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | - | Later |
| `MAX_FILE_SIZE` | Max upload size (bytes) | 10485760 | No |
| `ACCESS_TOKEN_LIFETIME` | JWT access token lifetime (min) | 60 | No |
| `REFRESH_TOKEN_LIFETIME` | JWT refresh token lifetime (days) | 30 | No |

---

## 🐛 Known Issues

- [ ] Email sending may be slow (synchronous)
- [ ] Large file uploads not tested
- [ ] No rate limiting yet
- [ ] No file preview functionality

---

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up HTTPS
- [ ] Use environment variables for secrets
- [ ] Set up static/media file serving (nginx)
- [ ] Configure CORS properly
- [ ] Set up logging
- [ ] Enable rate limiting
- [ ] Set up monitoring (Sentry)
- [ ] Configure backup system

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Django REST Framework documentation
- Google Gemini API
- Sentence Transformers
- ChromaDB team
- All contributors

---

## 📞 Support

For support, email support@documind.com or open an issue on GitHub.

---

## 🗺️ Roadmap

**Q1 2026:**
- Complete PDF processing pipeline
- Implement AI chat functionality
- Add conversation history

**Q2 2026:**
- Background task processing
- Real-time updates
- Mobile app (React Native)

**Q3 2026:**
- Advanced search features
- Document collaboration
- API rate limiting

**Q4 2026:**
- Multi-language support
- Voice input/output
- Analytics dashboard

---

**Built with ❤️ by the DocuMind Team**