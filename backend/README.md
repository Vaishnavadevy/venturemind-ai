# Backend

FastAPI service organized around API, service, repository, and model layers.

## Run locally

Install Python 3.11+ and a dependency manager, then install this project's package and start the development server:

```powershell
cd backend
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload
```

The API documentation is served at `/docs`; the first health endpoint is `GET /api/v1/health`.

## Database migrations

Set `DATABASE_URL` in `.env`, then run `alembic upgrade head` from this directory. The normalized initial schema is in `alembic/versions/20260712_0001_initial_schema.py`.
