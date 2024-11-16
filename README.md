# MysteryMovie

Project for Mystery Movie voting and tracking.

## Required software

- Python 3
- MySQL server
- libmysqlclient (https://dev.mysql.com/downloads/c-api/)
- (Optional) Python 3 `venv`

## Install and run

- (Optional) Make a new venv: `python3 -m venv .venv`
    - Activate with: `source .env/bin/activate`
- Install requirements: `pip3 install requirements.txt`
- Generate and set `.env` in settings:
     - `SECRET_KEY` should be `python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
     - `DB_NAME`, `DB_USER`, `DB_PASSWORD` can be set to whatever your MySQL setup is, like
     ```
     sudo mysql

     mysql> CREATE DATABASE mmg_1;
     mysql> CREATE USER 'mmg_user_a'@'localhost' IDENTIFIED BY 'mmg_password';
     mysql> GRANT CREATE, ALTER, INSERT, UPDATE, DELETE, SELECT, REFERENCES, INDEX ON mmg_1.* TO 'mmg_user_a'@'localhost';
     Query OK, 0 rows affected (0.00 sec)
     ```
    - would result in the fields in the `.env` being:
    ```
    DB_NAME=mmg_1
    DB_USER=mmg_user_a
    DB_PASSWORD=mmg_password
    ```
- Run initial migrations: `python3 manage.py migrate --settings=mmg.settings.development`

