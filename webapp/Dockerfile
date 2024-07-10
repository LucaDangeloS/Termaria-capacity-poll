FROM python:3.8

WORKDIR /app

COPY webapp/requirements.txt requirements.txt
RUN mkdir webapp
COPY webapp ./webapp
COPY .streamlit ./webapp/
# copy wheel files
COPY webapp/*.whl .
COPY *.py ./webapp/

# Create /aforo folder
RUN mkdir aforo

# dont write pyc files
# dont buffer to stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt \
    && rm -rf /root/.cache/pip

EXPOSE 8501