# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.cert_created import CertCreated  # noqa: E501
from swagger_server.models.create_cert import CreateCert  # noqa: E501
from swagger_server.models.server_info import ServerInfo  # noqa: E501
from swagger_server.models.test_case_list import TestCaseList  # noqa: E501
from swagger_server.test import BaseTestCase


class TestCertificationController(BaseTestCase):
    """CertificationController integration test stubs"""

    def test_create_cert(self):
        """Test case for create_cert

        Create a certificate for a testing (identified by the test_id)
        """
        body = CreateCert()
        response = self.client.open(
            '/certificate',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_cert(self):
        """Test case for get_cert

        Get the certificate for a testing (identified by the test_id)
        """
        query_string = [('test_id', 56),
                        ('access_token', 'access_token_example')]
        response = self.client.open(
            '/certificate',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_server_info(self):
        """Test case for get_server_info

        Get server info
        """
        response = self.client.open(
            '/',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_test_cases(self):
        """Test case for get_test_cases

        Get the list of mandatory and conditional mandatory test cases for a specified set of test conditions. If no conditions are specified, the list contains only mandatory test cases.
        """
        query_string = [('test_bed', 'test_bed_example'),
                        ('test_conditions', 'test_conditions_example')]
        response = self.client.open(
            '/test_cases',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
