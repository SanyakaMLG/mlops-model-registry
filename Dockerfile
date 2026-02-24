FROM python:3.10-slim

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir pdm

RUN pdm config python.use_venv false

COPY pyproject.toml pdm.lock* ./

RUN pdm install --prod --no-editable

COPY ./app ./app
COPY ./alembic ./alembic
COPY alembic.ini ./

EXPOSE 8000

CMD ["sh", "-c", "pdm run alembic upgrade head && pdm run uvicorn app.main:app --host 0.0.0.0 --port 8000"]