# 5GASP Certification Entity

## Overview
The 5GASP Certification Entity calculates the certificate grade and creates a certificate for a testing.  
The two main functions are creating a certificate and offering download of the certificate PDF file. Only pre-defined
users can create certificates, while anyone with a download URL can download the certificate. 

This server uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask.  
mod_wsgi is used as WSGI server for the Flask app.

## Adding API users

The endpoint to create certificates is protected by basic authentication. To add users, add an entry to the dictionary
`users` in the file `constants.py`.  
If the server is running, restart it to apply the change.

## Installing on the system

### Requirements
Python 3.8+  
Pango 1.44+  
Apache2 2.4+

Install the requirements with: (For Apache2, a compiler and development headers are required.)
```commandline
apt install pango1.0-tools apache2 apache2-dev gcc build-essential
```

Create a virtual environment and install the dependencies:  
In the root directory, run:
```commandline
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Start the server

The Certification Entity relies on a Redis instance to store certificates-related infromation. Thus, you have to run a redis docker image before starting the server:

```bash
docker run -d -p 6379:6379 --name redis -e ALLOW_EMPTY_PASSWORD=yes bitnami/redis:6.2.12
```

Fruthermore, you'll also need to create some env. variables to map redis' location:

```bash
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379
```

#### HTTPS
Provide the hostname and server certificate files in the command, then run it from the root directory
(`--processes` could be twice the number of CPUs):

```bash
mod_wsgi-express start-server wsgi.py --processes 4 --port 8080 \
    --https-only --https-port=8443 --server-name=<HOSTNAME> \
    --ssl-certificate-file='<ABSOLUTE PATH>' \
    --ssl-certificate-key-file='<ABSOLUTE PATH>'
```

#### HTTP

In the root directory, run (`--processes` could be twice the number of CPUs):
```bash
mod_wsgi-express start-server wsgi.py --processes 4 --port 8080
```

#### Additional Configuration

If the server is running behind a reverse proxy, you may need to perform some additional configurations, as to make sure the url through which the certificate will become available corresponds to your reverse proxy.
To do this, you may rely on the `API_CERTIFICATE_ENDPOINT` environment variable. E.g.:

```bash
export API_CERTIFICATE_ENDPOINT=https://ci-cd-service.5gasp.eu/certification-entity/certificate
```

After exporting this variable, you'll need to relaunch the server.
This env. variable can also be used with the docker image.


## Running with Docker

To run the server on a Docker container, execute the following from the root directory:

For HTTP:
```bash
# building the image
docker build -t cert_entity .

# starting up a container for HTTP
docker run -d --name cert_entity -p 8080:8080 -e REDIS_HOST=<redis_host>  -e REDIS_PORT=<redis_port> cert_entity
```

For HTTPS, you need to copy the certificate files into the root directory first:
```bash
# copy server certificate files, use the below filenames
cp <ABSOLUTE PATH> ssl_cert.pem
cp <ABSOLUTE PATH> ssl_cert_key.pem

# building the image
docker build -t cert_entity .

# starting up a container
docker run -d --name cert_entity \
    -p 8443:8443 \
    -p 8080:8080 \
    -e REDIS_HOST=<redis_host>  -e REDIS_PORT=<redis_port> \
    cert_entity \
    --processes 4 \
    --https-only \
    --ssl-certificate-file ssl_cert.pem \
    --ssl-certificate-key-file ssl_cert_key.pem \
    --server-name <HOST>
```

## Running with Docker Compose

From the root folder, simply execute:

```bash
docker compose up -d # or docker-compose up -d
```


## Example call

Create certificate
```commandline
curl -i -X POST https://<HOST>:<PORT>/certificate --basic -u 'testuser:arXKcZKv610q9geHqOoZZzEW' \
  -H 'Content-Type:application/json' \
  -d '{"test_id": 18, "access_token": "qmegiqsyvynzqkvm", "app_name": "YoGoKo-CITS-NetApp", 
       "app_version": "1.0", "app_author": "YoGoKo", "service_order": "https://nods_link"}'
```
If the certificate was successfully created, the call returns an URL. Call the URL in a browser to download the
certificate.
