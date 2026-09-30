# Deployment note

This project is a Python Flask application with server-side rendering and SQLite.

It is **not a static site**, so it should not be uploaded to Netlify as a normal drag-and-drop site. Netlify's current Functions workflow is intended for supported serverless runtimes and this Flask app would require a substantial rewrite into Netlify Functions plus a different database architecture.

## Recommended deployment for this exact project

Use a Python-compatible web host such as Render or Railway.

### Start command
```text
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
```

### Important database note
The application currently uses `study_hub.db` (SQLite). SQLite is suitable for development/demo deployment, but a production multi-user deployment should use a persistent database such as PostgreSQL. A persistent disk may also be needed if SQLite must remain the database.

### Secret key
Set the `SECRET_KEY` environment variable in the hosting dashboard. The application already reads it from the environment.
