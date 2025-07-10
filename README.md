## 🟩 `README.md` for WorkNest Backend (Django + DRF)

```markdown
# WorkNest Backend

**WorkNest** is a Django REST Framework backend that powers a service marketplace platform where users can find, book, and review verified workers. The backend handles user authentication, role-based access, appointment booking, ticket lifecycle management, and admin workflows.

---

## 🔑 Core Features

- Custom `CustomUser` model with support for roles: `user`, `worker`, `admin`
- JWT-based authentication using `SimpleJWT`
- Worker verification process with document upload (PDF)
- Multi-stage ticket system:
  - requested → accepted → in-progress → completed → paid → reviewed
- Ratings and Reviews model for post-payment feedback
- Admin panel to approve or reject worker registrations
- Geolocation & distance-based worker sorting support

---
## 🛠 Technologies

- Python 3.x
- Django 4.x
- Django REST Framework
- Simple JWT
- PostgreSQL (or SQLite for dev)
- CORS headers
- File upload support via Django’s `FileField` and `ImageField`

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/WorkNest-Backend.git
cd WorkNest-Backend
### 2️⃣ Set Up Virtual Environment
python -m venv env
source env/bin/activate   # On Windows: env\Scripts\activate
### 3️⃣ Install Requirements
pip install -r requirements.txt

### 4️⃣ Run Migrations
python manage.py makemigrations
python manage.py migrate

### 5️⃣ Create Superuser (Admin Panel)
python manage.py createsuperuser

### 6️⃣ Start the Server
python manage.py runserver
