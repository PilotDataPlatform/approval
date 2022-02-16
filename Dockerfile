FROM python:3.9-buster

ARG pip_username
ARG pip_password

WORKDIR /usr/src/app
RUN apt-get update && \
    apt-get install -y vim && \
    apt-get install -y less
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN PIP_USERNAME=$pip_username PIP_PASSWORD=$pip_password pip install --no-cache-dir -r internal_requirements.txt
RUN chmod +x gunicorn_starter.sh
CMD ["python", "run.py"]
