#!/usr/bin/env python3

import connexion

from swagger_server import encoder

app = connexion.App(__name__, specification_dir='./swagger/')
app.json_provider_class = encoder.JSONEncoder
app.add_api('swagger.yaml', arguments={'title': 'Certification Entity API'}, pythonic_params=True)


def main():
    app.run(port=8081)


if __name__ == '__main__':
    main()
