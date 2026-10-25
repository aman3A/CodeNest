# The Practical Stack

A Django publication starter for practical Python, software engineering, and AI articles. It currently includes public article pages, categories and tags, Django admin publishing with a rich-text post editor, and responsive server-rendered templates. Article HTML is sanitized before saving and rendering.

## Requirements

- Python 3.12 or newer
- pip

## Local setup (Windows PowerShell)

1. Create and activate a virtual environment: `python -m venv .venv` then `.venv\Scripts\Activate.ps1`.
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. (Optional) Copy `.env.example` to `.env` and set a local `SECRET_KEY`. Django does not load `.env` automatically; export values in PowerShell or use your preferred environment-variable manager.
4. Create the local database: `python manage.py migrate`.
5. Create an admin account: `python manage.py createsuperuser`.
6. Start the development server: `python manage.py runserver`.
7. Open `http://127.0.0.1:8000/` for the site and `/admin/` to add categories and posts. Set a post's status to Published to show it publicly.

Local development uses SQLite and stores uploaded covers under `media/`. Public pages only expose published posts. In the admin post editor, use the formatting toolbar for headings, emphasis, lists, quotes, and links. The built-in Django login page is at `/accounts/login/`.

## Checks

Run the automated tests with `python manage.py test`. Run Django's configuration checks with `python manage.py check`.

## Deployment notes

Set `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, and a PostgreSQL `DATABASE_URL` in the hosting provider's environment settings. Run `python manage.py migrate` as a controlled release step and `python manage.py collectstatic --no-input` before serving. WhiteNoise serves collected static assets. The application filesystem may be ephemeral on cloud hosts, so configure durable object storage for uploaded media before accepting production image uploads. `build.sh` provides a basic build command; review the host's recommended release workflow before using it unchanged.
