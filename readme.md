

# 🏗️ Cortts Real Estate Backend

This is the backend API for Cortts Real Estate, a property and client management SaaS platform for real estate companies. Built with FastAPI and SQLModel, it supports multi-role user management, property/project/unit tracking, payment scheduling, secure file storage, and push notifications.

---

## 🚀 Features

- **User & Role Management:** Admin, Agent (internal/external), and Client roles with RBAC and company association
- **Project & Unit Management:** CRUD, assignment, and audit tracking
- **Document Handling:** Upload/download of templates and signed files (Cloudflare R2)
- **Media File Uploads:** Support for media files with secure access and streaming downloads
- **Payment Tracking:** Flexible payment schedules, recalculation logic, and payment summaries
- **Notification System:** Expo Push, with multiple device tokens per user
- **Company Profiles:** Agents (internal/external) can be associated with companies
- **Audit & Soft-Delete:** Safe removal and change tracking for all major models
- **Pagination:** All list endpoints support paging for scalability

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, SQLModel, Pydantic
- **Database:** PostgreSQL
- **Object Storage:** Cloudflare R2 (S3-compatible)
- **Notifications:** Expo Push API
- **Authentication:** JWT with Role-based Access
- **Testing:** Pytest

---

## 📦 Project Structure

```
app/
  api/routes/         # FastAPI route handlers (users, units, payments, etc)
  auth/               # Auth dependencies and helpers
  core/               # Config and security utils
  db/                 # Database session and helpers
  models/             # SQLModel database models
  schemas/            # Pydantic schemas for API
  seed/               # Data seed scripts
  services/           # Business logic/services
  utility/            # Helper utilities (paging, deletion)
tests/                # Pytest-based test suite
alembic/              # DB migrations
uploaded_artworks/    # Uploaded media/files
tree.txt              # Project file tree
```

---

## ⚡️ Setup Instructions

1. **Clone the Repo**
   ```sh
   git clone https://github.com/your-org/cortts-backend.git
   cd cortts-backend
   ```

2. **Create a Virtual Environment**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Requirements**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   - Copy `.env.example` to `.env` and fill in required secrets (DB, Cloudflare R2, JWT, etc).
   - Email delivery supports two modes:
     - Local/dev: use Mailpit with `EMAIL_BACKEND=smtp`, `SMTP_HOST=localhost`, and `SMTP_PORT=1025`.
     - Production: keep `EMAIL_BACKEND=smtp` and configure real SMTP credentials so verification and reset emails are delivered to users.

5. **Run Database Migrations**
   ```sh
   make upgrade
   ```

6. **Seed Sample Data (Optional)**
   ```sh
   make seed-all
   ```

7. **Start the Server**
   ```sh
   make mail-dev-up
   make run
   # OR
   uvicorn app.main:app --reload
   ```

8. **API Docs**
   - Visit [http://localhost:8000/docs](http://localhost:8000/docs) for OpenAPI docs

---

## 🚦 Testing

- Run all tests:
  ```sh
  make test
  ```
- Add more test files in `tests/` as needed.

---

## ✉️ Email Delivery

The auth flow sends emails for:

- account verification after registration
- password reset requests

Supported configuration:

```env
EMAIL_ENABLED=true
EMAIL_BACKEND=smtp
EMAIL_FROM_EMAIL=no-reply@cortts.local
EMAIL_FROM_NAME=Cortts
EMAIL_EXPOSE_VERIFICATION_CODE=false

# Local Mailpit defaults
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=false
SMTP_USE_SSL=false
```

Notes:

- Local development can use Mailpit with `make mail-dev-up`, then view captured emails at `http://localhost:8025`.
- Production also uses `smtp`, but with your provider's host, port, credentials, and TLS settings.
- The API only returns the verification code from `/register` when `EMAIL_EXPOSE_VERIFICATION_CODE=true`.

---

## 🛡️ Security

- All API endpoints (except auth/register/login) require JWT authentication.
- Role-based access enforced via dependencies.
- Passwords are stored hashed (never plain-text).
- CORS restricted to allowed origins.
- File uploads are virus-scan ready (implement scan if needed for production).

---

## 📝 Contributing

Pull requests are welcome. Please open an issue first to discuss major changes.

---

## 📄 License

MIT or add your organization’s license.

---

## 🔒 Security Checklist

- [x] Passwords are hashed and never stored in plain text.
- [x] JWT authentication with role-based dependencies.
- [x] Secrets and credentials are stored in environment variables, not code.
- [x] CORS is restricted to allowed origins.
- [x] Pydantic schemas for validation; always validate user input.
- [x] Object ownership checks: users can only access their own data unless admin.
- [x] Soft-deletes are used for safe removals.
- [ ] File uploads should be virus-scanned before storage in production.
- [ ] Logging for critical user actions (optional/audit).
- [ ] No sensitive data is ever returned in error messages.
- [x] All endpoints require HTTPS in production.
- [x] No debug logs in production.

---

## 📧 Contact

For questions, email preciousidam@gmail.com or open an issue.
