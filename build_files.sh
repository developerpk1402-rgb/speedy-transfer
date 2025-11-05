#!/bin/bash

# Exit on error
set -e

echo "Python version:"
python --version

# Upgrade pip
python -m pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist and copy production settings
if [ ! -f .env ]; then
    cp vercel.env .env
fi

# Ensure static directories exist
mkdir -p staticfiles

# Collect static files with --noinput flag
echo "Collecting static files..."
python manage.py collectstatic --noinput
mkdir -p staticfiles
mkdir -p static

# Set production settings
export DJANGO_SETTINGS_MODULE=config.settings.production

# Initialize PyMySQL
python -c "import pymysql; pymysql.install_as_MySQLdb()"

# Collect static files with --clear to ensure clean collection
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run migrations if database is configured
if [ -n "$DB_HOST" ] && [ -n "$DB_NAME" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
fi

# Copy static files to the root static directory for direct access
cp -r staticfiles/* static/ || true