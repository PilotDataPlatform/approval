FROM python:3.9-buster

WORKDIR /usr/src/app
RUN apt-get update && \
    apt-get install -y vim && \
    apt-get install -y less
RUN pip install --no-cache-dir poetry==1.1.12
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root --no-interaction
COPY . .
RUN chmod +x gunicorn_starter.sh

CMD ["python", "run.py"]
