"""
Controller generated to handle auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""
from typing import List

from swagger_server import constants as c


def check_basicAuth(username, password, required_scopes):
    if c.users.get(username) == password:
        return {'sub': username}
    return
