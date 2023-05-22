# 5GASP Certification Entity

## Overview
The 5GASP Certification Entity calculates the certificate grade and creates a certificate for a testing.  
The two main functions are creating a certificate and offering download of the certificate PDF file. Only pre-defined
users can create certificates, while anyone with a download URL can download the certificate. 

This server uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask.  
mod_wsgi is used as WSGI server for the Flask app.

## Requirements
Python 3.8+  
Pango 1.44+  
Apache2 2.4+

Install the requirements with: (For Apache2, a compiler and development headers are required.)
```commandline
apt install pango1.0-tools apache2 apache2-dev gcc build-essentials
```

Create a virtual environment and install the dependencies:  
In the root directory, run:
```commandline
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Usage

### Adding users

The endpoint to create certificates is protected by basic authentication. To add users, add an entry to the dictionary
`users` in the file `constants.py`.  
If the server is running, restart it to apply the change.

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

### Example call

Create certificate
```commandline
curl -i -X POST https://<HOST>:<PORT>/certificate --basic -u 'testuser:arXKcZKv610q9geHqOoZZzEW' \
  -H 'Content-Type:application/json' \
  -d '{"test_id": 18, "access_token": "qmegiqsyvynzqkvm", "app_name": "YoGoKo-CITS-NetApp", 
       "app_version": "1.0", "app_author": "YoGoKo"}'
```
If the certificate was successfully created, the call returns an URL. Call the URL in a browser to download the
certificate.
