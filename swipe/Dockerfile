FROM python:3.9.4-alpine

WORKDIR /usr/src/project

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create the app user
RUN addgroup -S project && adduser -S project -G project

ENV HOME=/home
ENV APP_HOME=/home/api
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media
WORKDIR $APP_HOME

RUN chown -R project:project $APP_HOME

RUN apk add --update --no-cache tiff-dev jpeg-dev openjpeg-dev zlib-dev freetype-dev lcms2-dev \
libwebp-dev tcl-dev tk-dev harfbuzz-dev fribidi-dev libimagequant-dev libxcb-dev libpng-dev \
gcc build-base freetype-dev libpng-dev openblas-dev postgresql-dev python3-dev musl-dev

RUN pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
RUN pip3 install --no-cache-dir  --force-reinstall -Iv grpcio==1.38.1
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
