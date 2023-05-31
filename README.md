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

#### HTTPS
Provide the hostname and server certificate files in the command, then run it from the root directory
(`--processes` could be twice the number of CPUs):
```commandline
mod_wsgi-express start-server wsgi.py --processes 4 --port 8080 \
    --https-only --https-port=8443 --server-name=<HOSTNAME> \
    --ssl-certificate-file='<ABSOLUTE PATH>' \
    --ssl-certificate-key-file='<ABSOLUTE PATH>'
```

#### HTTP
In the root directory, run (`--processes` could be twice the number of CPUs):
```commandline
mod_wsgi-express start-server wsgi.py --processes 4 --port 8080
```

## Running with Docker

To run the server on a Docker container, execute the following from the root directory:

For HTTP:
```commandline
# building the image
docker build -t cert_entity .

# starting up a container for HTTP
docker run -d --name cert_entity -p 8080:8080 cert_entity
```

For HTTPS, you need to copy the certificate files into the root directory first:
```commandline
# copy server certificate files, use the below filenames
cp <ABSOLUTE PATH> ssl_cert.pem
cp <ABSOLUTE PATH> ssl_cert_key.pem

# building the image
docker build -t cert_entity .

# starting up a container
docker run -d --name cert_entity \
    -p 8443:8443 \
    -p 8080:8080 \
    cert_entity \
    --processes 4 \
    --https-only \
    --ssl-certificate-file ssl_cert.pem \
    --ssl-certificate-key-file ssl_cert_key.pem \
    --server-name <HOST>
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
