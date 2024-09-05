
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev musl-dev curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.4.0
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY pyproject.toml /app/
# COPY poetry.lock /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . /app/

WORKDIR /app/Parking_Service/parking_system


RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "parking_system.wsgi:application", "--bind", "0.0.0.0:8000"]

