# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class CreateCert(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, test_id: int=None, access_token: str=None, app_name: str=None, app_version: str=None,
                 app_author: str=None, service_order: str=None):  # noqa: E501
        """CreateCert - a model defined in Swagger

        :param test_id: The test_id of this CreateCert.  # noqa: E501
        :type test_id: int
        :param access_token: The access_token of this CreateCert.  # noqa: E501
        :type access_token: str
        :param app_name: The app_name of this CreateCert.  # noqa: E501
        :type app_name: str
        :param app_version: The app_version of this CreateCert.  # noqa: E501
        :type app_version: str
        :param app_author: The app_author of this CreateCert.  # noqa: E501
        :type app_author: str
        :param service_order: The service_order of this CreateCert.  # noqa: E501
        :type service_order: str
        """
        self.swagger_types = {
            'test_id': int,
            'access_token': str,
            'app_name': str,
            'app_version': str,
            'app_author': str,
            'service_order': str
        }

        self.attribute_map = {
            'test_id': 'test_id',
            'access_token': 'access_token',
            'app_name': 'app_name',
            'app_version': 'app_version',
            'app_author': 'app_author',
            'service_order': 'service_order'
        }
        self._test_id = test_id
        self._access_token = access_token
        self._app_name = app_name
        self._app_version = app_version
        self._app_author = app_author
        self._service_order = service_order

    @classmethod
    def from_dict(cls, dikt) -> 'CreateCert':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CreateCert of this CreateCert.  # noqa: E501
        :rtype: CreateCert
        """
        return util.deserialize_model(dikt, cls)

    @property
    def test_id(self) -> int:
        """Gets the test_id of this CreateCert.

        test_id from CI/CD Manager to query test details and results  # noqa: E501

        :return: The test_id of this CreateCert.
        :rtype: int
        """
        return self._test_id

    @test_id.setter
    def test_id(self, test_id: int):
        """Sets the test_id of this CreateCert.

        test_id from CI/CD Manager to query test details and results  # noqa: E501

        :param test_id: The test_id of this CreateCert.
        :type test_id: int
        """
        if test_id is None:
            raise ValueError("Invalid value for `test_id`, must not be `None`")  # noqa: E501

        self._test_id = test_id

    @property
    def access_token(self) -> str:
        """Gets the access_token of this CreateCert.

        access_token from CI/CD Manager for test_id  # noqa: E501

        :return: The access_token of this CreateCert.
        :rtype: str
        """
        return self._access_token

    @access_token.setter
    def access_token(self, access_token: str):
        """Sets the access_token of this CreateCert.

        access_token from CI/CD Manager for test_id  # noqa: E501

        :param access_token: The access_token of this CreateCert.
        :type access_token: str
        """
        if access_token is None:
            raise ValueError("Invalid value for `access_token`, must not be `None`")  # noqa: E501

        self._access_token = access_token

    @property
    def app_name(self) -> str:
        """Gets the app_name of this CreateCert.

        Name of the Network App  # noqa: E501

        :return: The app_name of this CreateCert.
        :rtype: str
        """
        return self._app_name

    @app_name.setter
    def app_name(self, app_name: str):
        """Sets the app_name of this CreateCert.

        Name of the Network App  # noqa: E501

        :param app_name: The app_name of this CreateCert.
        :type app_name: str
        """
        if app_name is None:
            raise ValueError("Invalid value for `app_name`, must not be `None`")  # noqa: E501

        self._app_name = app_name

    @property
    def app_version(self) -> str:
        """Gets the app_version of this CreateCert.

        Version of the Network App  # noqa: E501

        :return: The app_version of this CreateCert.
        :rtype: str
        """
        return self._app_version

    @app_version.setter
    def app_version(self, app_version: str):
        """Sets the app_version of this CreateCert.

        Version of the Network App  # noqa: E501

        :param app_version: The app_version of this CreateCert.
        :type app_version: str
        """
        if app_version is None:
            raise ValueError("Invalid value for `app_version`, must not be `None`")  # noqa: E501

        self._app_version = app_version

    @property
    def app_author(self) -> str:
        """Gets the app_author of this CreateCert.

        Author or who registered the Network App  # noqa: E501

        :return: The app_author of this CreateCert.
        :rtype: str
        """
        return self._app_author

    @app_author.setter
    def app_author(self, app_author: str):
        """Sets the app_author of this CreateCert.

        Author or who registered the Network App  # noqa: E501

        :param app_author: The app_author of this CreateCert.
        :type app_author: str
        """
        if app_author is None:
            raise ValueError("Invalid value for `app_author`, must not be `None`")  # noqa: E501

        self._app_author = app_author

    @property
    def service_order(self) -> str:
        """Gets the service_order of this CreateCert.

        Link to the service order of the Network App on NODS  # noqa: E501

        :return: The service_order of this CreateCert.
        :rtype: str
        """
        return self._service_order

    @service_order.setter
    def service_order(self, service_order: str):
        """Sets the service_order of this CreateCert.

        Link to the service order of the Network App on NODS  # noqa: E501

        :param service_order: The service_order of this CreateCert.
        :type service_order: str
        """
        if service_order is None:
            raise ValueError("Invalid value for `service_order`, must not be `None`")  # noqa: E501

        self._service_order = service_order
