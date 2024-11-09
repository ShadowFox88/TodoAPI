FROM python:3.12.5-slim AS base

# Set enviroment variables

# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1 
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1 

WORKDIR /todoapi

# Install dependencies
COPY requirements.txt /todoapi/

RUN pip install --upgrade -r /todoapi/requirements.txt

# Copy project files
COPY . /todoapi/

# Run the application
ENTRYPOINT [ "/todoapi/start-server.sh" ]