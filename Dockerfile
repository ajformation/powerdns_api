# For more information, please refer to https://aka.ms/vscode-docker-python
#FROM python:3.13-slim
FROM alpine

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV ZONE="example.net"
ENV PORT="5000"

RUN adduser -u 5678 --disabled-password --gecos "" --home /app appuser 

RUN apk update && \
    apk add --no-cache \
    python3 \
    python3-dev \
    py3-pip

WORKDIR /app

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt --break-system-packages

COPY . /app

RUN chown -R appuser /app

EXPOSE ${PORT}/tcp

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["python", "webapp.py"]
# gunicorn --bind "[::]:5000" --reload webapp:app
CMD ["/bin/sh", "-c", "gunicorn --bind [::]:${PORT} --reload webapp:app"]
#CMD gunicorn --bind "[::]":${PORT} --reload webapp:app
