FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update -y \
    && apt-get install -y \
    gcc libc-dev musl-dev  libpq-dev \
    && apt-get autoremove


RUN mkdir /quiz_app
WORKDIR /quiz_app
COPY ./quiz_app /quiz_app

RUN pip install --upgrade pip \
    && pip install poetry==1.1.13

COPY docker-entrypoint.sh poetry.lock pyproject.toml /

RUN chmod +x /docker-entrypoint.sh
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi
