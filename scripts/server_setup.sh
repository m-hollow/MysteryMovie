#!/usr/bin/env bash
set -euo pipefail

# Mystery Movie Club - Development Server Setup
# Automates steps from docs/SERVER_SETUP.md
# Note: "createsuperuser" is interactive and must be run manually afterward.

SETTINGS="mmg.settings.development"
DB_NAME="mmg_1"
DB_USER="mmg_user_a"
DB_PASSWORD="mmg_password"

cd "$(dirname "$0")/.."
PROJECT_ROOT="$(pwd)"

echo "==> Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "==> Installing dependencies..."
pip3 install -r requirements.txt

echo "==> Generating .env file..."
if [ -f .env ]; then
    echo "    .env already exists, skipping (delete it first to regenerate)"
else
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    cat > .env <<EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=True
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
EOF
    echo "    .env created"
fi

echo "==> Setting up MySQL database..."
echo "    This requires MySQL root access (you may be prompted for your password)."
sudo mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME};
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT CREATE, ALTER, INSERT, UPDATE, DELETE, SELECT, REFERENCES, INDEX
  ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "==> Running migrations..."
python3 manage.py migrate --settings="${SETTINGS}"

echo "==> Seeding initial data (ranks and trophies)..."
python3 manage.py shell --settings="${SETTINGS}" <<EOF
from movies.utility_functions import create_ranks, add_trophies
create_ranks()
add_trophies()
print("Seed data created successfully")
EOF

echo ""
echo "==> Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Create a superuser (interactive):"
echo "     python3 manage.py createsuperuser --settings=${SETTINGS}"
echo ""
echo "  2. Start the dev server:"
echo "     python3 manage.py runserver --settings=${SETTINGS}"
echo ""
echo "  Then visit http://localhost:8000/"
