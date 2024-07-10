FROM python:3.8

WORKDIR /app

COPY gatherer/requirements.txt requirements.txt
COPY gatherer/*.py .
COPY *.py .

# Create /aforo folder
RUN mkdir aforo

# dont write pyc files
# dont buffer to stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# dependencies
RUN pip install -r requirements.txt \
    && rm -rf /root/.cache/pip