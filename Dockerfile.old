FROM python:3.6.5-alpine3.7
ENV PYTHONUNBUFFERED 1

RUN apk add --update \
    bash \
    gcc \
    musl-dev \
    mariadb-dev \
    libffi-dev \
    build-base pango-dev cairo-dev cairo cairo-tools \
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
  && rm -rf /var/cache/apk/*

ENV LIBRARY_PATH=/lib:/usr/lib
RUN pip install --upgrade pip
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install -r /app/requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh