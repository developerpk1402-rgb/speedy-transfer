# Speedy Transfers

A Django-based transfer booking application that allows users to book transportation services with integrated payment processing via Stripe and PayPal.

## Features

- **Transfer Booking System**: Book one-way and round-trip transfers
- **Multi-zone Support**: Different zones with hotels and destinations
- **Vehicle Catalog**: Various car types (Sedan, SUV, etc.) with capacity management
- **Payment Integration**: Support for Stripe and PayPal payments
- **Contact Management**: Customer inquiry and booking management
- **Admin Interface**: Django admin with Jet admin theme
- **Responsive Design**: Modern UI with Tailwind CSS
- **Email Notifications**: Automated email system for bookings

## Project Structure

```
speedy-transfer-main/
├── app/                    # Main Django app
├── config/                 # Django configuration
│   └── settings/          # Environment-specific settings
├── speedy_app/            # Core application
│   └── core/              # Main business logic
├── templates/             # HTML templates and static assets
│   └── assets/            # CSS, JS, images, and fonts
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
└── docker-compose.yml    # Docker configuration
```

## Prerequisites

- Python 3.8+
- Node.js 14+ (for frontend assets)
- MySQL or PostgreSQL database
- Git

## Environment Setup

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306

# Payment Configuration
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_SECRET=your_paypal_secret
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key

# Email Configuration
EMAIL_HOST=your_email_host
EMAIL_PORT=465
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_password
DEFAULT_FROM_EMAIL=your_from_email
```

---

# Platform-Specific Setup Instructions

## macOS Setup

### **1. Install Homebrew (if not already installed)**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### **2. Install Python and Dependencies**
```bash
# Install Python 3.11
brew install python@3.11

# Install MySQL (if using MySQL)
brew install mysql

# Start MySQL service
brew services start mysql

# Install Node.js for frontend assets
brew install node
```

### **3. Clone and Navigate to Project**
```bash
git clone <repository-url>
cd speedy-transfer-main
```

### **4. Create Virtual Environment**
```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### **5. Install Python Dependencies**
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### **6. Install Frontend Dependencies**
```bash
cd templates/assets
npm install
```

### **7. Database Setup**
```bash
# Create database (MySQL)
mysql -u root -p
CREATE DATABASE speedy_transfers;
exit

# Or create database (PostgreSQL)
createdb speedy_transfers
```

### **8. Django Setup**
```bash
# Make migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### **9. Build Frontend Assets**
```bash
cd templates/assets
npm run build
# or for development with watch mode
npm run watch
```

### **10. Run Development Server**
```bash
# In one terminal - run Django server
python manage.py runserver 0.0.0.0:8000

# In another terminal - run livereload (optional)
python manage.py livereload
```

### **11. Access the Application**
- Main application: http://localhost:8000
- Admin interface: http://localhost:8000/admin

---

## Linux (Ubuntu, Fedora, etc.)

### **1. Install Python and Virtual Environment Module**
```bash
# Check Python version
python3 --version

# Install Python and venv (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-venv python3-pip

# Install Python and venv (Fedora)
sudo dnf install python3 python3-venv python3-pip

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### **2. Install Database**
```bash
# MySQL (Ubuntu/Debian)
sudo apt install mysql-server mysql-client

# PostgreSQL (Ubuntu/Debian)
sudo apt install postgresql postgresql-contrib

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql
```

### **3. Create Virtual Environment**
```bash
# Navigate to project directory
cd speedy-transfer-main

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### **4. Install Dependencies**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd templates/assets
npm install
```

---

## Windows

### **1. Install Python**
- Download Python from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"
- Verify installation: `python --version`

### **2. Install Node.js**
- Download from [nodejs.org](https://nodejs.org/)
- Install with default settings

### **3. Install Database**
- **MySQL**: Download from [mysql.com](https://dev.mysql.com/downloads/)
- **PostgreSQL**: Download from [postgresql.org](https://www.postgresql.org/download/)

### **4. Create Virtual Environment**
```powershell
# Navigate to project directory
cd speedy-transfer-main

# Create virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
venv\Scripts\Activate

# Or for Command Prompt
venv\Scripts\activate.bat
```

### **5. Install Dependencies**
```powershell
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd templates/assets
npm install
```

---

## Development Commands

### **Database Management**
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access Django shell
python manage.py shell
```

### **Frontend Development**
```bash
# Build assets
cd templates/assets
npm run build

# Watch for changes (development)
npm run watch
```

### **Internationalization**
```bash
# Create translation files
django-admin makemessages -l en

# Compile translations
django-admin compilemessages --ignore apps
```

### **Development Server**
```bash
# Run Django server
python manage.py runserver 0.0.0.0:8000

# Run with livereload
python manage.py livereload
```

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d
```

## Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific test modules
python manage.py test speedy_app.core.tests_payment_integration
python manage.py test speedy_app.core.tests_payment_stripe
python manage.py test speedy_app.core.tests_payment_paypal
```

## Production Deployment

### **Environment Variables**
Ensure all production environment variables are properly set in your deployment environment.

### **Static Files**
```bash
python manage.py collectstatic --noinput
```

### **Database**
Use a production-ready database like PostgreSQL or MySQL with proper configuration.

### **Web Server**
Configure a WSGI server like Gunicorn:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Troubleshooting

### **Common Issues**

1. **Database Connection Issues**
   - Verify database credentials in `.env`
   - Ensure database service is running
   - Check database exists

2. **Payment Integration Issues**
   - Verify API keys in environment variables
   - Check webhook endpoints
   - Test with sandbox credentials first

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check `STATICFILES_DIRS` in settings
   - Verify web server configuration

4. **Frontend Assets Not Building**
   - Ensure Node.js is installed
   - Run `npm install` in `templates/assets`
   - Check for build errors in console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is proprietary software. All rights reserved.

---

## Ignoring Virtual Environment in Git

Add to `.gitignore`:
```
venv/
.env
*.pyc
__pycache__/
```

## Support

For technical support or questions, please contact the development team.#   S p e e d y  
 