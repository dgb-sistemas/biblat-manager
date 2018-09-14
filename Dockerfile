FROM python:3.5-alpine

ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=biblat_manager.app

# Build-time metadata as defined at http://label-schema.org
ARG BIBLAT_MANAGER_BUILD_DATE
ARG BIBLAT_MANAGER_VCS_REF
ARG BIBLAT_MANAGER_WEBAPP_VERSION

ENV BIBLAT_MANAGER_BUILD_DATE ${BIBLAT_MANAGER_BUILD_DATE}
ENV BIBLAT_MANAGER_VCS_REF ${BIBLAT_MANAGER_VCS_REF}
ENV BIBLAT_MANAGER_WEBAPP_VERSION ${BIBLAT_MANAGER_WEBAPP_VERSION}

LABEL org.label-schema.build-date=$BIBLAT_MANAGER_BUILD_DATE \
      org.label-schema.name="Biblat Manager WebApp - development build" \
      org.label-schema.description="Biblat Manager main app" \
      org.label-schema.url="https://github.com/dgb-sistemas/biblat-manager/" \
      org.label-schema.vcs-ref=$BIBLAT_MANAGER_VCS_REF \
      org.label-schema.vcs-url="https://github.com/dgb-sistemas/biblat-manager/" \
      org.label-schema.vendor="DGB - Sistemas" \
      org.label-schema.version=$BIBLAT_MANAGER_WEBAPP_VERSION \
      org.label-schema.schema-version="1.0"

RUN apk --update add --no-cache \
    git gcc build-base zlib-dev jpeg-dev curl

COPY . /app
WORKDIR /app

RUN pip --no-cache-dir install -r requirements.txt

RUN flask compile_messages
RUN chown -R nobody:nogroup /app
VOLUME /app/data
USER nobody
EXPOSE 8000

HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost:8000/ || exit 1

CMD gunicorn --workers 3 --bind 0.0.0.0:8000 app:app --chdir=$PWD/biblat_manager --timeout 150 --log-level INFO
