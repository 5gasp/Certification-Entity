FROM python:3.8-bullseye

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    apache2 \
    apache2-dev \
    build-essential \
    gcc \
    pango1.0-tools

COPY requirements.txt /usr/src/app/
RUN pip3 install --no-cache-dir -r requirements.txt

RUN (getent group apache || groupadd apache) && useradd -m worker -p worker && usermod -a -G apache worker
RUN chown worker:apache /usr/src/app

COPY --chown=worker:apache . /usr/src/app

EXPOSE 8080
EXPOSE 8443

ENTRYPOINT ["mod_wsgi-express", "start-server", "wsgi.py", \
    "--user", "worker", "--group", "apache", \
    "--port", "8080", \
    "--https-port", "8443" \
]

CMD ["--processes", "4"]
