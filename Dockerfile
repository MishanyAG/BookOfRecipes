FROM python:3.12.3-alpine as requirements-stage

WORKDIR /temp

RUN pip install poetry

COPY pyproject.toml poetry.lock* /temp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without=dev


FROM python:3.12.3-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY --from=requirements-stage /temp/requirements.txt /requirements.txt

RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY alembic.ini /code/alembic.ini
COPY entrypoint.sh /code/entrypoint.sh
COPY app /code/app
RUN chmod a+x /code/entrypoint.sh

WORKDIR /code

ENTRYPOINT [ "/code/entrypoint.sh" ]
