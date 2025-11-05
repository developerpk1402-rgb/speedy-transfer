# Speedy Transfer - Project Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm 8+
- MySQL (optional, falls back to SQLite for development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd speedy-transfer-main
```

### 2. Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Node.js Dependencies
```bash
# Install frontend dependencies
npm run install-deps

# Build CSS (one-time)
npm run build-css

# Watch CSS changes (development)
npm run build-css
```

### 4. Database Setup
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
# Start Django server
npm run dev
# or
python manage.py runserver

# In another terminal, watch CSS changes
npm run build-css
```

## 📁 Project Structure

```
speedy-transfer-main/
├── config/                 # Django project settings
│   ├── settings/
│   │   ├── settings.py    # Base settings
│   │   ├── develop.py     # Development settings
│   │   └── test.py        # Test settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── speedy_app/            # Main Django app
│   └── core/              # Core functionality
│       ├── models.py      # Database models
│       ├── views.py       # View logic
│       ├── urls.py        # App URL routing
│       └── admin.py       # Admin interface
├── templates/              # HTML templates
│   └── assets/            # Frontend assets
│       ├── src/           # Source CSS/JS
│       ├── package.json   # Node.js dependencies
│       └── tailwind.config.js
├── manage.py              # Django management
├── package.json           # Project scripts
└── requirements.txt       # Python dependencies
```

## 🔧 Available Commands

### Django Commands
```bash
npm run dev              # Start development server
npm run test             # Run tests
npm run migrate          # Apply database migrations
npm run makemigrations  # Create new migrations
npm run shell           # Open Django shell
npm run collectstatic   # Collect static files
```

### Frontend Commands
```bash
npm run build-css        # Build CSS once
npm run install-deps     # Install Node.js dependencies
```

## 🗄️ Database Configuration

The project automatically detects available databases:

1. **MySQL** (if `mysqlclient` is installed)
2. **SQLite** (fallback for development)

### Environment Variables (.env file)
```bash
# Database
DB_NAME=speedy
DB_USER=speedy_user
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306

# Payment APIs
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_SECRET=your_paypal_secret
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key

# Email
EMAIL_HOST=65.99.252.200
EMAIL_PORT=465
EMAIL_HOST_USER=soporte@vittapp.com
EMAIL_HOST_PASSWORD=your_email_password
```

## 🎨 Frontend Development

### Tailwind CSS
- **Input**: `templates/assets/src/input.css`
- **Output**: `templates/assets/src/output.css`
- **Config**: `templates/assets/tailwind.config.js`

### Building CSS
```bash
# Development (watch mode)
npm run build-css

# Production
cd templates/assets
npx tailwindcss -i ./src/input.css -o ./src/output.css --minify
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test speedy_app.core.tests

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Deployment

### Production Settings
1. Set `DEBUG = False` in production settings
2. Configure production database
3. Set up proper static file serving
4. Configure environment variables
5. Use production WSGI server (Gunicorn)

### Docker (if available)
```bash
docker-compose up -d
```

## 🔍 Troubleshooting

### Common Issues

1. **ImportError: CarType**
   - Ensure all models are properly defined
   - Check for circular imports

2. **Database Connection Issues**
   - Verify database credentials
   - Check if MySQL service is running
   - Project will fall back to SQLite if MySQL unavailable

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_URL` and `STATIC_ROOT` settings

4. **CSS Not Building**
   - Ensure Node.js dependencies are installed
   - Check Tailwind configuration
   - Verify input.css exists

### Reset Database
```bash
# Remove database and migrations
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue
Remove-Item speedy_app\core\migrations\*.py -Exclude __init__.py

# Recreate
python manage.py makemigrations
python manage.py migrate
```

## 📞 Support

For issues related to:
- **Django/Backend**: Check Django logs and error messages
- **Frontend/CSS**: Verify Node.js setup and Tailwind configuration
- **Database**: Check connection settings and migrations
- **Payments**: Verify API keys and environment variables

## 🎯 Next Steps

1. Set up environment variables
2. Configure payment API keys
3. Set up email backend
4. Customize templates and styling
5. Add test data
6. Configure production settings




