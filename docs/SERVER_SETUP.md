# Server Setup & Installation

## Required Software

- Python 3
- MySQL server
- libmysqlclient ([download](https://dev.mysql.com/downloads/c-api/))
- (Optional) Python 3 `venv`

## Setup Steps

### 1. Clone and create virtual environment

```bash
git clone git@github.com:m-hollow/MysteryMovie.git
cd MysteryMovie
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Set up MySQL database

```sql
sudo mysql

CREATE DATABASE mmg_1;
CREATE USER 'mmg_user_a'@'localhost' IDENTIFIED BY 'mmg_password';
GRANT CREATE, ALTER, INSERT, UPDATE, DELETE, SELECT, REFERENCES, INDEX
  ON mmg_1.* TO 'mmg_user_a'@'localhost';
```

### 4. Configure environment

Create a `.env` file in the project root:

```env
SECRET_KEY=<generate with: python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'>
DEBUG=True
DB_NAME=mmg_1
DB_USER=mmg_user_a
DB_PASSWORD=mmg_password
```

### 5. Run migrations

```bash
python3 manage.py migrate --settings=mmg.settings.development
```

### 6. Create a superuser

```bash
python3 manage.py createsuperuser --settings=mmg.settings.development
```

### 7. Seed initial data

From the Django shell (`python3 manage.py shell --settings=mmg.settings.development`):

```python
from movies.utility_functions import create_ranks, add_trophies
create_ranks()    # Creates RoundRank entries (1st–10th)
add_trophies()    # Creates default Trophy entries
```

### 8. Run the development server

```bash
python3 manage.py runserver --settings=mmg.settings.development
```

Visit `http://localhost:8000/` — you'll be redirected to the login page.

## Automated Setup

For steps 1–5 and 7–8, you can use the setup script:

```bash
scripts/server_setup.sh
```

This script handles cloning, venv creation, dependency installation, `.env` generation, MySQL database/user creation, migrations, data seeding, and starting the dev server. Step 6 (superuser creation) requires interactive input and must be run manually.
