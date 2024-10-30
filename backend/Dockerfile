FROM python:3.9-slim

# python envs
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        python3-dev \
        graphviz \
        graphviz-dev \
        libgraphviz-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# python dependencies
COPY ./requirements.txt /
RUN pip install --upgrade pip && pip install -r /requirements.txt

# upload scripts
COPY ./scripts/entrypoint.sh ./scripts/start.sh ./scripts/gunicorn.sh /

# Fix windows docker bug, convert CRLF to LF
RUN sed -i 's/\r$//g' /start.sh && chmod +x /start.sh && sed -i 's/\r$//g' /entrypoint.sh && chmod +x /entrypoint.sh &&\
    sed -i 's/\r$//g' /gunicorn.sh && chmod +x /gunicorn.sh

WORKDIR /app
