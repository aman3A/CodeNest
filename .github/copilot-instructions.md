# Project instructions

- Project: The Practical Stack, a Django blog using Python, Django Templates, vanilla CSS/JavaScript, SQLite locally, and PostgreSQL through `DATABASE_URL` in production.
- Keep the initial scope focused on the `core` and `posts` apps. Do not add accounts, comments, bookmarks, or AI integrations unless requested.
- Public article queries must only return published posts.
- Run `python manage.py check` and `python manage.py test` after changes to Django behavior.
- Keep secrets in environment variables; do not commit `.env` or production credentials.
- Store locally uploaded media under `media/`; use durable object storage in production.
