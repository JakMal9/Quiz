FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update -y \
    && apt-get install -y \
    gcc libc-dev musl-dev  libpq-dev wait-for-it \
    && apt-get autoremove


RUN mkdir /quiz_app
WORKDIR /quiz_app
COPY ./quiz_app /quiz_app
COPY Pipfile Pipfile.lock ./

RUN pip install --upgrade pip \
    && pip install pipenv==v2022.6.7 \
    && pipenv install --dev --system --deploy --verbose

COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]